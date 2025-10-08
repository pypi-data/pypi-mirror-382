import zmq
import json
import base64
import zlib
import logging
from .response import Response
from .factor import Factor
from .analysis import Analysis
from .optimizer import Optimizer
from .node import Node
from .transform import Transform
from .information import BuildInfo
from .evaluation import Evaluation
from .fds import FDS

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

class HTTPException(IOError):

    def __init__(self, *args, **kwargs):
        self.status = kwargs.pop('status', 500)
        super().__init__(*args, **kwargs)

class SEClient:

    request_timeout = 4000
    REQUEST_RETRIES = 3
    SERVER_ENDPOINT = "tcp://localhost:4900"

    def __init__(self):
        self.connect()

    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.SERVER_ENDPOINT)

    def set_timeout(self, new_value):
        self.request_timeout = int(new_value)

    def close(self):
        self.socket.close()
        self.context.term()

    def status_ok(self, reply):
        return reply.get('status', 500) < 400

    def decode_payload(self, payload):
        payload_bytes = base64.b64decode(payload)
        return json.loads(zlib.decompress(payload_bytes).decode('utf-8'))

    def send_payload(self, payload):
        self.socket.send_json(payload)
        retries_left = self.REQUEST_RETRIES
        while True:
            syn_recvd = False
            if (self.socket.poll(self.request_timeout) & zmq.POLLIN) != 0:
                reply = self.socket.recv_json()
                if reply.get('status', 'NA') == 'SYN':
                    self.socket.send_json({
                        'status': 'ACK',
                        'count': reply.get('count', 'NA'),
                    })
                    retries_left = self.REQUEST_RETRIES
                    syn_recvd = True
                else:
                    if self.status_ok(reply):
                        if reply.get('payload', None):
                            reply['payload'] = self.decode_payload(reply['payload'])
                        retries_left = self.REQUEST_RETRIES
                        break
                    else:
                        if reply.get('payload', None):
                            error_msg = self.decode_payload(reply['payload'])
                            raise HTTPException("Received error from Stat-Ease 360: {}".format(error_msg), status=reply.get('status', 500))
                        raise HTTPException("Received invalid response from Stat-Ease 360: {}".format(reply), status=reply.get('status', 500))

            if not syn_recvd:
                retries_left -= 1
                # socket is confused, close and remove
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.close()
                if retries_left == 0:
                    raise HTTPException("No response from Stat-Ease 360 after {} attempts.".format(self.REQUEST_RETRIES), status=500)
                logging.warning("No response from Stat-Ease 360, retrying...")

                # reconnect and re-send
                self.connect()
                self.socket.send_json(payload)

        return reply

    def prompt(self, message):
        self.send_payload({
            "method": "POST",
            "uri": "prompt",
            "message": message,
        })

    def set_preference(self, key, value, area = ""):
        """Sets a preference.

        :param str key: The preference key. This can be found in the Stat-Ease 360 preference dialog.
        :param str value: The value to assign to the preference.
        """
        self.send_payload({
            "method": "POST",
            "uri": "preference",
            "key": key,
            "value": value,
            "area": area,
        })

    def get_preference(self, key):
        """Retrieves the current value of a preference.

        :param str key: The preference key. This can be found in the Stat-Ease 360 preference dialog.
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "preference",
            "key": key,
        })
        return result['payload']['preference']

    def go_to_node(self, node : Node, analysis_name = ''):
        self.send_payload({
            "method": "POST",
            "uri": "nodes",
            "node": str(node),
            "analysis": analysis_name,
        })

    def open_design(self, path = ""):
        self.send_payload({
            "method": "POST",
            "uri": "open",
            "path": path,
        })

    def import_data(self, data, build_info):
        """Imports a matrix of data as a new design."""
        self.send_payload({
            "method": "POST",
            "uri": "build/import",
            "data": data,
            "build_info": build_info.to_dict()
        })

    def import_design(self, data, build_info):
        """Alias for import_data."""
        self.import_data(data, build_info)

    def save_design(self, path = ""):
        self.send_payload({
            "method": "POST",
            "uri": "save",
            "path": path,
        })

    def has_open_design(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "has_open_design",
        })
        is_open = result['payload']['has_open_design']
        if is_open == "False":
            return False
        return True

    def get_build_info(self):
        return BuildInfo(self)

    def get_evaluation(self, model = "", varianceRatio = 1.0):
        return Evaluation(self, model, varianceRatio)

    def get_fds(self, model = "", bins = 10, samples = 1000000):
        return FDS(self, model, bins, samples)

    def list_analyses(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "analysis",
        })

        return result['payload']['analyses']

    def get_analysis(self, name):
        if not self.has_open_design():
            raise HTTPException("Received error from Stat-Ease 360: {}".format("There is no design loaded."), status=404)

        analyses = self.list_analyses()
        if not name in analyses:
            raise HTTPException("Received error from Stat-Ease 360: {}".format(f"There is no analysis named '{name}' in open design."), status=404)

        return Analysis(self, name)

    def get_optimizer(self):
        return Optimizer(self)

    def create_analysis(self, response_name, analysis_name, transform=Transform.No_Transform, **kwargs):
        """Creates an analysis for a response.

        :param str response_name: The name of the response to analyze.
        :param str analysis_name: The desired name for this analysis.
        :param str transform: The transform to apply to the response for this analysis. The default is "No Transform".
        """
        payload = {
            "method": "POST",
            "uri": "analysis/create",
            "response_name": response_name,
            "analysis_name": analysis_name,
            "transform": str(transform),
        }

        if kwargs.get("Constant") or kwargs.get("constant"):
            if kwargs.get("Constant"):
                constant = kwargs.get("Constant")
            if kwargs.get("constant"):
                constant = kwargs.get("constant")
            payload["constant"] = str(constant)

        if kwargs.get("Lambda") or kwargs.get("lambda"):
            if kwargs.get("Lambda"):
                l = kwargs.get("Lambda")
            if kwargs.get("lambda"):
                l = kwargs.get("lambda")
            payload["lambda"] = str(l)

        if kwargs.get("Lower Bound") or kwargs.get("lower bound") or kwargs.get("lower_bound"):
            if kwargs.get("Lower Bound"):
                lower_bound  = kwargs.get("Lower Bound")
            if kwargs.get("lower bound"):
                lower_bound  = kwargs.get("lower bound")
            if kwargs.get("lower_bound"):
                lower_bound  = kwargs.get("lower_bound")
            payload["lower_bound"] = str(lower_bound)

        if kwargs.get("Upper Bound") or kwargs.get("upper bound") or kwargs.get("upper_bound"):
            if kwargs.get("Upper Bound"):
                upper_bound  = kwargs.get("Upper Bound")
            if kwargs.get("upper bound"):
                upper_bound  = kwargs.get("upper bound")
            if kwargs.get("upper_bound"):
                upper_bound  = kwargs.get("upper_bound")
            payload["upper_bound"] = str(upper_bound)

        self.send_payload(payload)
        return Analysis(self, analysis_name)

    def delete_analysis(self, analysis_name):
        """Deletes an analysis.

        :param str analysis_name: The name of the analysis to delete.
        """
        self.send_payload({
            "method": "DELETE",
            "uri": "analysis/delete",
            "analysis_name": analysis_name
        })

    def create_response(self, response_name, response_units="", response_format="General"):
        """Creates a response.
        :param str response_name: The desired name of the response.
        :param str response_units: The response units.
        :param str response_format: The format of the response values in the user interface. The default is "General".
        """

        reply = self.send_payload({
            "method": "POST",
            "uri": "design/response/create",
            "response_name": response_name,
            "response_units": response_units,
            "response_format": response_format
        })

        return Response(self, response_name)

    def list_responses(self):
        """Returns a list of all response names in the current design.

        Use :func:`get_response` to retrieve response settings and row data.

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.list_responses()
            ["R1", "R2"]
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "design/response",
        })

        return result['payload']['responses']

    def get_response(self, name):
        """Retrieves a response from the current design.

        :param str name: The name of the response. Case insensitive.
        :rtype: statease.response.Response

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.get_response("CFU")
            name: “CFU”
            units: “per cm^2”
            length: 20
        """
        return Response(self, name)

    def get_responses(self):
        '''Retrieve all response objects in the current design.
          :rtype: Python list of statease.response.Response objects

          :Example:
              >>> import statease as se
              >>> se_conn = se.connect()
              >>> responses = se_conn.get_responses()
        '''
        names = self.list_responses()
        responses = []
        for name in names:
            responses.append(self.get_response(name))
        return responses

    def delete_response(self, response_name):
        """Deletes a response.

        :param str response_name: The name of the response to delete.
        """
        self.send_payload({
            "method": "DELETE",
            "uri": "design/response/delete",
            "response_name": response_name
        })

    def create_factor(self, factor_name, factor_levels = [-1,1], factor_type = "numeric", categoric_type="nominal"):
        """Creates a factor.

        :param str factor_name: The name of the factor.
        :param list factor_levels: The actual levels of the factor. For continuous factors this should simply be [low, high].
                For categoric or discrete factors this should be a list of all valid factor levels. The default is [-1, 1].
        :param str factor_type: The type of the factor. The default is "numeric".
        :param str categoric_type: If the factor type is "categoric", this will set type of categoric factor (e.g. nominal or ordinal). The default is "nominal".
        """

        reply = self.send_payload({
            "method": "POST",
            "uri": "design/factor/create",
            "factor_name": factor_name,
            "factor_levels": factor_levels,
            "factor_type": factor_type,
            "categoric_type": categoric_type
        })

        return Factor(self, factor_name)

    def list_factors(self):
        """Returns a list of all factor names in the current design.

        Use :func:`get_factor` to retrieve factor settings and row data.

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.list_factors()
            ["A", "B", "C"]
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "design/factor",
        })

        return result['payload']['factors']

    def get_factor(self, name):
        """Retrieves a factor from the current design.

        :param str name: The name of the factor. Case insensitive.
        :rtype: statease.factor.Factor

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.get_factor("n-propanol")
            name: “N-Propanol”
            units: “wt %”
            length: 20
        """
        return Factor(self, name)

    def get_block(self):
        """Retrieves the block from the current design.

        :rtype: statease.factor.Factor

        :Example:
            >>> import statease as se
            >>> se_conn = se.connect()
            >>> se_conn.get_block()
            name: “Block”
            length: 20
        """
        return Factor(self, is_block=True)

    def get_factors(self):
        '''Retrieve all Factor objects in the current design.
          :rtype: Python list of statease.factor.Factor objects

          :Example:
              >>> import statease as se
              >>> se_conn = se.connect()
              >>> factors = se_conn.get_factors()
        '''
        names = self.list_factors()
        factors = []
        for name in names:
            factors.append(self.get_factor(name))
        return factors

    def delete_factor(self, factor_name):
        """Deletes a factor.

        :param str factor_name: The name of the factor to delete.
        """
        self.send_payload({
            "method": "DELETE",
            "uri": "design/factor/delete",
            "factor_name": factor_name
        })

    def get_design_model(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/model",
        })

        return result['payload']['model']

    def get_groups(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/groups",
        })

        return result['payload']['groups']

    def get_subgroups(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/subgroups",
        })

        # N.B. DX returns the subgroups as "groups" in the payload. Do not change!
        return result['payload']['groups']

    def get_design_ids(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/design-id",
        })

        return result['payload']['design_id']

    def get_space_point_types(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/space-type",
        })

        return result['payload']['space_type']

    def get_build_point_types(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/build-type",
        })

        return result['payload']['build_type']

    def get_comments(self):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/comments",
        })

        return result['payload']['comments']

    def set_comment(self, row, comment):
        """Sets the comment on a row.

        :Example:
            >>> se_conn.set_row_comment(1, 'Bad batch')
        """
        self.send_payload({
            "method": "POST",
            "uri": "design/row/{}/comment".format(row),
            "comment": comment,
        })

    def get_row_status(self, rows=None):
        result = self.send_payload({
            "method": "GET",
            "uri": "design/row-status",
            "rows": rows,
        })

        return result['payload']['row_status']

    def set_row_status(self, rows, status):
        """Sets the status of one or more rows.

        :Example:
            >>> # ignores rows 2/4/6/8
            >>> se_conn.set_row_status([ 1, 3, 5, 7], RowStatus.IGNORED)
        """
        self.send_payload({
            "method": "POST",
            "uri": "design/row-status",
            "rows": rows,
            "status": str(status),
        })

    def get_standard_order(self):
        """Gets the 'Standard Order' for each row in the design. Sorting the
        factors by this order will reproduce the 'Standard Order' for textbook
        designs, e.g. 2^k factorial designs.

        :Example:
            >>> std_order = se_conn.get_standard_order()
            >>> sorted_factor_values = [ factor.values[i] for i in std_order ]
        """
        result = self.send_payload({
            "method": "GET",
            "uri": "design/std-order",
        })

        return result['payload']['standard_order']

    def build_design(self, build_info):
        """Builds a new design given a BuildInfo object, which contains the
        parameters for building the design (factors, responses, etc.).
        """

        reply = self.send_payload({
            "method": "POST",
            "uri": "build",
            "build_info": build_info.to_dict()
        })

        return reply

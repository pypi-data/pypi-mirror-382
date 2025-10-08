import json
from urllib.parse import quote as url_parse


class Response:
    """The Response class holds information about an individual Response in
    Stat-Ease 360. Instances of this class are typically created by
    :func:`statease.client.SEClient.get_response`.

    :ivar str name: the name of the response
    :ivar str units: the units of the response
    :ivar list values: the values of the response, in run order
    """

    def __init__(self, client = None, name = "", **kwargs):
        self.__name = name
        self.__client = client

        if self.__client:
            self.get()
        else:
            self.from_dict(kwargs)

    def __str__(self):
        return 'name: "{}"\nunits: "{}"\nlength: {}\nis_equation_only: {}'.format(self.__name, self.__units, len(self.__values),self.__is_equation_only)

    def get(self):
        result = self.__client.send_payload({
            "method": "GET",
            "uri": "design/response/" + url_parse(self.__name, safe='')
        })

        self.from_dict(result['payload'])

    def post(self, endpoint, payload):
        return self.__client.send_payload({
            "method": "POST",
            "uri": "design/response/{}/{}".format(url_parse(self.__name, safe=''), endpoint),
            **payload,
        })

    def from_dict(self, data):
        self.__name = data.get('name', self.__name)
        self.__units = data.get('units', '')
        self.__values = tuple(data.get('values', []))
        self.__is_equation_only = data.get('is_equation_only',False)

    def to_dict(self):
        data = {}
        data["name"] = self.__name
        data["units"] = self.__units
        data["column_type"] = 'response'
        return data;

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        result = self.post("name", {"name": name })
        if result['status'] == 200:
            self.__name = name

    @property
    def units(self):
        return self.__units

    @units.setter
    def units(self, units):
        result = self.post("units", {"units": units })
        if result['status'] == 200:
            self.__units = units

    @property
    def values(self):
        """Get or set the response values. When setting the response values, you may use
        either a list or a dictionary. If fewer values are assigned than there are rows
        in the design, they will be filled in starting with first row. If a dictionary
        is used, it must use integers as keys, and it will fill response values in rows
        indexed by the dictionary keys. The indices are 0-based, so the first row is
        index 0, the second index 1, and so on.

        :Example:
            >>> # sets the first 4 rows to a list of values
            >>> response.values = [.1, .2, .3, .4]
            >>> # sets the 7th through 10th rows to specific values
            >>> response.values = { 6: .1, 7: .2, 8: .3, 9: .4 }
            >>> # sets the 6th run to a specific value
            >>> response.values = { 5: .8 }
        """
        return self.__values

    @property
    def is_equation_only(self):
        return self.__is_equation_only

    @values.setter
    def values(self, response_values):
        result = self.post("set", {"response_values": response_values })
        self.__values = tuple(result['payload']['values'])

    def simulate(self, equation, std_dev=1, variance_ratio=1, is_simulation=True):
        """Simulates data for a response.

        :param str equation: An equation that is recognized by the Stat-Ease
                             360 simulator. Search the help for
                             "Equation Entry" for more information on the
                             equation format.
        :param float std_dev: This adds some normal error to each simulated
                              value.
        :param float variance_ratio: If there are groups in the design,
                                     inter-group variability will be simulated
                                     using a combination of this parameter
                                     and the std_dev parameter.
        :param bool is_simulation: If False, sets the std_dev parameter to 0 and sets the
                                   response analysis to "equation only". Use this to
                                   create a function that does not require regression
                                   analysis, but will available in numerical optimization.
                                   Note: The default is true, but this parameter takes
                                   precedence over the std_dev parameter when False.
        :Example:
            >>> response.simulate('a+b+sin(a)', std_dev=2) # A simulation with noise
            >>> response.simulate('exp(1+a-2*b)', is_simulation=False) # Noiseless equation
        """
        if (not is_simulation): # "equation only"
            std_dev = 0

        response = self.post("simulate", {
            "equation": equation,
            "std_dev": std_dev,
            "variance_ratio": variance_ratio,
            "is_simulation": is_simulation,
        })

        # older versions didn't return the updated values
        if 'payload' in response and 'values' in response['payload']:
            self.values = response['payload']['values']

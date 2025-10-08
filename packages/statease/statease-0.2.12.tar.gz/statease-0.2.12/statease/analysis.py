from collections import namedtuple
from urllib.parse import quote as url_parse
from enum import Enum
from .graph import Graph
from .transform import Transform

class ModelOrder(Enum):
    """Represents a full model order."""
    LinearSquared = -1
    Interaction = -2
    PartialQuadratic = -2
    SpecialCubic = -3
    SpecialQuartic = -4
    SpecialQuintic = -5
    
    Mean = 0
    
    Linear = 1
    Quadratic = 2
    Cubic = 3
    Quartic = 4
    Fifth = 5
    Sixth = 6
    
    MainEffects = 11
    ModelOrder_2FI = 12
    ModelOrder_3FI = 13
    ModelOrder_4FI = 14
    ModelOrder_5FI = 15
    ModelOrder_6FI = 16
    ModelOrder_7FI = 17
    ModelOrder_8FI = 18
    ModelOrder_9FI = 19
    
    KCV = 101
    
    
class Analysis:
    """The Analysis class holds information about an Analysis in
    Stat-Ease 360. Instances of this class are typically created by
    :func:`statease.client.SEClient.get_analysis`.
    """

    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def predict(self, points, coded=False, **kwargs):
        """ Makes predictions at one or more points."""

        payload = {
            "method": "POST",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/predict",
            "points": points,
            "coded": coded,
            "prediction_only": True,
        }
        result = self.client.send_payload(payload)

        if type(result['payload']) == list:
            predictions = []
            for p in result['payload']:
                predictions.append(p)
            return predictions

        return result['payload']

    def get_prediction(self, points, **kwargs):
        """ Retrieves a Prediction object for one or more points. """

        payload = {
            "method": "POST",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/predict",
            "points": points,
        }
        if kwargs.get("population", False):
            payload["population"] = kwargs["population"]
        if kwargs.get("alpha", False):
            payload["alpha"] = kwargs["alpha"]
        if kwargs.get("n", False):
            payload["n"] = kwargs["n"]
        if kwargs.get("interval_bound", False):
            payload["interval_bound"] = kwargs["interval_bound"]
        if kwargs.get("adjust_for_poe", None) != None:
            payload["adjust_for_poe"] = kwargs["adjust_for_poe"]
        if kwargs.get("second_order_poe", None) != None:
            payload["second_order_poe"] = kwargs["second_order_poe"]
        if kwargs.get("coded", None) != None:
            payload["coded"] = kwargs["coded"]

        if kwargs.get("prediction_only", None) != None:
            payload["prediction_only"] = kwargs["prediction_only"]
        else:
            payload["prediction_only"] = False

        result = self.client.send_payload(payload)

        if payload["prediction_only"] == True:
            return result['payload']

        if type(result['payload']) == list:
            predictions = []
            for p in result['payload']:
                pred = namedtuple('Prediction', iter(p.keys()))(**p)
                predictions.append(pred)
            return predictions
        return namedtuple('Prediction', iter(result['payload'].keys()))(**result['payload'])

    def set_model(self, model=None, **kwargs):
        """ Sets the model used in the analysis. """
        payload = {
            "method": "POST",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/model",
        }
        if 'center_point_status' in kwargs:
            payload["center_point_status"] = kwargs["center_point_status"]
        
        key = ''
        if model:
            key = 'model'
            value = model
        else:
            if kwargs.get('model'): # e.g. model='A,B,C'
                key = 'model'
            if kwargs.get('process_order'):
                key = 'process_order'
            if kwargs.get('mixture_order'):
                key = 'mixture_order'
            if kwargs.get('mixture1_order'):
                key = 'mixture1_order'
            if kwargs.get('mixture2_order'):
                key = 'mixture2_order'

            value = ''
            order = kwargs.get(key)
            if isinstance(order, str):    #e.g. model_order='linear'
                value = order
            elif isinstance(order, ModelOrder):   #e.g. model_order=ModelOrder.Linear
                value = str(order)
        
        payload[key] = value
            
        result = self.client.send_payload(payload)
        return result['payload']

    def get_transform(self):

        payload = {
            "method": "GET",
            "uri": "analysis/" + self.name + "/transform"
        }

        result = self.client.send_payload(payload)
        return result['payload']
        
    def set_transform(self, transform : Transform, **kwargs):

        payload = {
            "method": "POST",
            "uri": "analysis/" + self.name + "/transform",
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

        result = self.client.send_payload(payload)
        return result['payload']

    def get_preanalysis(self):

        payload = {
            "method": "GET",
            "uri": "analysis/" + self.name + "/preanalysis"
        }

        result = self.client.send_payload(payload)
        return result['payload']
        
    def auto_select(self, initial_model, criterion, method, alpha=None, select_by_degree=False, **kwargs):
        """ Performs an auto-selection on an initial model.

        :param str initial_model: A model to auto-select a subset of terms from.
        :param str criterion: The criterion used to evaluate each sub-model.
                              Valid options are "AICc", "BIC", "pValues",
                              or "AdjRSquared" (case-insensitive).
        :param str method: The method used to select sub-models. Valid options
                           are "Forward", "Backward", "Stepwise", and
                           "AllHierarchical" (case-insensitive).
        :param float alpha: This is the alpha used to either include or exclude
                            terms when using the "pValues" criterion. You can
                            also pass `alpha_in` and/or `alpha_out` to set
                            those values separately (setting both only has an
                            effect when using the "Stepwise" method).
        :param bool select_by_degree: Restricts the sub-model comparisons to
                                      lower order terms before considering
                                      higher order terms.

        :Example:
            >>> result_model = analysis.auto_select('A+B+C+AB+BC+ABC', 'BICc', 'Backward')
            >>> print(result_model)
            >>> "A+B+AB"
        """
        payload = {
            "method": "POST",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/autoselect",
            "model": initial_model,
            "criterion": criterion,
            "select_method": method,
            "select_by_degree": select_by_degree,
        }
        if kwargs.get("alpha_in", alpha):
            payload["alpha_in"] = kwargs.get("alpha_in", alpha)
        if kwargs.get("alpha_out", alpha):
            payload["alpha_out"] = kwargs.get("alpha_out", alpha)
        result = self.client.send_payload(payload)
        return result['payload']['selection_log']

    def go_to_node(self, node):
        """ Forces the Stat-Ease 360 GUI to display a particular node. """
        self.client.send_payload({
            "method": "POST",
            "uri": "nodes",
            "node": str(node),
            "analysis": self.name,
        })

    def analyze(self):
        """ Runs the analyses on the selected model. """
        return self.get_anova()

    def get_anova(self):
        """ Retrieves an AnovaResults object for this analysis. """
        return AnovaResults(self.client, self.name)

    def get_diagnostics(self):
        """ Retrieves an DiagnosticsResults object for this analysis. """
        return DiagnosticsResults(self.client, self.name)

    def plot_residuals(self, plot_type='normal', residual_type='external', graph_width = 1080, graph_height = 1080, full_file_path=''):
        if full_file_path == '':
            result = self.client.send_payload({
                "method": "GET",
                "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/residuals?plot_type={}&residual_type={}".format(plot_type, residual_type),
            })
            return Graph(result['payload'])
        else:
            payload = {
                "method": "POST",
                "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/residuals",
                "plot_type": plot_type,
                "residual_type": residual_type,
                "graph_width": graph_width,
                "graph_height": graph_height,
                "full_file_path": full_file_path
            }
            return self.client.send_payload(payload)

    def plot_predicted_vs_actual(self, graph_width = 1080, graph_height = 1080, full_file_path=''):
        if full_file_path == '':
            result = self.client.send_payload({
                "method": "GET",
                "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/pred_vs_actual",
            })
            return Graph(result['payload'])
        else:
            payload = {
                "method": "POST",
                "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/pred_vs_actual",
                "graph_width": graph_width,
                "graph_height": graph_height,
                "full_file_path": full_file_path
            }
            return self.client.send_payload(payload)
    
    def apply_box_cox_transform(self):
        payload = {
                "method": "POST",
                "uri": "analysis/" + url_parse(self.name, safe='') + "/box_cox_transform"
            }
        return self.client.send_payload(payload)
            
    def plot_box_cox(self):
        result = self.client.send_payload({
            "method": "GET",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/box_cox",
        })
        return Graph(result['payload'])

    def plot_box_cox(self):
        result = self.client.send_payload({
            "method": "GET",
            "uri": "analysis/" + url_parse(self.name, safe='') + "/graph/box_cox",
        })
        return Graph(result['payload'])

class AnovaResults:

    def __init__(self, client, analysis_name):
        self.client = client
        self.analysis_name = analysis_name

        result = self.client.send_payload({
            "method": "GET",
            "uri": "analysis/" + url_parse(self.analysis_name, safe='') + "/anova",
        })

        self.terms = []
        for k, v in result['payload'].items():
            if k == 'terms':
                for term_dict in v:
                    term = namedtuple('Term', iter(term_dict.keys()))(**term_dict)
                    self.terms.append(term)
            else:
                setattr(self, k, v)

    def __str__(self):
        return """{transform}
R2: {r2}
Adj R2: {adjr2}
Pred R2: {predr2}
PRESS: {press}
BIC: {bic}
AICc: {aicc}
Terms: {terms}""".format(
            transform=self.transform,
            r2=self.r2,
            adjr2=self.adj_r2,
            predr2=self.pred_r2,
            press=self.press,
            bic=self.bic,
            aicc=self.aicc,
            terms=self.terms,
        )

class DiagnosticsResults:

    def __init__(self, client, analysis_name):
        self.client = client
        self.analysis_name = analysis_name

        result = self.client.send_payload({
            "method": "GET",
            "uri": "analysis/" + url_parse(self.analysis_name, safe='') + "/diagnostics",
        })

        for k, v in result['payload'].items():
            setattr(self, k, v)

    def __str__(self):
        return """Actual: {actual}

Predicted: {predicted}

Residuals: {residuals}
""".format(
            actual=self.actual,
            predicted=self.predicted,
            residuals=self.residuals,
        )

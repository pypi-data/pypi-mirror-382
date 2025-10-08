from urllib.parse import urlencode
from .graph import Graph

def table_to_string(table):
  """Converts a dictionary with a data and column element into a Pandas-style table string"""

  widths = []
  if 'columns' in table.keys():
    for c in range(0, len(table['columns'])):
      widths.append(len(table['columns'][c].replace("\n", "\\n")))
  for row in table['data']:
    for c in range(0, len(row)):
      if isinstance(row[c], list) or isinstance(row[c], dict):
        widths[c] = max(widths[c], len(row[c]))
      else:
        widths.append(20)

  out = ""

  if 'columns' in table.keys():
      for c in range(0, len(table['columns'])):
        out += f"  {table['columns'][c]:>{widths[c]}}".replace("\n", "\\n")
      out += "\n"

  for row in table['data']:
    for c in range(0, len(row)):
      out += f"  {row[c]:>{widths[c]}}"
    out += "\n"

  return out

class Evaluation:

  def __init__(self, client, model = "", varianceRatio = 0.0):
    self.client = client

    if model == "":
        result = self.client.send_payload({
          "method": "GET",
          "uri": "information/evaluation",
        })
    else:
        params = {
            'model': model,
            'variance_ratio': str(varianceRatio)
        }
        result = self.client.send_payload({
          "method": "GET",
          "uri": 'information/evaluation/?{}'.format(urlencode(params)),
        })

    for k, v in result['payload'].items():
      setattr(self, k, v)

  def __str__(self):
    out = "Model Terms:\n"
    out += table_to_string(self.model_terms)

    out += "\nDegrees of Freedom:\n"
    out += table_to_string(self.df)

    out += "\nDegrees of Freedom:\n"
    out += table_to_string(self.matrix_measures)

    return out

  def plot_term(self, plot_type = 'perturbation', term = None, reference_point = None):

    params = { 'type': plot_type }
    if term is not None:
      params['term'] = term
    if reference_point is not None:
      params['reference_point'] = ','.join([str(i) for i in reference_point])
    payload = {
      "method": "GET",
      "uri": "information/evaluation/plot?{}".format(urlencode(params)),
    }
    result = self.client.send_payload(payload)
    return Graph(result['payload'])

  def get_x_matrix(self):
    payload = {
      "method": "GET",
      "uri": "information/evaluation/matrix/x",
    }
    result = self.client.send_payload(payload)
    return result['payload']

  def get_z_matrix(self):
    payload = {
      "method": "GET",
      "uri": "information/evaluation/matrix/z",
    }
    result = self.client.send_payload(payload)
    return result['payload']

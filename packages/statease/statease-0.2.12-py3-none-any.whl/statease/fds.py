from urllib.parse import urlencode

def list_to_string(title, olist):
  out = title + ':-' + '\n'
  for c in range(0, len(olist)):
    out += '\t' + str(olist[c]) + '\n'
  return out

class FDS:

  def __init__(self, client, model = '', bins = 10, samples = 1000000):
    self.client = client

    params = {
      'bins': bins,
      'samples': samples,
    }
    if model != '':
      params['model'] = model

    uri = 'information/fds?{}'.format(urlencode(params))
    result = self.client.send_payload({
      'method': 'GET',
      'uri': uri,
    })

    for k, v in result['payload']['FDS'].items():
      setattr(self, k, v)

  def __str__(self):

    out = '\nFDS Data:-' + '\n' + '#########' + '\n'
    attrs = vars(self)
    
    for item in attrs.items():
      if isinstance(item[1], list) or isinstance(item[1], dict):
        out += list_to_string(item[0], item[1])
      elif item[0] != 'client':
        out += item[0] + ': ' + str(item[1]) + '\n'

    return out

module.exports = {
  'versionContextError': {
    'msg': 'You must specify exactly one of -w (workspaceId), -v (versionId), or -m (microversionId).',
    'status': 1
  },
  'missingDocumentOrElementError': {
    'msg': 'You must specify a -d (documentId) and -e (elementId).',
    'status': 1
  },
  'credentialsFileError': {
    'msg': 'You must provide an API key file named config/apikey.js; please see config/apikeyexample.js for an example.',
    'status': 2
  },
  'credentialsFormatError': {
    'msg': 'Fields in config/apikey.js have an incorrect format.',
    'status': 2
  },
  'badBaseUrlError': {
    'msg': 'baseUrl field in config/apikey.js is invalid (must begin with http:// or https://).',
    'status': 2
  },
  'getError': {
    'msg': 'GET request failed.',
    'status': 3
  },
  'notOKError': {
    'msg': 'API call failed.',
    'status': 3
  }
}
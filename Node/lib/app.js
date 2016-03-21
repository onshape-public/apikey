var apikey = null;
try {
  apikey = require('../config/apikey.js');
} catch (e) {
  console.log('You must provide an API key file named config/apikey.js; please see config/apikeyexample.js for an example.');
  process.exit(2);
}

module.exports = function (documentId, wvm, wvmId, elementId) {
  console.log('Document ID: ' + documentId);
  if (wvm === 'w') {
    console.log('Workspace ID: ' + wvmId);
  } else if (wvm === 'v') {
    console.log('Version ID: ' + wvmId);
  } else if (wvm === 'm') {
    console.log('Microversion ID: ' + wvmId);
  }
  console.log('Element ID: ' + elementId);
};
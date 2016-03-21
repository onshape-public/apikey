var util = require('./util.js');
var errors = require('../config/errors.js');

var apikey = null;
try {
  apikey = require('../config/apikey.js');
} catch (e) {
  util.error(errors.credentialsFileError);
}

var onshape = require('./onshape.js')(apikey);

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
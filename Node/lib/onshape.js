var util = require('./util.js');
var errors = require('../config/errors.js');

module.exports = function (creds) {
  var protocol = null;
  // basic error checking on creds
  if (typeof creds.baseUrl !== 'string' || typeof creds.userId !== 'string' ||
    typeof creds.accessKey !== 'string' || typeof creds.secretKey !== 'string') {
    util.error(errors.credentialsFormatError);
  }
  if (creds.baseUrl.indexOf('http://') === 0) {
    protocol = require('http');
  } else if (creds.baseUrl.indexOf('https://') === 0) {
    protocol = require('https');
  } else {
    util.error(errors.badBaseUrlError);
  }

  var get = function (resource, query) {
    
  }

  return null;
};
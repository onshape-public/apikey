var util = require('./util.js');
var errors = require('../config/errors.js');
var crypto = require('crypto');
var url = require('url');
var querystring = require('querystring');

var apikey = null;
try {
  apikey = require('../config/apikey.js');
} catch (e) {
  util.error(errors.credentialsFileError);
}

// creates random 25-character string
var buildNonce = function () {
  var chars = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
    'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0',
    '1', '2', '3', '4', '5', '6', '7', '8', '9'
  ];
  var nonce = '';
  for (var i = 0; i < 25; i++) {
    nonce += chars[Math.ceil(Math.random()*chars.length)];
  }
  return nonce;
}

module.exports = (function (creds) {
  var protocol = null;
  // basic error checking on creds
  if (typeof creds.baseUrl !== 'string' ||
    typeof creds.accessKey !== 'string' ||
    typeof creds.secretKey !== 'string') {
    util.error(errors.credentialsFormatError);
  }
  if (creds.baseUrl.indexOf('http://') === 0) {
    protocol = require('http');
  } else if (creds.baseUrl.indexOf('https://') === 0) {
    protocol = require('https');
  } else {
    util.error(errors.badBaseUrlError);
  }

  // this function will modify the object passed in the headers parameter
  var buildHeaders = function (method, path, queryString, headers) {
    // the Date header needs to be reasonably (5 minutes) close to the server time when the request is received
    var authDate = (new Date()).toUTCString();
    // the On-Nonce header is a random (unique) string that serves to identify the request
    var onNonce = buildNonce();
    if (!('Content-Type' in headers)) {
      headers['Content-Type'] = 'application/json';
    }
    // the Authorization header needs to have this very particular format, which the server uses to validate the request
    // the access key is provided for the server to retrieve the API key; the signature is encrypted with the secret key
    var hmacString = (method + '\n' + onNonce + '\n' + authDate + '\n' +
      headers['Content-Type'] + '\n' + path + '\n' + queryString + '\n').toLowerCase();
    var hmac = crypto.createHmac('sha256', creds.secretKey);
    hmac.update(hmacString);
    var signature = hmac.digest('base64');
    var asign = 'On ' + creds.accessKey + ':HmacSHA256:' + signature;

    headers['On-Nonce'] = onNonce;
    headers['Date'] = authDate;
    headers['Authorization'] = asign;

    return headers;
  }

  var buildDWMVEPath = function (opts) {
    var path = '/api/' + opts.resource + '/d/' + opts.d;
    if ('w' in opts) {
      path += '/w/' + opts.w;
    } else if ('v' in opts) {
      path += '/v/' + opts.v;
    } else if ('m' in opts) {
      path += '/m/' + opts.m;
    }
    path += '/e/' + opts.e;
    if ('subresource' in opts) {
      path += '/' + opts.subresource;
    }

    return path;
  }

  var buildQueryString = function (opts) {
    if (!('query' in opts) || typeof opts.query !== 'object') {
      return '';
    }
    return querystring.stringify(opts.query);
  }

  /*
   * opts: {
   *   d: document ID
   *   w: workspace ID (only one of w, v, m)
   *   v: version ID (only one of w, v, m)
   *   m: microversion ID (only one of w, v, m)
   *   e: elementId
   *   resource: top-level resource (partstudios)
   *   subresource: sub-resource, if any (massproperties)
   *   path: from /api/...; if present, overrides the other options
   *   query: query object
   * }
   */
  var get = function (opts, cb) {
    var path = '';
    if ('path' in opts) {
      path = opts.path;
    } else {
      path = buildDWMVEPath(opts);
    }
    var queryString = buildQueryString(opts);
    var headers = buildHeaders('GET', path, queryString, {});
    if (queryString !== '') queryString = '?' + queryString;
    var requestOpts = url.parse(creds.baseUrl + path + queryString);
    requestOpts.method = 'GET';
    requestOpts.headers = headers;
    var req = protocol.request(requestOpts, function (res) {
      res.on('data', function (data) {
        if (res.statusCode === 200) {
          cb(data);
        } else {
          console.log(data.toString());
          util.error(errors.notOKError);
        }
      });
    }).on('error', function (e) {
      util.error(errors.getError);
    });
    req.end();
  }

  return {
    get: get
  };
})(apikey);
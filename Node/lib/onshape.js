var util = require('./util.js');
var errors = require('../config/errors.js');
var crypto = require('crypto');
var url = require('url');
var querystring = require('querystring');
var fs = require('fs');
var pathModule = require('path');

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
    nonce += chars[Math.floor(Math.random()*chars.length)];
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

  var buildHeaders = function (method, path, queryString, inputHeaders) {
    var headers = util.copyObject(inputHeaders);
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

    if (!('Accept' in headers)) {
      headers['Accept'] = 'application/vnd.onshape.v1+json';
    }

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
    if ('e' in opts) {
      path += '/e/' + opts.e;
    }
    if ('subresource' in opts) {
      path += '/' + opts.subresource;
    }

    return path;
  }

  var buildQueryString = function (opts) {
    if (!('query' in opts) || typeof opts.query !== 'object' || opts.query == null) {
      return '';
    }
    return querystring.stringify(opts.query);
  }

  var inputHeadersFromOpts = function (opts) {
    return (!('headers' in opts) || typeof opts.headers !== 'object' || opts.headers == null) ?
      {} : util.copyObject(opts.headers);
  }

  /*
   * opts: {
   *   d: document ID
   *   w: workspace ID (only one of w, v, m)
   *   v: version ID (only one of w, v, m)
   *   m: microversion ID (only one of w, v, m)
   *   e: elementId
   *   baseUrl: base URL; if present, overrides apikey.js
   *   resource: top-level resource (partstudios)
   *   subresource: sub-resource, if any (massproperties)
   *   path: from /api/...; if present, overrides the other options
   *   accept: accept header (default: application/vnd.onshape.v1+json)
   *   query: query object
   *   headers: headers object
   * }
   */
  var get = function (opts, cb) {
    var path = '';
    if ('path' in opts) {
      path = opts.path;
    } else {
      path = buildDWMVEPath(opts);
    }
    var baseUrl = ('baseUrl' in opts) ? opts.baseUrl : creds.baseUrl;
    var queryString = buildQueryString(opts);
    var inputHeaders = inputHeadersFromOpts(opts);
    var headers = buildHeaders('GET', path, queryString, inputHeaders);
    if (queryString !== '') queryString = '?' + queryString;
    var requestOpts = url.parse(baseUrl + path + queryString);
    requestOpts.method = 'GET';
    requestOpts.headers = headers;
    var req = protocol.request(requestOpts, function (res) {
      var wholeData = '';
      res.on('data', function (data) {
        wholeData += data;
      });
      res.on('end', function () {
        if (res.statusCode === 200) {
          cb(wholeData);
        } else if (res.statusCode === 307) {
          var redirectParsedUrl = url.parse(res.headers.location);
          console.log('Redirecting to ' + res.headers.location);
          // the redirect contains a query string, which the API key mechanism needs to encrypt
          var redirectOpts = {
            baseUrl: redirectParsedUrl.protocol + '//' + redirectParsedUrl.host,
            path: redirectParsedUrl.pathname,
            headers: inputHeaders,
            query: querystring.parse(redirectParsedUrl.query)
          };
          get(redirectOpts, cb);
        } else {
          console.log(requestOpts.method + ' ' + baseUrl + path + queryString);
          console.log('Status: ' + res.statusCode);
          if (wholeData) {
            console.log(wholeData.toString());
          }
          util.error(errors.notOKError);
        }
      });
    }).on('error', function (e) {
      console.log(requestOpts.method + ' ' + baseUrl + path + queryString);
      console.log(e);
      util.error(errors.getError);
    });
    req.end();
  };

  /*
   * opts: {
   *   d: document ID
   *   w: workspace ID (only one of w, v, m)
   *   v: version ID (only one of w, v, m)
   *   m: microversion ID (only one of w, v, m)
   *   e: elementId
   *   baseUrl: base URL; if present, overrides apikey.js
   *   resource: top-level resource (partstudios)
   *   subresource: sub-resource, if any (massproperties)
   *   path: from /api/...; if present, overrides the other options
   *   accept: accept header (default: application/vnd.onshape.v1+json)
   *   body: POST body
   *   headers: headers object
   * }
   */
  var post = function (opts, cb) {
    var path = '';
    if ('path' in opts) {
      path = opts.path;
    } else {
      path = buildDWMVEPath(opts);
    }
    var baseUrl = ('baseUrl' in opts) ? opts.baseUrl : creds.baseUrl;
    var headers = buildHeaders('POST', path, '', inputHeadersFromOpts(opts));
    var requestOpts = url.parse(baseUrl + path);
    requestOpts.method = 'POST';
    requestOpts.headers = headers;
    var req = protocol.request(requestOpts, function (res) {
      var wholeData = '';
      res.on('data', function (data) {
        wholeData += data;
      });
      res.on('end', function () {
        if (res.statusCode === 200) {
          cb(wholeData);
        } else {
          console.log(requestOpts.method + ' ' + baseUrl + path);
          console.log(req.body);
          console.log('Status: ' + res.statusCode);
          if (wholeData) {
            console.log(wholeData.toString());
          }
          util.error(errors.notOKError);
        }
      });
    }).on('error', function (e) {
      console.log(requestOpts.method + ' ' + baseUrl + path);
      console.log(e);
      util.error(errors.postError);
    });
    if ('body' in opts) {
      req.write(JSON.stringify(opts.body));
    } else {
      req.write('{}');
    }
    req.end();
  };

  /*
   * opts: {
   *   d: document ID
   *   w: workspace ID
   *   e: elementId
   *   baseUrl: base URL; if present, overrides apikey.js
   *   resource: top-level resource (partstudios)
   *   subresource: sub-resource, if any (massproperties)
   *   path: from /api/...; if present, overrides the other options
   *   headers: headers object
   * }
   */
  var del = function (opts, cb) { // 'delete' is a reserved keyword, so it can't be a variable name
    var path = '';
    if ('path' in opts) {
      path = opts.path;
    } else {
      path = buildDWMVEPath(opts);
    }
    var baseUrl = ('baseUrl' in opts) ? opts.baseUrl : creds.baseUrl;
    var headers = buildHeaders('DELETE', path, '', inputHeadersFromOpts(opts));
    var requestOpts = url.parse(baseUrl + path);
    requestOpts.method = 'DELETE';
    requestOpts.headers = headers;
    var req = protocol.request(requestOpts, function (res) {
      var wholeData = '';
      res.on('data', function (data) {
        wholeData += data;
      });
      res.on('end', function () {
        if (res.statusCode === 200) {
          cb(wholeData);
        } else {
          console.log(requestOpts.method + ' ' + baseUrl + path);
          console.log('Status: ' + res.statusCode);
          if (wholeData) {
            console.log(wholeData.toString());
          }
          util.error(errors.notOKError);
        }
      });
    }).on('error', function (e) {
      console.log(requestOpts.method + ' ' + baseUrl + path);
      console.log(e);
      util.error(errors.deleteError);
    });
    req.end();
  };

  /*
   * opts: {
   *   d: document ID
   *   w: workspace ID (only one of w, v, m)
   *   v: version ID (only one of w, v, m)
   *   m: microversion ID (only one of w, v, m)
   *   e: elementId
   *   baseUrl: base URL; if present, overrides apikey.js
   *   resource: top-level resource (partstudios)
   *   subresource: sub-resource, if any (massproperties)
   *   path: from /api/...; if present, overrides the other options
   *   headers: headers object
   *   file: local path of file to upload
   *   mimeType: MIME type of file
   *   body: other form data; should be plain key/value pairs
   * }
   */
  var upload = function (opts, cb) {
    var path = '';
    if ('path' in opts) {
      path = opts.path;
    } else {
      path = buildDWMVEPath(opts);
    }
    var baseUrl = ('baseUrl' in opts) ? opts.baseUrl : creds.baseUrl;

    // set up headers
    var inputHeaders = inputHeadersFromOpts(opts);
    var boundaryKey = Math.random().toString(16); // random string for boundary
    inputHeaders['Content-Type'] = 'multipart/form-data; boundary="' + boundaryKey + '"';
    var headers = buildHeaders('POST', path, '', inputHeaders);
    var requestOpts = url.parse(baseUrl + path);
    requestOpts.method = 'POST';
    requestOpts.headers = headers;

    // set up request
    var req = protocol.request(requestOpts, function (res) {
      var wholeData = '';
      res.on('data', function (data) {
        wholeData += data;
      });
      res.on('end', function () {
        if (res.statusCode === 200) {
          cb(wholeData);
        } else {
          console.log(requestOpts.method + ' ' + baseUrl + path);
          console.log('Status: ' + res.statusCode);
          if (wholeData) {
            console.log(wholeData.toString());
          }
          util.error(errors.notOKError);
        }
      });
    }).on('error', function (e) {
      console.log(requestOpts.method + ' ' + baseUrl + path);
      console.log(e);
      util.error(errors.postError);
    });

    // set up file info
    if (!('body' in opts)) {
      opts.body = {};
    }
    var filename = pathModule.basename(opts.file);
    opts.body.encodedFilename = filename;
    opts.body.fileContentLength = fs.statSync(opts.file).size;

    // set up form data
    for (var key in opts.body) {
      req.write('--' + boundaryKey + '\r\nContent-Disposition: form-data; name="' + key + '"\r\n\r\n');
      req.write('' + opts.body[key]);
      req.write('\r\n');
    }

    // add file and end request
    req.write('--' + boundaryKey + '\r\nContent-Disposition: form-data; name="file"; filename="' + filename + '"\r\n');
    req.write('Content-Type: ' + opts.mimeType + '\r\n\r\n');
    var readStream = fs.createReadStream(opts.file);
    readStream.on('data', function (data) {
      req.write(data);
    });
    readStream.on('end', function () {
      req.write('\r\n--' + boundaryKey + '--');
      req.end();
    });
  };

  return {
    get: get,
    post: post,
    delete: del,
    upload: upload
  };
})(apikey);

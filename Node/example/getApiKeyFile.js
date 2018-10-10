var util = require('../lib/util');
var errors = require('../config/errors.js');
var apikey = null;
try {
    apikey = require('../config/apikey.js');
} catch (e) {
    util.error(errors.credentialsFileError);
}

module.exports = apikey;

var assert = require('assert');
var client = require('../lib/app');

describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when the value is not present', function() {
      assert.equal([1,2,3].indexOf(4), -1);
    });
  });
});
describe('API Key Testing Spec', function() {
  describe('Use the API to make some get calls', function() {
    it('should get the user\'s documents', function() {
        client(require('../config/apikey')).getDocuments({}, function (data) {
            data.should.be.ok()
        });
    });
  });
});


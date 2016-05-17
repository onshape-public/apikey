var error = function (err) {
  console.log(err.msg);
  process.exit(err.status);
}

var copyObject = function (object) {
	if (object === null || typeof object !== 'object') {
		return object;
	}
	var copy = {};
	var keys = Object.keys(object);
	for (var i = 0; i < keys.length; i++) {
		if (object.hasOwnProperty(keys[i])) {
			copy[keys[i]] = copyObject(object[keys[i]]);
		}
	}
	return copy;
}

module.exports = {
  'error': error,
  'copyObject': copyObject
};
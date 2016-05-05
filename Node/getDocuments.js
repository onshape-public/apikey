var util = require('./lib/util.js');
var errors = require('./config/errors.js');

var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will get documents available to the user with the specified query params.\n');
  console.log('\tUsage: node getDocuments.js [--query <query>] [--filter <filter>] [--owner <owner>] [--ownerType <ownerType>] [--sortColumn <sortColumn>] [--sortOrder <sortOrder>] [--offset <offset>] [--limit <limit>]');
  console.log('See API documentation for query parameters.');
  process.exit(0);
}

var queryParams = ['query', 'filter', 'owner', 'ownerType', 'sortColumn', 'sortOrder', 'offset', 'limit'];
var queryObject = {};
for (var i = 0; i < queryParams.length; i++) {
	if (queryParams[i] in argv) {
		queryObject[queryParams[i]] = argv[queryParams[i]];
	}
}

app = require('./lib/app.js');

var getDocuments = function (queryObject) {
  app.getDocuments(queryObject, function (data) {
    var docs = JSON.parse(data.toString()).items;
    for (var i = 0; i < docs.length; i++) {
      var privacy = docs[i].public ? 'public' : 'private';
      var ownerName = (docs[i].owner && ('name' in docs[i].owner)) ? docs[i].owner.name : 'nobody';
      console.log(docs[i].name + '    ' + privacy + '   Owned by: ' + ownerName);
    }
  });
};

getDocuments(queryObject);
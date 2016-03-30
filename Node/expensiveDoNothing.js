var util = require('./lib/util.js');
var errors = require('./config/errors.js');

var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will create an element then delete it, resulting in nothing particularly helpful.\n');
  console.log('\tUsage: node expensiveDoNothing.js -d <documentId> -w <workspaceId>');
  process.exit(0);
}
if (!argv['d'] || !argv['w']) {
  util.error(errors.missingDocumentOrWorkspaceError);
}

app = require('./lib/app.js');
app.expensiveDoNothing(argv['d'], argv['w']);
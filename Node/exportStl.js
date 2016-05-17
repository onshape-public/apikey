var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will export a part studio as STL and print the STL file to the console.\n');
  console.log('\tUsage: node exportStl.js -d <documentId> -w <workspaceId> -e <workspaceId>');
  process.exit(0);
}
if (!argv['d'] || !argv['w'] || !argv['e']) {
  util.error(errors.missingDWEError);
}

app = require('./lib/app.js');

var partStudioStl = function (documentId, workspaceId, elementId) {
  app.partStudioStl(documentId, workspaceId, elementId, null, function (data) {
    console.log(data.toString());
  });
}

partStudioStl(argv['d'], argv['w'], argv['e']);
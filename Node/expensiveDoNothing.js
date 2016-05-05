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

var expensiveDoNothing = function (documentId, workspaceId) {
  partStudioId = null;

  var createPartStudioStep = function () {
    var name = 'DELETE THIS PART STUDIO!';
    app.createPartStudio(documentId, workspaceId, name, function (data) {
      partStudioId = JSON.parse(data.toString()).id;
      console.log('Created a part studio with id ' + partStudioId + '.');
      deleteElementStep();
    });
  };

  var deleteElementStep = function () {
    app.deleteElement(documentId, workspaceId, partStudioId, function (data) {
      console.log('Deleted that part studio with id ' + partStudioId + '.  Nothing has actually been accomplished.');
    });
  };

  createPartStudioStep();
}

expensiveDoNothing(argv['d'], argv['w']);
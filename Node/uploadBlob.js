var util = require('./lib/util.js');
var errors = require('./config/errors.js');
var pathModule = require('path');

var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will upload a given file to a new blob element.\n');
  console.log('\tUsage: node uploadBlob.js -d <documentId> -w <workspaceId> -f <filepath> -t <MIME type>');
  console.log('An example file is provided at ./example/blobexample.txt, with MIME type text/plain.');
  process.exit(0);
}
if (!argv['d'] || !argv['w']) {
  util.error(errors.missingDocumentOrWorkspaceError);
}
if (!argv['t']) {
  util.error(errors.missingMimeType);
}
if (!argv['f']) {
  util.error(errors.missingFile);
}

app = require('./lib/app.js');

var uploadBlob = function (documentId, workspaceId, file, mimeType) {
  app.uploadBlobElement(documentId, workspaceId, file, mimeType, function (data) {
    var blobData = JSON.parse(data.toString());
    console.log('Uploaded file to new element with id ' + blobData.id + ' and name ' + blobData.name + '.');
  });
}

uploadBlob(argv['d'], argv['w'], pathModule.normalize(argv['f']), argv['t']);
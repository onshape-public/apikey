var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will tally the total weight of each material in a given part studio.\n');
  console.log('\tUsage: node . -d <documentId> -[wvm] <wvmId> -e <elementId>');
  console.log('\n(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm]\n');
  process.exit(0);
}
var versionContext = 0;
var wvm = null;
if (argv['w']) {
  versionContext++;
  wvm = 'w';
}
if (argv['v']) {
  versionContext++;
  wvm = 'v';
}
if (argv['m']) {
  versionContext++;
  wvm = 'm';
}
if (versionContext !== 1) {
  console.log('You must specify exactly one of -w (workspaceId), -v (versionId), or -m (microversionId).');
  process.exit(1);
}
if (!argv['d'] || !argv['e']) {
  console.log('You must specify a -d (documentId) and -e (elementId).');
  process.exit(1);
}

app = require('./lib/app.js');
app(argv['d'], wvm, argv[wvm], argv['e']);
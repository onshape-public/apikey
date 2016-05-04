var util = require('./lib/util.js');
var errors = require('./config/errors.js');

var minimist = require('minimist');
var app = null;

var argv = minimist(process.argv.slice(2));
if (argv['u'] || argv['usage'] || argv['h'] || argv['help']) {
  console.log('\nThis app will tally the total weight of each material in a given part studio.\n');
  console.log('\tUsage: node massByMaterial.js -d <documentId> -[wvm] <wvmId> -e <elementId>');
  console.log('\n(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm])\n');
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
  util.error(errors.versionContextError);
}
if (!argv['d'] || !argv['e']) {
  util.error(errors.missingDocumentOrElementError);
}

app = require('./lib/app.js');

var massByMaterial = function (documentId, wvm, wvmId, elementId) {
  var partsByMaterial = {};
  var massesByMaterial = {};

  var getPartsStep = function () {
    app.getParts(documentId, wvm, wvmId, elementId, function (data) {
      var partsList = JSON.parse(data.toString()); // it's a JSON array
      for (var i = 0; i < partsList.length; i++) {
        if (partsList[i]['material'] === undefined) {
          continue;
        }
        if (!(partsList[i]['material']['id'] in partsByMaterial)) {
          partsByMaterial[partsList[i]['material']['id']] = [];
        }
        partsByMaterial[partsList[i]['material']['id']].push(partsList[i]['partId']);
      }
      getMassPropertiesStep();
    });
  };

  var getMassPropertiesStep = function () {
    app.getMassProperties(documentId, wvm, wvmId, elementId, function (data) {
      var massList = JSON.parse(data.toString());
      var totalMass = 0;
      for (var material in partsByMaterial) {
        massesByMaterial[material] = 0;
        for (var i = 0; i < partsByMaterial[material].length; i++) {
          if (massList.bodies[partsByMaterial[material][i]]['hasMass']) {
            massesByMaterial[material] += massList.bodies[partsByMaterial[material][i]]['mass'][0];
            totalMass += massList.bodies[partsByMaterial[material][i]]['mass'][0];
          }
        }
        console.log(material + ': ' + massesByMaterial[material]);
      }
      console.log('—-———-—-–—-–—––--——-–—-–––-–––');
      console.log('Total mass: ' + totalMass);
    });
  };

  getPartsStep();
};

massByMaterial(argv['d'], wvm, argv[wvm], argv['e']);
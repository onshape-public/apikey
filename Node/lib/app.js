var util = require('./util.js');
var errors = require('../config/errors.js');

var onshape = require('./onshape.js');

var getParts = function (documentId, wvm, wvmId, elementId, cb) {
  var opts = {
    d: documentId,
    e: elementId,
    resource: 'parts'
  };
  opts[wvm] = wvmId;
  onshape.get(opts, cb);
}

var getMassProperties = function (documentId, wvm, wvmId, elementId, cb) {
  var opts = {
    d: documentId,
    e: elementId,
    resource: 'partstudios',
    subresource: 'massproperties',
    query: {
      massAsGroup: false
    }
  }
  opts[wvm] = wvmId;
  onshape.get(opts, cb);
}

var createPartStudio = function (documentId, workspaceId, name, cb) {
  var opts = {
    d: documentId,
    w: workspaceId,
    resource: 'partstudios'
  }
  if (typeof name === 'string') {
    opts.body = {name: name};
  }
  onshape.post(opts, cb);
}

var deleteElement = function (documentId, workspaceId, elementId, cb) {
  var opts = {
    d: documentId,
    w: workspaceId,
    e: elementId,
    resource: 'elements',
  }
  onshape.delete(opts, cb);
}

var uploadBlobElement = function (documentId, workspaceId, file, mimeType, cb) {
  var opts = {
    d: documentId,
    w: workspaceId,
    resource: 'blobelements',
    file: file,
    mimeType: mimeType
  }
  onshape.upload(opts, cb);
}

var massByMaterial = function (documentId, wvm, wvmId, elementId) {
  var partsByMaterial = {};
  var massesByMaterial = {};

  var getPartsStep = function () {
    getParts(documentId, wvm, wvmId, elementId, function (data) {
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
    getMassProperties(documentId, wvm, wvmId, elementId, function (data) {
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

var expensiveDoNothing = function (documentId, workspaceId) {
  partStudioId = null;

  var createPartStudioStep = function () {
    var name = 'DELETE THIS PART STUDIO!';
    createPartStudio(documentId, workspaceId, name, function (data) {
      partStudioId = JSON.parse(data.toString()).id;
      console.log('Created a part studio with id ' + partStudioId + '.');
      deleteElementStep();
    });
  };

  var deleteElementStep = function () {
    deleteElement(documentId, workspaceId, partStudioId, function (data) {
      console.log('Deleted that part studio with id ' + partStudioId + '.  Nothing has actually been accomplished.');
    });
  };

  createPartStudioStep();
}

var uploadBlob = function (documentId, workspaceId, file, mimeType) {
  uploadBlobElement(documentId, workspaceId, file, mimeType, function (data) {
    var blobData = JSON.parse(data.toString());
    console.log('Uploaded file to new element with id ' + blobData.id + ' and name ' + blobData.name + '.');
  });
}

module.exports = {
  massByMaterial: massByMaterial,
  expensiveDoNothing: expensiveDoNothing,
  uploadBlob: uploadBlob
}
var onshape = null;

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

var getDocuments = function (queryObject, cb) {
    var opts = {
        path: '/api/documents',
        query: queryObject
    }
    onshape.get(opts, cb);
}

var getEndpoints = function (cb) {
    var opts = {
        path: '/api/endpoints'
    }
    onshape.get(opts, cb);
}

var partStudioStl = function (documentId, workspaceId, elementId, queryObject, cb) {
    var opts = {
        d: documentId,
        w: workspaceId,
        e: elementId,
        query: queryObject,
        resource: 'partstudios',
        subresource: 'stl',
        headers: {
            'Accept': 'application/vnd.onshape.v1+octet-stream'
        }
    };
    onshape.get(opts, cb);
}

module.exports = function (creds) {
    onshape = require('./onshape.js')(creds);
    return {
        getParts: getParts,
        getMassProperties: getMassProperties,
        createPartStudio: createPartStudio,
        deleteElement: deleteElement,
        uploadBlobElement: uploadBlobElement,
        getDocuments: getDocuments,
        getEndpoints: getEndpoints,
        partStudioStl: partStudioStl
    };
};

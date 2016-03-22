This sample app tallies the total weight of each material used in a given part studio element.

To use it, you must have node and npm installed on your computer, and run `npm install` on the command line in this directory to install the dependencies.  Run the app with `node .` in this directory.  Try `node . -u` or `node . --usage` to print the following usage message:

`This app will tally the total weight of each material in a given part studio.`  
`    Usage: node massByMaterial.js -d <documentId> -[wvm] <wvmId> -e <elementId>`  
`(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm])`

You must also copy config/apikeyexample.js to a new file called apikey.js inside the config directory; build an API key (with at least read permission) through the Developer Portal, and add these credentials to it.  Make sure that the API key corresponds to the stack against which you are running the app -- if you are running it against partner.dev.onshape.com, create the API key with the partner Developer Portal, not the one on production.

To get a meaningful result, you'll also need a part studio with parts that have been assigned some materials, of course!
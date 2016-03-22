This series of sample apps illustrate the use of API keys to call Onshape APIs with Node.js.  The following apps are available:

massByMaterial
expensiveDoNothing

To use them, you must have node and npm installed on your computer, and run `npm install` on the command line in this directory to install the dependencies.  Run the app with `node <app>` in this directory.  Try `node <app> -u` or `node <app> --usage` to print a usage message specifying the parameters.

You must also copy config/apikeyexample.js to a new file called apikey.js inside the config directory; build an API key (with at least the relevant permissions) through the Developer Portal, and add these credentials to it.  Make sure that the API key corresponds to the stack against which you are running the app -- if you are running it against partner.dev.onshape.com, create the API key with the partner Developer Portal, not the one on production.

# massByMaterial

This massByMaterial sample app tallies the total weight of each material used in a given part studio element.  (Requires OAuth2Read)

This is the usage message:

`This app will tally the total weight of each material in a given part studio.`  
`    Usage: node massByMaterial.js -d <documentId> -[wvm] <wvmId> -e <elementId>`  
`(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm])`

To get a meaningful result, you'll also need a part studio with parts that have been assigned some materials, of course!

# expensiveDoNothing

This expensiveDoNothing.js sample app creates an element then deletes it, which provides no potential benefit to the user, but at least it does so using API keys.  (Requires OAuth2Write, OAuth2Delete)

This is the usage message:

`This app will create an element then delete it, resulting in nothing particularly helpful.`  
`    Usage: node expensiveDoNothing.js -d <documentId> -w <workspaceId>`


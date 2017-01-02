This series of sample apps illustrate the use of API keys to call Onshape APIs with Node.js.  The following apps are available:

massByMaterial
expensiveDoNothing
uploadBlob
getDocuments
exportStl

To use them, you must have node and npm installed on your computer, and run `npm install` on the command line in this directory to install the dependencies.  Run the app with `node <app>` in this directory.  Try `node <app> -u` or `node <app> --usage` to print a usage message specifying the parameters.

You must also copy config/apikeyexample.js to a new file called apikey.js inside the config directory; build an API key (with at least the relevant permissions) through the Developer Portal, and add these credentials to it.  Make sure that the API key corresponds to the stack against which you are running the app -- for most users it should just be cad.onshape.com.

# massByMaterial

This massByMaterial.js sample app tallies the total weight of each material used in a given part studio element.  It demonstrates a generic GET request.  (Requires OAuth2Read)

### Usage:

`This app will tally the total weight of each material in a given part studio.`  
`    Usage: node massByMaterial.js -d <documentId> -[wvm] <wvmId> -e <elementId>`  
`(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm])`

To get a meaningful result, you'll also need a part studio with parts that have been assigned some materials, of course!

# expensiveDoNothing

This expensiveDoNothing.js sample app creates an element then deletes it, which provides no potential benefit to the user, but at least it does so using API keys.  It demonstrates generic POST and DELETE requests.  (Requires OAuth2Write, OAuth2Delete)

### Usage:

`This app will create an element then delete it, resulting in nothing particularly helpful.`  
`    Usage: node expensiveDoNothing.js -d <documentId> -w <workspaceId>`

# uploadBlob

This uploadBlob.js sample app creates a new blob element from a given file.  It demonstrates a multi-part file upload.  (Requires OAuth2Write)

### Usage:

`This app will upload a given file to a new blob element.`  
`    Usage: node uploadBlob.js -d <documentId> -w <workspaceId> -f <filepath> -t <MIME type>`  
`An example file is provided at ./example/blobexample.txt, with MIME type text/plain.`

# getDocuments

This getDocuments.js sample app simply gets a list of documents with given query parameters.  It demonstrates GET requests.  (Requires OAuth2Read)

### Usage:

`This app will get documents available to the user with the specified query params.`  
`    Usage: node getDocuments.js [--query <query>] [--filter <filter>] [--owner <owner>] [--ownerType <ownerType>] [--sortColumn <sortColumn>] [--sortOrder <sortOrder>] [--offset <offset>] [--limit <limit>]`  
`See API documentation for query parameters.`

# exportStl

This exportStl.js sample app exports a given part studio as STL and helpfully prints it to the console.  It demonstrates GET requests resulting in 307 redirects.  (Requires OAuth2Read)

### Usage:

`This app will export a part studio as STL and print the STL file to the console.`  
`Usage: node exportStl.js -d <documentId> -w <workspaceId> -e <workspaceId>`
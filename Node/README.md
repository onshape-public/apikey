This sample app tallies the total weight of each material used in a given part studio element.

To use it, you must have node and npm installed on your computer, and run `npm install` on the command line in this directory to install the dependencies.  Run the app with `node .` in this directory.  Try `node . -u` or `node . --usage` to print the following usage message:

`This app will tally the total weight of each material in a given part studio.`
`    Usage: node . -d <documentId> -[wvm] <wvmId> -e <elementId>`
`(wvmId should be a workspaceId (-w), versionId (-v), or microversionId (-m), depending on the given value of [wvm])`
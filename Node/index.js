// creds should look like:
// {
// 	'baseUrl': 'https://cad.onshape.com',
// 	'accessKey': 'accesskey',
// 	'secretKey': 'secretkey'
// }
function client (creds) {
    return require('./lib/app')(creds);
}

module.exports = client;

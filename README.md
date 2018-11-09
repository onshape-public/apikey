# Onshape API Key Sample Apps

Simple Node.js and Python apps to demonstrate API key usage

This is a fork of the official OnShape apikey repository (https://github.com/onshape/apikey). In this fork I have added
an ClientExtended class which adds functionality to the Client class in the original repository. Extension include:

- Allowing credential to be in a specified file location
- Additional api calls for: lists of teams, parts, elements, and workspaces, setting part metadata, fetching bills of material (BOMs), paged output (Pager).
- onshape_util - a Python-based interactive, command line (CLI) utility to run OnShape api calls.
- api_doc_util - a Python-based interactive, command line (CLI) utility that uses onshapepy to view and export 
documentation for the REST API.

Note: There is another fork of the code with the same project name (AguaClara/onshapepy). We are working to merge the two together to get a single version with a superset of the two projects.

---

### Getting Started

Please see the [node](https://github.com/onshape/apikey/tree/master/Node) and
[python](https://github.com/onshape/apikey/tree/master/python) folders for
instructions on working with each of the applications.

### Why API Keys?

API keys are useful for small applications meant for personal use, allowing developers to avoid the overhead of the OAuth workflow.  Creating an app is very easy with API keys, as the samples hopefully demonstrate: create an API key with the Developer Portal, set up a function to build your API key header as in the samples, and make your API calls!  There's no need to deal with OAuth redirects or things like that.

We've moved over to using API keys for authenticating requests instead of using
cookies for several reasons.

1. Security: Each request is signed with unique headers so that we can be sure it's
coming from the right place.
2. OAuth: The API key system we're now using for HTTP requests is the same process
developers follow when building full-blown OAuth applications; there's no longer a disconnect
between the two.

### Questions and Concerns

If you need information or have a question unanswered in this documentation,
feel free to chat with us by sending an email to
[api-support@onshape.com](mailto:api-support@onshape.com) or by checking out
the [forums](https://forum.onshape.com/).

### Working with API Keys

Read the following and you'll be up and running with using API keys in your
application:

##### Instructions

1. Get the Developer role for your Onshape account by contacting us at
[api-support@onshape.com](mailto:api-support@onshape.com).

2. Create and manage your API key pairs from the [Developer Portal](https://dev-portal.dev.onshape.com);
note that the secret will only be displayed once! Keep it somewhere safe.

3. Now that you have a key pair, see [below](#generating-a-request-signature) for
information on signing your requests to use our API.

Once you have your access key and secret, you will want to avoid giving others access to them since they're tied directly to your personal Onshape account.  Think of your API key as a username and password pair.  Therefore, you should avoid placing them directly in the code for your application, especially if others might see it.  The samples use a separate configuration file that you yourself will need to create that will contain this information, but there are other ways to keep the access key and secret safe, like setting them as environment variables.

##### Scopes

There are several scopes available for API keys (equivalent to OAuth scopes):

* "OAuth2Read" - Read non-personal information (documents, parts, etc.)
* "OAuth2ReadPII" - Read personal information (name, email, etc.)
* "OAuth2Write" - Create and edit documents / etc.
* "OAuth2Delete" - Delete documents / etc.
* "OAuth2Purchase" - Authorize purchases from account

##### Generating A Request Signature

To ensure that a request is coming from you, we have a process for signing
requests that you must follow for API calls to work. Everything is done via HTTP
headers that you'll need to set:

1. *Date*: A standard date header giving the time of the request; must be
accurate within **5 minutes** of request. Example: `Mon, 11 Apr 2016 20:08:56 GMT`
2. *On-Nonce*: A string that satisfies the following requirements (see the code for one possible way to generate it):
    * At least 16 characters
    * Alphanumeric
    * Unique for each request
3. *Authorization*: This is where the API keys come into play. You'll sign the request by implementing this algorithm:
    * **Input**: Method, URL, On-Nonce, Date, Content-Type, AccessKey, SecretKey
    * **Output**: String of the form: `On <AccessKey>:HmacSHA256:<Signature>`
    * **Steps to generate the signature portion**:
        1. Parse the URL and get the following:
            1. The path, e.g. `/api/documents` (no query params!)
            2. The query string, e.g. `a=1&b=2`
                * NOTE: If no query paramaters are present, use an empty string
        2. Create a string by appending the following information in order. Each
        field should be separated by a newline (`\n`) character, and the string
        must be converted to lowercase:
            1. HTTP method
            2. On-Nonce header value
            3. Date header value
            4. Content-Type header value
            5. URL pathname
            6. URL query string
        3. Using SHA-256, generate an [HMAC digest](https://en.wikipedia.org/wiki/Hash-based_message_authentication_code),
        using the API secret key first and then the above string, then encode it in Base64.
        4. Create the `On <AccessKey>:HmacSHA256:<Signature>` string and use that in the Authorization header in your request.

Below is an example function to generate the authorization header, using
Node.js's standard `crypto` and `url` libraries:

```js
// ...at top of file
var u = require('url');
var crypto = require('crypto');

/**
* Generates the "Authorization" HTTP header for using the Onshape API
*
* @param {string} method - Request method; GET, POST, etc.
* @param {string} url - The full request URL
* @param {string} nonce - 25-character nonce (generated by you)
* @param {string} authDate - UTC-formatted date string (generated by you)
* @param {string} contentType - Value of the "Content-Type" header; generally "application/json"
* @param {string} accessKey - API access key
* @param {string} secretKey - API secret key
*
* @return {string} Value for the "Authorization" header
*/
function createSignature(method, url, nonce, authDate, contentType, accessKey, secretKey) {
    var urlObj = u.parse(url);
    var urlPath = urlObj.pathname;
    var urlQuery = urlObj.query ? urlObj.query : ''; // if no query, use empty string

    var str = (method + '\n' + nonce + '\n' + authDate + '\n' + contentType + '\n' +
        urlPath + '\n' + urlQuery + '\n').toLowerCase();

    var hmac = crypto.createHmac('sha256', secretKey)
        .update(str)
        .digest('base64');

    var signature = 'On ' + accessKey + ':HmacSHA256:' + hmac;
    return signature;
}
```

Some API endpoints return 307 redirects.  You must generate an Authorization header for the redirect as well, but please note that the server portion of the URL might be different, the redirect URL may contain query parameters that must be encoded in the Authorization header, etc.  Please see the samples for examples.

### API keys and OAuth

Our API key workflow differs from our OAuth workflow in one important characteristic: an API key allows a *user* (specifically, a developer) to make requests, while OAuth allows an *application* to make requests on behalf of the user.  We require the OAuth workflow for apps in the Onshape App Store, so if you develop an app using API keys and want to distribute it through the App Store, you will need to change to OAuth.  Please see our OAuth sample apps for examples of how to make OAuth work (onshape/app-bom is a great place to start).  The good news is that we've structured API keys to work very similarly to OAuth in the operation of your app.  While you will need to build your Authorization header differently (and set up redirects and signins as in the onshape/app-bom sample), the API calls themselves will work the same in both versions, provided that the API key and the OAuth app have the same scopes.  An API key with the OAuth2Read and OAuth2Write scopes will have the same access to the same API endpoints as an OAuth application with the OAuth2Read and OAuth2Write scopes, for example.  (The only differences are when calling API endpoints relating to the OAuth application itself, since an API key request obviously does not come from an OAuth application.)

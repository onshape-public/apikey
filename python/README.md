# Python API Key Sample

Simple demonstration of getting a key and structuring API calls.

---

### Local Setup

Install the dependencies:

* Python 2
* pip
* virtualenv

Then, from this folder:

```sh
$ virtualenv -p /path/to/python2 env && source env/bin/activate
```

You can now install the needed Python packages:

```sh
$ pip install -r requirements.txt
```

To exit the virtual environment at any time, simply type `deactivate`.

### Running the App

Create a `creds.json` file in the root project directory, with the following format:

```json
{
    "https://partner.dev.onshape.com": {
        "access_key": "ACCESS KEY",
        "secret_key": "SECRET KEY"
    },
    "https://cad.onshape.com": {
        "access_key": "ACCESS KEY",
        "secret_key": "SECRET KEY"
    }
}
```

Just replace "ACCESS KEY" and "SECRET KEY" with the values you got from the
developer portal. To test on other stacks, you'll create another object in the file,
with credentials for that specific stack.

To run the application:

```sh
$ python app.py
```

If you want to specify a different stack to test on, simply go into `app.py` and
change the `stack` parameter on this line:

```py
c = Client(stack='NEW STACK HERE')
```

The demo does a few basic things to demonstrate GET, POST, and DELETE calls:

1. Creates a new document
2. Gets your list of documents
3. Deletes the new document

### Working w/ API Keys

For general information on our API keys and how they work, read this
[document](https://github.com/onshape/apikey/blob/master/README.md). For general
API support, please reach out to us at
[api-support@onshape.com](mailto:api-support@onshape.com).

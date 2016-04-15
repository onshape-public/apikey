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

To run the app, simply do the following:

```bash
$ ONSHAPE_ACCESS_KEY="ACCESS KEY" ONSHAPE_SECRET_KEY="SECRET KEY" python app.py
```

Of course, replace "ACCESS KEY" and "SECRET KEY" with the values you got from the
developer portal.

The demo does a few basic things, to demonstrate GET, POST, and DELETE calls:

1. Creates a new document
2. Gets your list of documents
3. Deletes the new document

### Working w/ API Keys

For general information on our API keys and how they work, read this
[document](https://github.com/onshape/apikey/blob/master/README.md). For general
API support, please reach out to us at
[api-support@onshape.com](mailto:api-support@onshape.com).

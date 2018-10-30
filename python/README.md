# Python API Key Sample

OnShapepy

Python package to use the OnShape API. Based on apikey by Ty-Lucas Kelley.

This README is out of date....

- Can use Python 3+
- Can keep credentials in any file (pass in creds filename)

---

### Local Setup

Install the dependencies:

* Python 2 (2.7.9+). Python 3.5+ is better!
* pip
* note: it's best to do all of this in a virtual env. See pipenv for the latest...

You can now install the needed Python packages:

```sh
$ pip install -r requirements.txt
```

Create a `creds.json` file in the root project directory, with the following format:

```json
{
    "https://cad.onshape.com": {
        "access_key": "ACCESS KEY",
        "secret_key": "SECRET KEY"
    }
}
```

Just replace "ACCESS KEY" and "SECRET KEY" with the values you got from the
developer portal. To test on other stacks, you'll create another object in the file,
with credentials for that specific stack.

To run the basic application:

```sh
$ python onshape_util.py
```

The old basic app

```sh
$ python app.py
```

To print an STL representation of a given part studio to the console:

```sh
$ python exportstl.py
```

If you want to specify a different stack to test on, simply go into the file you're running and
change the `stack` parameter on this line:

```py
c = ClientExtended(stack='https://cad.onshape.com', creds='path/to/creds.json')
```

To get information regarding the onshape api run:

```sh
$ python get_endpoints.py
```

This will use to Onshape api to get documentation about the onShape api. Note: this utility requires pip
installing cooked_input from pypi.


### Working with API Keys

For general information on our API keys and how they work, read this
[document](https://github.com/onshape/apikey/blob/master/README.md). For general
API support, please reach out to us at
[api-support@onshape.com](mailto:api-support@onshape.com).

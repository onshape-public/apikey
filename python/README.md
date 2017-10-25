# Python API Key Sample

Simple demonstration of getting a key and structuring API calls.

---

### Local Setup

Install the dependencies:

* Python 2 (2.7.9+)
* pip
* virtualenv

Then, from this folder:

--for Linux:
```sh
$ virtualenv -p /path/to/python2 env && source env/bin/activate
```

--for Windows:
```sh
$ virtualenv -p /path/to/python2.exe env && env/Scripts/activate.bat
```
References:

* https://stackoverflow.com/questions/8921188/issue-with-virtualenv-cannot-activate
* https://virtualenv.pypa.io/en/stable/userguide/#activate-script

You can now install the needed Python packages:

--for Linux:
```sh
$ pip install -r requirements.txt
```

--for Windows:
```sh
$ pip install -r requirements-win.txt
```

The windows-specific requirements file encompasses libraries that work for Win-OS

References:
* https://pypi.python.org/pypi/pyreadline

To exit the virtual environment at any time, simply type `deactivate`.

### Running the App

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
$ python app.py
```

To print an STL representation of a given part studio to the console:

```sh
$ python exportstl.py
```

If you want to specify a different stack to test on, simply go into the file you're running and
change the `stack` parameter on this line:

```py
c = Client(stack='NEW STACK HERE')
```

### Working with API Keys

For general information on our API keys and how they work, read this
[document](https://github.com/onshape/apikey/blob/master/README.md). For general
API support, please reach out to us at
[api-support@onshape.com](mailto:api-support@onshape.com).

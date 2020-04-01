# DealCloud for Python

This package provides two functions for working with the DealCloud Web Service
from Python: `create_client()` and `bind_service()`. It also comes with
examples of basic usage. As a SOAP service, the usage pattern will be familiar
to those with experience with XML and SOAP services. This package can be used
successfully with Python versions 3.6 and higher.


## Getting Started

To get started on Windows, create your virtual environment and install the
package by cloning this repository and running the setup script. See the 
[Installation Notes](https://github.com/holtjp/dealcloud-python#installation-notes-for-linux-users)
if you are a Linux user and the setup script raises exceptions.

```
python setup.py install
```

Now, all you need to do is review the examples and apply similar patterns.
Simply create an instance of the client and a service proxy and then you're
ready to go.

```python
import dealcloud as dc


client = dc.create_client(
    email='user@dealcloud.com', password='super_secret!', hostname='yoursite'
)
service = dc.bind_service(client)
```

`client` will be an instance of `zeep.client.Client` and `service` will be an
instance of `zeep.proxy.ServiceProxy`. So everything you might know about
interacting with SOAP services via Zeep is applicable here as well. If you
are not familiar with the Zeep project, you can find the package on the
Python Package Index [here](https://pypi.org/project/zeep/) and read the
documentation [here](https://python-zeep.readthedocs.io/en/master/).

### Installation Notes for Linux Users

The DealCloud for Python package relies on Zeep, which in turn relies on the
lxml and requests packages. This means that you may need to install libxml2-dev
and libxslt-dev on your system if they are not already present. For example,
you can use this line on a Debian-based distribution:

```bash
sudo apt-get install libxml2-dev libxslt-dev
```

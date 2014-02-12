python-gssapi
=============

Attempt at an object-oriented interface to GSSAPI for Python.
This project is licensed under the terms of the MIT license (see LICENSE.txt).


Python3 Support
---------------
python-gssapi is able to run on Python3, but to install it you can't use the setup script right now,
because the ctypesgen module used to build the gssapi_h module is not able to run on Python3 and it
generates just Python2 code.
An issue about Python3 support for ctypesgen has been opened on Google Code.
So to install python-gssapi on Python3 use the following stetps:
- Build python-gssapi on Python2. Do not install it, just build it.
- Look for the generated gssapi_h module in your build directory and use 2to3 to port it to py3
- Move the converted gssapi_h module into the gssapi source directory.
- Finally move the gssapi source directory to /path/to/your/python/installation/lib/python3.x/site-packages/

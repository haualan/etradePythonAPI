# etradePythonAPI

Applying machine learning methods to investing could be a fun thing to do, but there are barriers for investors even if they are well versed in Python. It is quite difficult to implement SciPy or NumPy models when most of the brokerage houses only provide APIs with Java or C++ examples. This is an open source library I've written that allows easy integration with Etrade's API for those investors who are looking to write programs in Python.

Before initial use:
  * Edit settings file in etrade_settings.py
  * Request a consumer key and secret key from etrade

Example workflow:
```
import etradepy as et
et.Login()
et.listAccounts()
```


# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paymentsgate']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=44.0.2,<45.0.0',
 'httpx>=0.28.1,<0.29.0',
 'jwt>=1.3.1,<2.0.0',
 'pydantic>=2.8.2,<3.0.0',
 'ruff>=0.11.7,<0.12.0',
 'tomli>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'paymentsgate',
    'version': '1.5.9',
    'description': "PaymentsGate's Python SDK for REST API",
    'long_description': '\n# Paymentsgate Python SDK for Payments REST API\n\n\n## Requirements\n\n- Python >= 3.8.1\n- dependencies:\n  - [`requests`](https://github.com/kennethreitz/requests)\n  - [`pydantic`](https://docs.pydantic.dev/latest/)\n  - [`jwt`](https://pyjwt.readthedocs.io/en/stable/)\n  \n## Installation\n\nThe simplest way to install SDK is to use [PIP](https://docs.python.org/3/installing/):\n\n```bash\npip install paymentsgate\n```\n\n## Basic usage\n\n```python\nfrom paymentsgate import ApiClient, Credentials, Currencies\n\n\n# minimal configuration\nconfig = Credentials().fromFile(\'/path/to/credentials.json\');\n\n# create ApiClient\nclient = ApiClient(config, baseUrl=\'https://api.example.com\');\n\n# request quote\nres = cli.Quote(\n  {\n    "amount": 10.10,\n    "currency_from": Currencies.EUR,\n    "currency_to": Currencies.AZN,\n  }\n)\nprint(res);\n```\n\nThe `credentials.json` file is used to connect to the client and contains all necessary data to use the API. This file can be obtained in your personal cabinet, in the service accounts section. Follow the instructions in the documentation to issue new keys. If you already have keys, but you don\'t feel comfortable storing them in a file, you can use client initialization via variables. In this case, the key data can be stored in external storage instead of on the file system:\n\n```python\nfrom paymentsgate import ApiClient, Credentials\n\nconfig = Credentials(\n  account_id="00000000-4000-4000-0000-00000000000a" \n  public_key="LS0tLS1CRUdJTiBSU0EgUFJJVkFUNSUlFb3dJQk..."\n)\n\nclient = ApiClient(config, baseUrl=\'https://api.example.com\');\n\n...\n```\n*It is important to note that the data format for key transfer is base46.\n\n## Examples\n\n### create PayIn\n\n```python\nres = cli.PayIn(\n  {\n    "amount": 10.10,\n    "currency": Currencies.AZN,\n    "invoiceId": "INVOICE-112123124",\n    "clientId": "",\n    "successUrl": "https://example.com/success",\n    "failUrl": "https://example.com/fail",\n    "type": InvoiceTypes.m10\n  }\n)\nprint(res);\n```\n\n### create PayOut\n\n```python\nres = cli.PayOut(\n  {\n    "amount": 5.12,\n    "currencyTo": Currencies.EUR,\n    "invoiceId": "INVOICE-112123124",\n    "clientId": "CLIENT-003010023004",\n    "baseCurrency": CurrencyTypes.fiat,\n    "feesStrategy": FeesStrategy.add,\n    "recipient": {\n      "account_number": "4000000000000012",\n      "account_owner": "CARD HOLDER",\n      "type": CredentialsTypes.card\n    }\n  }\n)\nprint(res);\n```\n\n### Error handling\n\n```python\ntry:\n  res = cli.PayOut(\n    {\n      "amount": 5.12,\n      "currencyTo": Currencies.EUR,\n      "invoiceId": "INVOICE-112123124",\n      "clientId": "CLIENT-003010023004",\n      "baseCurrency": CurrencyTypes.fiat,\n      "feesStrategy": FeesStrategy.add,\n      "recipient": {\n        "account_number": "4000000000000012",\n        "account_owner": "CARD HOLDER",\n        "type": CredentialsTypes.card\n      }\n    }\n  )\n  print(res);\nexcept APIAuthenticationError as err:\n  print(f"Authentication fail: {err.message}")\nexcept APIResponseError as err:\n  print(f"Exception: {err.error}; Message: {err.message}")\n```',
    'author': 'PaymentsGate',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/paymentsgate/python-secure-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

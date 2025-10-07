
# Paymentsgate Python SDK for Payments REST API


## Requirements

- Python >= 3.8.1
- dependencies:
  - [`requests`](https://github.com/kennethreitz/requests)
  - [`pydantic`](https://docs.pydantic.dev/latest/)
  - [`jwt`](https://pyjwt.readthedocs.io/en/stable/)
  
## Installation

The simplest way to install SDK is to use [PIP](https://docs.python.org/3/installing/):

```bash
pip install paymentsgate
```

## Basic usage

```python
from paymentsgate import ApiClient, Credentials, Currencies


# minimal configuration
config = Credentials().fromFile('/path/to/credentials.json');

# create ApiClient
client = ApiClient(config, baseUrl='https://api.example.com');

# request quote
res = cli.Quote(
  {
    "amount": 10.10,
    "currency_from": Currencies.EUR,
    "currency_to": Currencies.AZN,
  }
)
print(res);
```

The `credentials.json` file is used to connect to the client and contains all necessary data to use the API. This file can be obtained in your personal cabinet, in the service accounts section. Follow the instructions in the documentation to issue new keys. If you already have keys, but you don't feel comfortable storing them in a file, you can use client initialization via variables. In this case, the key data can be stored in external storage instead of on the file system:

```python
from paymentsgate import ApiClient, Credentials

config = Credentials(
  account_id="00000000-4000-4000-0000-00000000000a" 
  public_key="LS0tLS1CRUdJTiBSU0EgUFJJVkFUNSUlFb3dJQk..."
)

client = ApiClient(config, baseUrl='https://api.example.com');

...
```
*It is important to note that the data format for key transfer is base46.

## Examples

### create PayIn

```python
res = cli.PayIn(
  {
    "amount": 10.10,
    "currency": Currencies.AZN,
    "invoiceId": "INVOICE-112123124",
    "clientId": "",
    "successUrl": "https://example.com/success",
    "failUrl": "https://example.com/fail",
    "type": InvoiceTypes.m10
  }
)
print(res);
```

### create PayOut

```python
res = cli.PayOut(
  {
    "amount": 5.12,
    "currencyTo": Currencies.EUR,
    "invoiceId": "INVOICE-112123124",
    "clientId": "CLIENT-003010023004",
    "baseCurrency": CurrencyTypes.fiat,
    "feesStrategy": FeesStrategy.add,
    "recipient": {
      "account_number": "4000000000000012",
      "account_owner": "CARD HOLDER",
      "type": CredentialsTypes.card
    }
  }
)
print(res);
```

### Error handling

```python
try:
  res = cli.PayOut(
    {
      "amount": 5.12,
      "currencyTo": Currencies.EUR,
      "invoiceId": "INVOICE-112123124",
      "clientId": "CLIENT-003010023004",
      "baseCurrency": CurrencyTypes.fiat,
      "feesStrategy": FeesStrategy.add,
      "recipient": {
        "account_number": "4000000000000012",
        "account_owner": "CARD HOLDER",
        "type": CredentialsTypes.card
      }
    }
  )
  print(res);
except APIAuthenticationError as err:
  print(f"Authentication fail: {err.message}")
except APIResponseError as err:
  print(f"Exception: {err.error}; Message: {err.message}")
```
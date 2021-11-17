# SecureTrust Portal API - WRM API code examples

## Index

* [Perl](#perl)
* [Python](#python)

### GitHub repo: [api-wrm-examples](./README.md)

This GitHub repo includes basic code examples for the SecureTrust Portal WRM API.

## Introduction

This repo contains some basic examples of different languages implementing the SecureTrust Portal WRM API. Use of this API does require a SecureTrust Portal user account that is enabled for API. Contact WRMSupport@securetrust.com if you are a SecureTrust WRM customer and need to request access.

## Perl

### Merchant list

The [wrmapi-merchant_list-csv.pl](./perl/wrmapi-merchant_list-csv.pl) file shows how to implement the Token API for authentication, and several methods of the WRM API, to create a CSV file containing information about all WRM Merchants, including the unique Merchant ID necessary for use with the WRM API.

## Python

### Merchant list

The [wrmapi-merchant_list-csv.py](./python/wrmapi-merchant_list-csv.py) file shows how to implement the Token API for authentication, and several methods of the WRM API, to create a CSV file containing information about all WRM Merchants, including the unique Merchant ID necessary for use with the WRM API.

## Credentials

You will need valid credentials for the SecureTrust portal that are enabled for API access. The example scripts store the credentials in a .json file: `creds.json`. This file must contain properly formatted JSON that matches the requirements for the [SecureTrust Portal Token API](https://developer.securetrust.com/openapi/token/operation/getToken/) getToken method.

### Example creds.json

```json
{
"username": "apiuser",
"password": "secret"
}
```

## License and additional information

### License
Copyright 2021 SecureTrust Inc.

This repository uses the Unlicense. See [LICENSE](./LICENSE) for details.

### SecureTrust Portal
The SecureTrust portal is can be accessed at (https://portal.securetrust.com/)

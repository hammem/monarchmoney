# Monarch Money

Python library for accessing [Monarch Money](https://www.monarchmoney.com/referral/ngam2i643l) data.

# Installation

## From Source Code

Clone this repository from Git

`git clone https://github.com/hammem/monarchmoney.git`

## Instantiate & Login

Before you can access any of your data, you'll need to create an instance and login:

```python
mm = MonarchMoney()
mm.login(email, password)
```

This may throw a `RequireMFAException`.  If it does, you'll need to get a multi-factor token and call the following method:

```python
mm.multi_factor_authenticate(email, password, multi_factor_code)
```

## Accessing Data

As of writing this README, the following methods are supported:

- `get_accounts` - all the accounts linked to Monarch Money 
- `get_subscription_details` - the Monarch Money account's status (e.g. paid or trial)
- `get_transactions` - transaction data, defaults to returning the last 100 transactions; can also be searched by date range
- `get_transaction_categories` all of the categories configured in the account
- `get_transaction_tags`  all of the tags configured in the account


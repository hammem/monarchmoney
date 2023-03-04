# Monarch Money

Python library for accessing [Monarch Money](https://www.monarchmoney.com/referral/ngam2i643l) data.

# Installation

## From Source Code

Clone this repository from Git

`git clone https://github.com/hammem/monarchmoney.git`

## From Tarball

Download it from GitHub

`curl -OJL https://github.com/hammem/monarchmoney/tarball/master`

and then install it:

`python setup.py install`

# Instantiate & Login

There are two ways to use this library: interactive and non-interactive.

## Interactive

If you're using this library in something like iPython or Jupyter, you can run an interactive-login which supports multi-factor authentication:

```python
mm = MonarchMoney()
await mm.interactive_login()
```
This will prompt you for the email, password and, if needed, the multi-factor token.

## Non-interactive

For a non-interactive session, you'll need to create an instance and login:

```python
mm = MonarchMoney()
mm.login(email, password)
```

This may throw a `RequireMFAException`.  If it does, you'll need to get a multi-factor token and call the following method:

```python
mm.multi_factor_authenticate(email, password, multi_factor_code)
```

# Accessing Data

As of writing this README, the following methods are supported:

- `get_accounts` - all the accounts linked to Monarch Money 
- `get_subscription_details` - the Monarch Money account's status (e.g. paid or trial)
- `get_transactions` - transaction data, defaults to returning the last 100 transactions; can also be searched by date range
- `get_transaction_categories` all of the categories configured in the account
- `get_transaction_tags`  all of the tags configured in the account


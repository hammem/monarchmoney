# Monarch Money

Python library for accessing [Monarch Money](https://www.monarchmoney.com/referral/ngam2i643l) data.

# Installation

## From Source Code

Clone this repository from Git

`git clone https://github.com/hammem/monarchmoney.git`

## Via `pip`

`pip install monarchmoney`
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

Alternatively, you can provide the MFA Secret Key. The MFA Secret Key is found when setting up the MFA in Monarch Money by going to Settings -> Security -> Enable MFA -> and copy the "Two-factor text code". Then provide it in the login() method:
```python
await nm.login(
        email=email,
        password=password,
        save_session=False,
        use_saved_session=False,
        mfa_secret_key=mfa_secret_key,
    )

```

# Accessing Data

As of writing this README, the following methods are supported:

- `get_accounts` - all the accounts linked to Monarch Money
- `get_account_holdings` - all of the securities in a brokerage or similar type of account
- `get_subscription_details` - the Monarch Money account's status (e.g. paid or trial)
- `get_transactions` - transaction data, defaults to returning the last 100 transactions; can also be searched by date range
- `get_transaction_categories` all of the categories configured in the account
- `get_transaction_tags` - all of the tags configured in the account
- `get_cashflow` - cashflow data (by category, category group, merchant and a summary)
- `get_cashflow_summary` - cashflow summary (income, expense, savings, savings rate)

# Contributing

Any and all contributions -- code, documentation, feature requests, feedback -- are welcome!

If you plan to submit up a pull request, you can expect a timely review.  There aren't any strict requirements around the environment you need to configure aside from using [Black](https://github.com/psf/black) to auto-format the code.  An action is configured in this repo to run against all PRs and merges and will block them from being committed.

# FAQ

**How do I use this API if I login to Monarch via Google?**

If you currently use Google or 'Continue with Google' to access your Monarch account, you'll need to set a password to leverage this API.  You can set a password on your Monarch account by going to your [security settings](https://app.monarchmoney.com/settings/security).  

Don't forget to use a password unique to your Monarch account and to enable multi-factor authentication!

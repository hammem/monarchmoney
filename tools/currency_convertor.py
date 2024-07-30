import asyncio
import json
from functools import lru_cache
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from monarchmoney import MonarchMoney
from currency_converter import CurrencyConverter, ECB_URL, RateNotFoundError
from datetime import date
import urllib.request
import os.path as op
import glob, os

from monarchmoney.monarchmoney import BalanceHistoryRow

# This script converts (a) transactions (b) account balances for Monarch accounts
# from USD to CAD, so that you can view your accounts in 1 currency.
#
# Note: the currency can easily be changed in the method "get_usd_cad_rate"
# Note: does not work for "holdings" based accounts (e.g. brokerages) yet

TRANSACTION_ACCOUNTS_TO_CONVERT = [
    # use mm.get_accounts to get account IDs
    # put the one's you want to convert from USD to CAD here
    "123412341241234",
]

# create a tag to track converted transactions and put the tag ID here
USD2CAD_TAG = "123412341241234"
# create a tag to track 'checkpoint' transactions put the tag ID here
CHECKPOINT_TAG = "123412341241234"
# create a category for checkpoint transactions (e.g. "python")
CHECKPOINT_CATEGORY_ID = "123412341241234"
THROUGHPUT = 10


async def get_unconverted_transactions(
    mm: MonarchMoney, account_id: str
) -> Dict[str, Any]:
    offset = 0
    limit = 100
    total = 100
    transactions = {}
    while offset < total:
        transaction_response = await mm.get_transactions(
            account_ids=[account_id], has_notes=False, offset=offset, limit=limit
        )
        if "allTransactions" in transaction_response:
            total = transaction_response["allTransactions"]["totalCount"]
            if "results" in transaction_response["allTransactions"]:
                results = transaction_response["allTransactions"]["results"]
                new_transactions = {
                    result["id"]: result
                    for result in results
                    if not result["tags"]
                    or USD2CAD_TAG not in [tag["id"] for tag in result["tags"]]
                }
                transactions.update(new_transactions)
                print(f"offset: {offset}, results: {len(results)}")
                offset += limit
    print(f"new/unconverted transactions: {len(transactions)}")
    return transactions


@lru_cache
def get_usd_cad_rate(date_str: str) -> Optional[float]:
    filename = f"ecb_{date.today():%Y%m%d}.zip"
    if not op.isfile(filename):
        urllib.request.urlretrieve(ECB_URL, filename)
    for f in glob.glob("ecb_*.zip"):
        if f != filename:
            os.remove(f)
    c = CurrencyConverter(filename)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    result = None
    delta = 0
    while delta <= 10:
        try:
            result = c.convert(1, "USD", "CAD", date=date_obj - timedelta(days=delta))
            return result
        except RateNotFoundError:
            delta += 1
    return result


async def update_transaction_task(
    mm: MonarchMoney,
    transaction: Dict[str, Any],
    cad_amount: float,
    usd_amount: float,
    sem: asyncio.Semaphore,
    dry_run: bool = False,
) -> None:
    async with sem:
        print(
            f"converting transaction {transaction['merchant']['name']} at {transaction['date']} from USD${usd_amount} to CAD${cad_amount}"
        )
        transaction_id = transaction["id"]
        if not dry_run:
            await mm.update_transaction(
                transaction_id, amount=cad_amount, notes=f"USD={usd_amount}"
            )
            await mm.set_transaction_tags(transaction_id, [USD2CAD_TAG])


async def convert_transactions_usd_to_cad(
    mm: MonarchMoney, account_id: str, dry_run: bool = False
) -> None:
    transactions = await get_unconverted_transactions(mm, account_id)
    sem = asyncio.Semaphore(THROUGHPUT)
    tasks = []
    for transaction_id, transaction in transactions.items():
        usd_amount = transaction["amount"]
        cad_amount = round(get_usd_cad_rate(transaction["date"]) * usd_amount, 2)
        tasks.append(
            asyncio.ensure_future(
                update_transaction_task(mm, transaction, cad_amount, usd_amount, sem)
            )
        )
    await asyncio.gather(*tasks)


async def get_checkpoint_transaction(
    mm: MonarchMoney, account_id: str
) -> Dict[str, Any]:
    transaction_response = await mm.get_transactions(
        account_ids=[account_id], tag_ids=[CHECKPOINT_TAG]
    )
    if (
        "allTransactions" in transaction_response
        and "results" in transaction_response["allTransactions"]
        and len(transaction_response["allTransactions"]["results"]) > 0
    ):
        return transaction_response["allTransactions"]["results"][0]
    else:
        response = await mm.create_transaction(
            date=datetime.today().strftime("%Y-%m-%d"),
            amount=0.0,
            account_id=account_id,
            merchant_name="python",
            category_id=CHECKPOINT_CATEGORY_ID,
        )
        transaction_id = response["createTransaction"]["transaction"]["id"]
        await mm.update_transaction(transaction_id, hide_from_reports=True)
        await mm.set_transaction_tags(transaction_id, tag_ids=[CHECKPOINT_TAG])
        return await get_checkpoint_transaction(mm, account_id)


async def convert_account_balance_history(
    mm: MonarchMoney, account_id: str, dry_run: bool = False
) -> bool:
    checkpoint = await get_checkpoint_transaction(mm, account_id)
    last_conversion_dt = (
        datetime.strptime(checkpoint["notes"], "%Y-%m-%d")
        if checkpoint["notes"]
        else None
    )
    if last_conversion_dt:
        print(
            f"resuming from last conversion date: {last_conversion_dt.strftime('%Y-%m-%d')}"
        )
    bal_history = await mm.get_account_history(account_id=account_id)
    new_bal_rows = []
    for bal_record in bal_history:
        cad_amount = get_usd_cad_rate(bal_record["date"]) * bal_record["signedBalance"]
        converted_bal = round(cad_amount, 2)
        bal_date = datetime.strptime(bal_record["date"], "%Y-%m-%d")
        if not last_conversion_dt:
            last_conversion_dt = bal_date - timedelta(days=1)
        if bal_date > last_conversion_dt:
            last_conversion_dt = bal_date
            new_bal_row = BalanceHistoryRow(
                date=bal_date,
                amount=converted_bal,
                account_name=bal_record["accountName"],
            )
            new_bal_rows.append(new_bal_row)
    print(f"converting {len(new_bal_rows)} balance records")
    if not dry_run and new_bal_rows:
        await mm.update_transaction(
            checkpoint["id"], notes=last_conversion_dt.strftime("%Y-%m-%d")
        )
        print(f"saving last conversion date: {last_conversion_dt.strftime('%Y-%m-%d')}")
        return await mm.upload_account_balance_history(account_id, new_bal_rows)


async def convert_currency():
    mm = MonarchMoney()
    mm.load_session()

    accounts = await mm.get_accounts()
    accounts = accounts["accounts"]
    account_id_to_name = {
        accounts["id"]: accounts["displayName"] for accounts in accounts
    }
    for account_id in TRANSACTION_ACCOUNTS_TO_CONVERT:
        print(
            f"CONVERTING account transactions for '{account_id_to_name[account_id]}' ({account_id})"
        )
        await convert_transactions_usd_to_cad(mm, account_id)
        print(
            f"CONVERTING account balance history for '{account_id_to_name[account_id]}' ({account_id})"
        )
        await convert_account_balance_history(mm, account_id)


asyncio.run(convert_currency())

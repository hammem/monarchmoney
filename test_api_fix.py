#!/usr/bin/env python3
"""
Verify the api.monarch.com domain fix.

Usage:
    MONARCH_TOKEN=<your_token> python test_api_fix.py
"""

import asyncio
import os
import sys
from monarchmoney import MonarchMoney, MonarchMoneyEndpoints

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"


def ok(label, detail=""):
    print(f"  {GREEN}PASS{RESET}  {label}" + (f"  ({detail})" if detail else ""))


def fail(label, detail=""):
    print(f"  {RED}FAIL{RESET}  {label}" + (f"  ({detail})" if detail else ""))


async def can_fetch_accounts(token: str, base_url: str) -> bool:
    MonarchMoneyEndpoints.BASE_URL = base_url
    try:
        await MonarchMoney(token=token).get_accounts()
        return True
    except Exception as e:
        if any(x in str(e) for x in ("525", "TransportServer", "TransportQuery")):
            return False
        raise


async def run_suite(token: str) -> int:
    MonarchMoneyEndpoints.BASE_URL = "https://api.monarch.com"
    mm = MonarchMoney(token=token)
    failures = 0

    for name, coro in [
        ("get_accounts()",             mm.get_accounts()),
        ("get_transactions(limit=5)",  mm.get_transactions(limit=5)),
        ("get_cashflow()",             mm.get_cashflow()),
        ("get_subscription_details()", mm.get_subscription_details()),
    ]:
        try:
            await coro
            ok(name)
        except Exception as e:
            fail(name, str(e)[:120])
            failures += 1

    return failures


def main():
    print(f"\n{BLUE}=== Monarch Money — api.monarch.com domain fix ==={RESET}\n")

    token = os.environ.get("MONARCH_TOKEN")
    if not token:
        fail("MONARCH_TOKEN env var not set")
        print("  Set it with:  export MONARCH_TOKEN=<your_token>\n")
        sys.exit(1)
    ok("Token loaded from MONARCH_TOKEN")

    print(f"\n{YELLOW}[1] Old domain — api.monarchmoney.com{RESET}")
    if asyncio.run(can_fetch_accounts(token, "https://api.monarchmoney.com")):
        fail("Expected 525, but old domain returned data")
    else:
        ok("api.monarchmoney.com returns 525 (dead)")

    print(f"\n{YELLOW}[2] New domain — api.monarch.com{RESET}")
    if not asyncio.run(can_fetch_accounts(token, "https://api.monarch.com")):
        fail("api.monarch.com failed unexpectedly")
        sys.exit(1)
    ok("api.monarch.com is reachable")

    print(f"\n{YELLOW}[3] Full API suite against api.monarch.com{RESET}")
    failures = asyncio.run(run_suite(token))

    print(f"\n{BLUE}=== Result ==={RESET}")
    if failures == 0:
        print(f"  {GREEN}All tests passed.{RESET}\n")
    else:
        print(f"  {RED}{failures} test(s) failed.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

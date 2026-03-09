#!/usr/bin/env python3
"""
Verify that patching MonarchMoneyEndpoints.BASE_URL to api.monarch.com works.

Demonstrates:
  - OLD domain (api.monarchmoney.com) is broken with Cloudflare 525
  - NEW domain (api.monarch.com) works correctly

Run: python test_api_fix.py
"""

import asyncio
import sys
import keyring
from monarchmoney import MonarchMoney, MonarchMoneyEndpoints

KEYRING_SERVICE = "com.mcp.monarch-mcp-server"
KEYRING_USERNAME = "monarch-token"

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def ok(label, detail=""):
    print(f"  {GREEN}PASS{RESET}  {label}" + (f"  ({detail})" if detail else ""))

def fail(label, detail=""):
    print(f"  {RED}FAIL{RESET}  {label}" + (f"  ({detail})" if detail else ""))

def info(msg):
    print(f"        {msg}")


async def test_domain(token: str, base_url: str) -> bool:
    MonarchMoneyEndpoints.BASE_URL = base_url
    mm = MonarchMoney(token=token)
    try:
        result = await mm.get_accounts()
        return True
    except Exception as e:
        msg = str(e)
        if "525" in msg or "TransportServer" in msg or "TransportQuery" in msg:
            return False
        raise


async def run_full_suite(token: str) -> int:
    MonarchMoneyEndpoints.BASE_URL = "https://api.monarch.com"
    mm = MonarchMoney(token=token)
    failures = 0

    tests = [
        ("get_accounts()",              lambda: mm.get_accounts()),
        ("get_transactions(limit=5)",   lambda: mm.get_transactions(limit=5)),
        ("get_cashflow()",              lambda: mm.get_cashflow()),
        ("get_subscription_details()",  lambda: mm.get_subscription_details()),
    ]

    for name, fn in tests:
        try:
            result = await fn()
            if name.startswith("get_accounts"):
                n = len(result.get("accounts", []))
                ok(name, f"{n} accounts")
            elif name.startswith("get_transactions"):
                n = len(result.get("allTransactions", {}).get("results", []))
                ok(name, f"{n} transactions")
            else:
                ok(name, "response received")
        except Exception as e:
            fail(name, str(e)[:120])
            failures += 1

    return failures


def main():
    print(f"\n{BLUE}=== Monarch Money API domain fix - verification ==={RESET}\n")

    # 1. Check token
    token = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if not token:
        fail("Token found in keyring", "not found - run login_setup.py first")
        sys.exit(1)
    ok("Token found in keyring", f"length {len(token)}")
    info(f"Library default URL:  {MonarchMoneyEndpoints.BASE_URL}")

    # 2. Demonstrate old domain is broken
    print(f"\n{YELLOW}[1] Old domain - api.monarchmoney.com{RESET}")
    old_works = asyncio.run(test_domain(token, "https://api.monarchmoney.com"))
    if old_works:
        fail("api.monarchmoney.com is broken", "unexpectedly returned data")
    else:
        ok("api.monarchmoney.com is broken", "Cloudflare 525 as expected")

    # 3. Demonstrate new domain works
    print(f"\n{YELLOW}[2] New domain - api.monarch.com{RESET}")
    new_works = asyncio.run(test_domain(token, "https://api.monarch.com"))
    if new_works:
        ok("api.monarch.com is reachable")
    else:
        fail("api.monarch.com failed unexpectedly")
        sys.exit(1)

    # 4. Run full API suite against new domain
    print(f"\n{YELLOW}[3] Full API suite against api.monarch.com{RESET}")
    failures = asyncio.run(run_full_suite(token))

    # 5. Summary
    print(f"\n{BLUE}=== Result ==={RESET}")
    if failures == 0:
        print(f"  {GREEN}All tests passed.{RESET} The domain fix works correctly.\n")
    else:
        print(f"  {RED}{failures} test(s) failed.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

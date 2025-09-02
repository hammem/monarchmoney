#!/usr/bin/env python3
"""
Extract operations from monarch.har
"""
import re

with open("monarch.har", "r") as f:
    content = f.read()

# Find all operationName entries
matches = re.findall(r'"operationName":"([^"]*)"', content)

operations = set(matches)
print("=== Operations found in monarch.har ===")
for op in sorted(operations):
    print(f"- {op}")

print(f"\n=== Analysis ===")
print(f"Total operations: {len(operations)}")

# Look for specific functionality
net_worth_ops = [
    op
    for op in operations
    if "net" in op.lower()
    or "worth" in op.lower()
    or "balance" in op.lower()
    or "snapshot" in op.lower()
]
bill_ops = [
    op for op in operations if "bill" in op.lower() or "recurring" in op.lower()
]
settings_ops = [
    op
    for op in operations
    if "setting" in op.lower()
    or "preference" in op.lower()
    or "household" in op.lower()
]
summary_ops = [
    op
    for op in operations
    if "summary" in op.lower() or "card" in op.lower() or "dashboard" in op.lower()
]

print(f"\nPotential replacements:")
if net_worth_ops:
    print(f"Net Worth/Balance ops: {net_worth_ops}")
if bill_ops:
    print(f"Bills/Recurring ops: {bill_ops}")
if settings_ops:
    print(f"Settings/Preferences ops: {settings_ops}")
if summary_ops:
    print(f"Summary/Dashboard ops: {summary_ops}")

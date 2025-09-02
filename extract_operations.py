#!/usr/bin/env python3
"""
Extract all unique operation names from HAR files
"""
import json
import glob
import re

operations = set()

for har_file in glob.glob("/Users/keith/src/monarchmoney-enhanced/*.har"):
    with open(har_file, "r") as f:
        content = f.read()

        # Find all operationName entries
        matches = re.findall(r'"operationName":"([^"]*)"', content)
        for match in matches:
            operations.add(match)

print("All real MonarchMoney operations found:")
for op in sorted(operations):
    print(f"- {op}")

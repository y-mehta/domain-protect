#!/usr/bin/env python
import json

from utils.aws import list_accounts, list_domains, publish_to_sns
from utils.dns import vulnerable_ns


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    json_data = {"Findings": []}

    accounts = list_accounts()

    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        domains = list_domains(account_id, account_name)

        for domain in domains:
            print(f"testing {domain} in {account_name} account")
            result = vulnerable_ns(domain)
            if result:
                print(f"{domain} in {account} is vulnerable")
                vulnerable_domains.append(domain)
                json_data["Findings"].append({"Account": account_name, "AccountID": str(account_id), "Domain": domain})

                if len(vulnerable_domains) == 0:
                    print(f"No registered domains found in {account_name} account")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Registered domains with missing hosted zones found in Amazon Route53")

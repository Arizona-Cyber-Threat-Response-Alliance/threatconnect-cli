import requests
import hmac
import hashlib
import base64
import os
import time
import logging
from colorama import Fore, Style, init
from datetime import datetime
import urllib.parse
import re

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve Access ID and Secret Key from environment variables
tc_accessid = os.getenv('tc_accessid')
tc_secretkey = os.getenv('tc_secretkey')

if not tc_accessid or not tc_secretkey:
    logging.error("Missing environment variables for Access ID or Secret Key")
    exit(1)

ioc_patterns = {
    "host": r"(?i)\b((?:(?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+(?!apk|apt|arpa|asp|bat|bdoda|bin|bsspx|cer|cfg|cgi|class|close|cpl|cpp|crl|css|dll|doc|docx|dyn|exe|fl|gz|hlp|htm|html|ico|ini|ioc|jar|jpg|js|jxr|lco|lnk|loader|log|lxdns|mdb|mp4|odt|pcap|pdb|pdf|php|plg|plist|png|ppt|pptx|quit|rar|rtf|scr|sleep|ssl|torproject|tmp|txt|vbp|vbs|w32|wav|xls|xlsx|xml|xpi|dat($|\r\n)|gif($|\r\n)|xn$)(?:xn--[a-zA-Z0-9]{2,22}|[a-zA-Z]{2,13}))(?!.*@)",
    "ipv4": r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    "email_address": r"(?i)[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])",
    "md5": r"\b([a-fA-F\d]{32})\b",
    "url": r"\b(?:(?:https?|s?ftp|tcp|file)://)(?:(?:\b(?=.{4,253})(?:(?:[a-z0-9_-]{1,63}\.){0,124}(?:(?!-)[-a-z0-9]{1,63}(?<!-)\.){0,125}(?![-0-9])[-a-z0-9]{2,24}(?<![-0-9]))\b|\b(?:(?:(?:[0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b)(?::(?:[1-9]|[1-8][0-9]|9[0-9]|[1-8][0-9]{2}|9[0-8][0-9]|99[0-9]|[1-8][0-9]{3}|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9]|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?\b)(?:/[-a-zA-Z0-9_.~%!$&'()*+,;=:@]*)*(?:\?[-a-zA-Z0-9_.~%!$&'()*+,;=:@/?]*#?)?(?:\#[-a-zA-Z0-9_.~%!$&'()*+,;=:@/?]+)?",
    "ipv6": r"(?<![a-zA-Z0-9:])(?:(?:(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4})|(?:(?=(?:[a-fA-F0-9]{0,4}:){0,7}[a-fA-F0-9]{0,4})(?:(?:[a-fA-F0-9]{1,4}:){1,7}|:)(?:(?::[a-fA-F0-9]{1,4}){1,7}|:)))(?![a-zA-Z0-9:])",
    "sha-1": r"\b([a-fA-F\d]{40})\b",
    "sha-256": r"\b([a-fA-F\d]{64})\b",
    "mutex": r"(?:Global\\|Local\\)?(?:\S| ){1,260}",
    "asn": r"[Aa][Ss][Nn][1-4]?\d{1,8}",
    "reg_key_value": r"(?=.{1,257}$)(?:(?:HKEY_CLASSES_ROOT|HKEY_CURRENT_CONFIG|HKEY_CURRENT_USER|HKEY_CURRENT_USER_LOCAL_SETTINGS|HKEY_LOCAL_MACHINE|HKEY_PERFORMANCE_DATA|HKEY_PERFORMANCE_NLSTEXT|HKEY_PERFORMANCE_TEXT|HKEY_USERS)(?:(?!\\\\.+)(?:\\.+))*)",
    "reg_key_value2": r".{0,214}",
    "user_agent": r"[A-Za-z0-9 /().,!""#$%&’*+-\;:<>=?@\[\]{}^_`|~]{1,256}",
    "email_subject": r".{1,100}",
}

def generate_auth_header(api_path, query_string, http_method, timestamp):
    message = f"{api_path}{query_string}:{http_method}:{timestamp}" if query_string else f"{api_path}:{http_method}:{timestamp}"
    signature = base64.b64encode(hmac.new(tc_secretkey.encode(), message.encode(), hashlib.sha256).digest()).decode()
    return f"TC {tc_accessid}:{signature}"

def determine_indicator_type(indicator):
    for ioc_type, pattern in ioc_patterns.items():
        if re.match(pattern, indicator, re.IGNORECASE):
            return ioc_type
    return "unknown"

def construct_tql_query(indicator_type: str, indicator: str) -> str:
    # Map your internal indicator types to the expected ThreatConnect API types
    type_mapping = {
        "ipv4": "Address",
        "host": "Host",
        "email_address": "EmailAddress",
        "url": "URL",
        "asn": "ASN",
        "cidr": "CIDR",
        "email_subject": "EmailSubject",
        "mutex": "Mutex",
        "registry_key": "Registry Key",
        "user_agent": "User Agent",
        # Add other mappings as necessary
    }
    api_indicator_type = type_mapping.get(indicator_type.lower(), "Unknown")

    # Construct the TQL query to filter by both type and summary
    tql_query = f'typeName in ("{api_indicator_type}") and summary in ("{indicator}")'
    return tql_query


def query_indicator_with_tql(indicator_type: str, indicator: str):
    try:
        # Ensure 'indicator' is defined and passed correctly to this function
        tql_query = construct_tql_query(indicator_type, indicator)
        encoded_tql = urllib.parse.quote(tql_query)
        api_path = '/api/v3/indicators'
        query_string = f'?tql={encoded_tql}'
        timestamp = str(int(time.time()))
        auth_header = generate_auth_header(api_path, query_string, 'GET', timestamp)
        headers = {
            'Timestamp': timestamp,
            'Authorization': auth_header,
            'Accept': 'application/json'
        }
        print("Please provide an instance name. Example: company.threatconnect.com")
        instance_name=input("Instance name: ")
        full_url = f'https://{instance_name}.threatconnect.com{api_path}{query_string}'
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(Fore.RED + f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
    except requests.exceptions.RequestException as req_err:
        print(Fore.RED + f"Request error occurred: {req_err}")
    except Exception as err:
        # If this line throws the error, ensure 'indicator' is correctly passed to the function
        print(Fore.RED + f"An unexpected error occurred: {err}")
    return None

def format_and_print_indicator_data(indicator_data):
    for indicator in indicator_data:
        # Assuming 'dateAdded', 'lastModified', etc., are the correct keys in your data
        date_added = indicator.get('dateAdded', 'N/A')
        last_modified = indicator.get('lastModified', 'N/A')
        summary = indicator.get('summary', 'N/A')
        # Convert date strings to datetime objects if they are not 'N/A'
        if date_added != 'N/A':
            date_added = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y %H:%M:%S")
        if last_modified != 'N/A':
            last_modified = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y %H:%M:%S")

        print(f"{Fore.RED}{Style.BRIGHT}Summary:{Style.RESET_ALL} {indicator.get('summary', 'N/A')}")
        print(f"{Fore.RED}{Style.BRIGHT}Date Added:{Style.RESET_ALL} {date_added}")
        print(f"{Fore.RED}{Style.BRIGHT}Last Modified:{Style.RESET_ALL} {last_modified}")
        print(f"{Fore.RED}{Style.BRIGHT}Type:{Style.RESET_ALL} {indicator.get('type', 'N/A')}")
        print(f"{Fore.RED}{Style.BRIGHT}Rating:{Style.RESET_ALL} {'💀' * int(indicator.get('rating', 0))} ({indicator.get('rating', 'N/A')}/5)")
        print(f"{Fore.RED}{Style.BRIGHT}Confidence:{Style.RESET_ALL} {indicator.get('confidence', 'N/A')}%")
        print(f"{Fore.RED}{Style.BRIGHT}Owner:{Style.RESET_ALL} {indicator.get('ownerName', 'N/A')}")
        print(f"{Fore.RED}{Style.BRIGHT}Active:{Style.RESET_ALL} {'Yes' if indicator.get('active', False) else 'No'}")
        print(f"{Fore.RED}{Style.BRIGHT}Web Link:{Style.RESET_ALL} {indicator.get('webLink', 'N/A')}")
        #if 'legacyLink' in indicator:
            # print(f"{Fore.RED}{Style.BRIGHT}Legacy Link:{Style.RESET_ALL} {indicator.get('legacyLink', 'N/A')}")
        if 'source' in indicator:
            print(f"{Fore.RED}{Style.BRIGHT}Source:{Style.RESET_ALL} {indicator.get('source', 'N/A')}")

        description = indicator.get('description', 'No description available.')
        print("\n" + f"{Fore.RED}{Style.BRIGHT}Description:{Style.RESET_ALL}\n{description}\n")

        print("-" * 40 + "\n")

def main():
    input_string = input("Enter indicators (separated by space, line, or comma): ")
    indicators = re.split(r'[,\n\s]+', input_string.strip())

    for indicator in indicators:
        if indicator:  # Ensure the indicator is not empty
            indicator_type = determine_indicator_type(indicator)
            print(Fore.YELLOW + f"Processing Indicator: {indicator}, Type: {indicator_type}")
            data = query_indicator_with_tql(indicator_type, indicator)  # Correctly pass 'indicator' here
            if data and 'data' in data and data['status'] == 'Success':
                format_and_print_indicator_data(data['data'])
            else:
                print(Fore.RED + "No data returned from the query or an error occurred.")

if __name__ == "__main__":
    main()

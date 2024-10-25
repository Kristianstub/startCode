import requests
import json
import sys

# Removed ipify import as per previous guidance

from platform import mac_ver, win32_ver, system

# Domeneshop API credentials
API_TOKEN = "heytDI6dBJVcUQHV"
API_SECRET = "ekNjmFzmJZ3Y9noTVvwavcKRo6NH3G5s09vDfeJhj9KpCOlKQsELruoTNuohFKNs"

# Your domain and hostname
DOMAIN = 'codexenmo.no'
HOSTNAME = 'gruppe10'  # Ensure this is a string

# Domeneshop API endpoints
BASE_URL = 'https://api.domeneshop.no/v0'

# Function to get the current public IP
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip = response.json().get('ip')
        if ip:
            return ip
        else:
            print("Could not retrieve IP from response.")
            sys.exit(1)
    except Exception as e:
        print(f"Error getting public IP: {e}")
        sys.exit(1)

# Function to get domain ID
def get_domain_id(session):
    response = session.get(f'{BASE_URL}/domains')
    response.raise_for_status()
    domains = response.json()
    for domain in domains:
        if domain['domain'] == DOMAIN:
            return domain['id']
    print(f"Domain {DOMAIN} not found.")
    sys.exit(1)

# Function to get DNS record ID
def get_record_id(session, domain_id):
    response = session.get(f'{BASE_URL}/domains/{domain_id}/dns')
    response.raise_for_status()
    records = response.json()
    for record in records:
        if record['host'] == HOSTNAME and record['type'] == 'A':
            return record['id']
    return None  # Record not found

# Function to create DNS record
def create_dns_record(session, domain_id, ip):
    data = {
        "host": HOSTNAME,
        "type": "A",
        "data": ip,
        "ttl": 300
    }
    response = session.post(
        f'{BASE_URL}/domains/{domain_id}/dns',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    response.raise_for_status()
    print(f"Created DNS record for {HOSTNAME}.{DOMAIN} with IP {ip}")

# Function to update DNS record
def update_dns_record(session, domain_id, record_id, ip):
    data = {
        "host": HOSTNAME,
        "type": "A",
        "data": ip,
        "ttl": 300
    }
    response = session.put(
        f'{BASE_URL}/domains/{domain_id}/dns/{record_id}',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    response.raise_for_status()
    print(f"Updated DNS record for {HOSTNAME}.{DOMAIN} to IP {ip}")

def main():
    # Create a session with basic auth
    session = requests.Session()
    session.auth = (API_TOKEN, API_SECRET)

    # Get current public IP
    current_ip = get_public_ip()

    try:
        # Get domain ID
        domain_id = get_domain_id(session)

        # Get record ID
        record_id = get_record_id(session, domain_id)

        if record_id:
            # Update existing DNS record
            update_dns_record(session, domain_id, record_id, current_ip)
        else:
            # Create a new DNS record
            create_dns_record(session, domain_id, current_ip)

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
        sys.exit(1)
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()

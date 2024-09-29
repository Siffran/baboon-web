# Extract data from Raid Helper API: https://raid-helper.dev/documentation/api
import requests

RAID_HELPER_EVENT_API_URL = "https://raid-helper.dev/api/v2/events/"

def fetch_all_raid_events(server_id, api_key):
    url = f"https://raid-helper.dev/api/v3/servers/{server_id}/events"
    headers = {
        'Authorization': f'{api_key}'
    }

    try:
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching events: {e}")
        return None

def fetch_event_details(event_id):
    """Fetch event data from the Raid-Helper API based on event ID."""
    url = f"https://raid-helper.dev/api/v2/events/{event_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    
        data = response.json()
        return data

    except requests.RequestException as e:
        print(f"Error fetching event data from Raid-Helper API: {e}")
        return None
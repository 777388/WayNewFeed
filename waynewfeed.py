import requests
import json
import hashlib
import time
import feedparser
from xml.etree import ElementTree

# Wayback Machine CDX API endpoint
CDX_API = "http://web.archive.org/cdx/search/cdx"

# List of URLs to query
QUERY_URLS = ["https://example.com", "https://example.org"]

# File to store the list of URLs and snapshots
DATA_FILE = "data.json"

# RSS feed file
RSS_FILE = "feed.xml"

# Polling interval (in seconds)
POLL_INTERVAL = 300

def fetch_data(url):
    # Fetch the data from the CDX API
    params = {
        'url': url,
        'output': 'json',
        'fl': 'timestamp,original'
    }
    response = requests.get(CDX_API, params=params)
    response.raise_for_status()

    # Parse the response and extract the URLs and snapshots
    data = []
    for row in json.loads(response.text):
        timestamp, url = row[:2]
        data.append((url, timestamp))

    return data

def hash_data(data):
    # Hash the list of URLs and snapshots to detect changes
    data_hash = hashlib.sha256(json.dumps(data).encode()).hexdigest()
    return data_hash

def load_data():
    # Load the previous data from the file
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_data(data):
    # Save the current data to the file
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def generate_feed(data):
    # Generate the RSS feed with the new entries
    feed = ElementTree.Element('rss', version='2.0')
    channel = ElementTree.SubElement(feed, 'channel')
    ElementTree.SubElement(channel, 'title').text = 'Wayback Machine'
    ElementTree.SubElement(channel, 'link').text = 'http://web.archive.org/'

    for url, timestamp in data:
        item = ElementTree.SubElement(channel, 'item')
        ElementTree.SubElement(item, 'title').text = url
        ElementTree.SubElement(item, 'link').text = f'http://web.archive.org/web/{timestamp}/{url}'
        ElementTree.SubElement(item, 'pubDate').text = time.strftime('%a, %d %b %Y %H:%M:%S %z', time.gmtime())

    return feed

def display_feed():
    # Parse and display the RSS feed in the terminal
    with open(RSS_FILE, 'r') as f:
        feed = feedparser.parse(f)
    for entry in feed.entries:
        print(f'{entry.published} - {entry.title} ({entry.link})')

if __name__ == '__main__':
    while True:
        # Fetch the data and hash it to detect changes
        data = {}
        for url in QUERY_URLS:
            data[url] = fetch_data(url)
        data_hash = hash_data(data)

        # Load the previous data and hash it
        prev_data = load_data()
        prev_data_hash = hash_data(prev_data)

        if data_hash != prev_data_hash:
    # Generate the RSS feed with the new entries
    new_data = {}
    for url in QUERY_URLS:
        prev_snapshots = prev_data.get(url, [])
        snapshots = data.get(url, [])

        new_snapshots = [snapshot for snapshot in snapshots if snapshot not in prev_snapshots]

        # Check if there are any new snapshots for the URL
        if new_snapshots:
            # Append the new snapshots to the previous data
            new_data[url] = prev_snapshots + new_snapshots
            print(f'New snapshots for {url}:')
            for snapshot in new_snapshots:
                print(f' - {snapshot[0]} ({snapshot[1]})')
        else:
            # Use the previous data if there are no new snapshots
            new_data[url] = prev_snapshots

    # Save the new data to the file
    save_data(new_data)

    # Generate and save the RSS feed
    feed = generate_feed(new_data)
    with open(RSS_FILE, 'w') as f:
        f.write(ElementTree.tostring(feed).decode())

    # Display the new entries in the terminal
    display_feed()

# Wait for the next poll interval
time.sleep(POLL_INTERVAL)


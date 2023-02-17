import requests
import hashlib
import time

def get_domain_urls(domain, start_timestamp):
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=timestamp,original&collapse=urlkey"

    response = requests.get(cdx_url)
    urls = []

    if response.status_code == 200:
        for i, entry in enumerate(response.json()):
            if i == 0:
                continue  # Skip the first entry

            timestamp = entry[0]
            if int(timestamp) >= start_timestamp:
                urls.append(entry[1])

    return urls

if __name__ == '__main__':
    domains = ['example.com', 'google.com', 'stackoverflow.com']
    sleep_time = 60  # seconds
    start_timestamp = int(time.time())

    print("Monitoring new URLs for the following domains:")
    print('\n'.join(domains))

    # Keep track of the URLs that have been seen
    seen_urls = set()

    # Keep track of whether it's the first run
    first_run = True

    while True:
        for domain in domains:
            urls = get_domain_urls(domain, start_timestamp)

            for url in urls:
                if url not in seen_urls:
                    if not first_run:
                        print(f"New URL found for {domain}: {url}")
                    seen_urls.add(url)

        # After the first run, set first_run to False
        first_run = False

        time.sleep(sleep_time)

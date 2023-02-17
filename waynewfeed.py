import requests
import hashlib
import time

def get_domain_urls(domain, start_timestamp):
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=timestamp,original&collapse=urlkey"

    response = requests.get(cdx_url)
    urls = []

    if response.status_code == 200:
        for entry in response.json():
            timestamp = entry[0]
            if int(timestamp) >= start_timestamp:
                urls.append(entry[1])

    return urls

if __name__ == '__main__':
    domains = ['example.com', 'google.com', 'facebook.com']
    sleep_time = 60  # seconds
    start_timestamp = int(time.time())

    print(f"Monitoring new URLs for {len(domains)} domains...")

    # Keep track of the URLs that have been seen for each domain
    seen_urls = {domain: set() for domain in domains}

    while True:
        for domain in domains:
            urls = get_domain_urls(domain, start_timestamp)

            for url in urls:
                if url not in seen_urls[domain]:
                    print(f"New URL found for {domain}: {url}")
                    seen_urls[domain].add(url)

        time.sleep(sleep_time)

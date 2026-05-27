import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_links_from_page(url, all_categorized_urls):
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LinkGraphBot/1.0)'
        })
        if resp.status_code != 200:
            return []
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, 'lxml')
    base_domain = urlparse(url).netloc

    # Remove nav, header, footer — only keep main content links
    for tag in soup.find_all(['nav', 'header', 'footer']):
        tag.decompose()

    content = soup.find('main') or soup.find('article') or soup.find('body')
    if not content:
        return []

    found_links = []
    for a_tag in content.find_all('a', href=True):
        href = a_tag['href'].strip()
        absolute = urljoin(url, href)
        parsed = urlparse(absolute)

        if parsed.netloc.replace('www.', '') != base_domain.replace('www.', ''):
            continue

        normalized = absolute.rstrip('/')
        if normalized in all_categorized_urls and normalized != url.rstrip('/'):
            found_links.append(normalized)

    return list(set(found_links))


def extract_all_links(categorized_urls):
    all_urls_set = set(
        url.rstrip('/')
        for pages in categorized_urls.values()
        for url in pages
    )

    all_pages = [url for pages in categorized_urls.values() for url in pages]
    links = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(extract_links_from_page, url, all_urls_set): url
            for url in all_pages
        }
        for future in as_completed(futures):
            source = futures[future]
            targets = future.result()
            for target in targets:
                links.append({'source': source.rstrip('/'), 'target': target})

    return links

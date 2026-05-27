PATTERNS = {
    'blog':      ['/blog/', '/blogs/', '/posts/', '/articles/', '/news/', '/insights/'],
    'features':  ['/features/', '/feature/'],
    'compare':   ['/compare/', '/vs/', '/alternative', '/alternatives/'],
    'solutions': ['/solutions/', '/solution/', '/use-case/', '/use-cases/'],
}

def categorize_urls(urls):
    categorized = {'blog': [], 'features': [], 'compare': [], 'solutions': []}

    for url in urls:
        url_lower = url.lower()
        for category, patterns in PATTERNS.items():
            if any(p in url_lower for p in patterns):
                categorized[category].append(url)
                break

    return categorized

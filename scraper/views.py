import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .utils.sitemap import fetch_sitemap
from .utils.categorizer import categorize_urls
from .utils.extractor import extract_all_links
from .utils.graph_builder import build_graph_data
from .utils.html_generator import generate_html


@csrf_exempt
@require_http_methods(['POST'])
def generate_view(request):
    try:
        body = json.loads(request.body)
        sitemap_url = body.get('sitemap_url', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    if not sitemap_url:
        return JsonResponse({'error': 'sitemap_url is required.'}, status=400)

    if not sitemap_url.startswith('http'):
        return JsonResponse({'error': 'sitemap_url must start with http or https.'}, status=400)

    try:
        urls = fetch_sitemap(sitemap_url)
        if not urls:
            return JsonResponse({'error': 'No URLs found in sitemap. Check the URL and try again.'}, status=400)

        categorized = categorize_urls(urls)
        total_categorized = sum(len(v) for v in categorized.values())
        if total_categorized == 0:
            return JsonResponse({'error': 'No blog, feature, compare, or solution pages found in sitemap.'}, status=400)

        links  = extract_all_links(categorized)
        graph  = build_graph_data(categorized, links)
        html   = generate_html(graph, sitemap_url)

        stats = {
            'total_pages': len(graph['nodes']),
            'total_links': len(graph['links']),
            'blogs':       len(categorized.get('blog', [])),
            'features':    len(categorized.get('features', [])),
            'compare':     len(categorized.get('compare', [])),
            'solutions':   len(categorized.get('solutions', [])),
        }

        return JsonResponse({'html': html, 'stats': stats})

    except Exception as e:
        return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)


@require_http_methods(['GET'])
def health_view(request):
    return JsonResponse({'status': 'ok'})

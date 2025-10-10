from math import floor

import requests
from django.conf import settings
from django.utils.translation import get_language
from django.views.generic import TemplateView


def get_page_links(pages_count, current_page, term):

    page_links = []

    if pages_count > 1:

        if current_page == 1:
            from_page = 1
            to_page = from_page + 7
        if current_page == pages_count + 1:
            pass
        else:
            from_page = current_page - 4
            to_page = current_page + 5

        if from_page < 1:
            from_page = 1

        if to_page > pages_count:
            to_page = pages_count

        for page in range(from_page, to_page + 1):
            page_link = "?q=%s&page=%s" % (term, page)

            page_links.append({
                'page': page,
                'url': page_link
            })

    return page_links


def get_prev_next_links(next_page_number, prev_page_number, term):
    next_link = None
    if next_page_number:
        next_link = "?q=%s&page=%s" % (term, next_page_number)

    prev_link = None
    if prev_page_number:
        prev_link = "?q=%s&page=%s" % (term, prev_page_number)

    return [prev_link, next_link]


def get_prev_next_page_number(pages_count, current_page):

    current_page = int(current_page)
    pages_count - int(pages_count)

    if current_page > 1:
        prev_page_number = current_page - 1
    else:
        prev_page_number = None

    if current_page < pages_count:
        next_page_number = current_page + 1
    else:
        next_page_number = None

    return [prev_page_number, next_page_number]


def get_total_pages(total_hits):
    pages_count = floor(total_hits / 10)

    modulo = total_hits % 10
    if modulo > 0:
        pages_count = pages_count + 1

    return pages_count


def get_api_re_path(term, current_page):
    base_url = settings.SITE_SEARCH_API_BASE_URL
    site_key = settings.SITE_SEARCH_SITE_KEY
    lang = get_language()

    return "%s%s?term=%s&lang=%s&page=%s" % (base_url, site_key, term, lang, current_page)


class SearchResult(TemplateView):

    template_name = "simplesitesearch/search_results.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # get Term from url params
        term = request.GET.get('q', None)
        honeypot_message = request.GET.get('message', None)

        # get current page from url params
        current_page = int(request.GET.get('page', 1))

        if term and not honeypot_message:

            term = ' '.join(term.split()[:10])

            # get api URl depending on current page
            api_url = get_api_re_path(term, current_page)

            # get results from api
            response = requests.get(api_url, verify=False)
            # convert results to usable json
            try:
                response_data = response.json()
            except:
                response_data = {
                    'total_hits': 0,
                    'hits': []
                }

            # get pages count
            pages_count = get_total_pages(response_data['total_hits'])

            # get prev and next page numbers
            prev_page_number, next_page_number = get_prev_next_page_number(pages_count, current_page)

            # get prev and next btn links
            prev_link, next_link = get_prev_next_links(next_page_number, prev_page_number, term)

            # get pages links
            page_links = get_page_links(pages_count, current_page, term)

            context.update({
                'pages_count': pages_count,
                'current_page': current_page,
                'results_count': response_data['total_hits'],
                'prev_link': prev_link,
                'next_link': next_link,
                'page_links': page_links,
                'results': response_data['hits']
            })
        else:
            context.update({
                'results': None
            })

        context.update({
            'query': term
        })

        return self.render_to_response(context)

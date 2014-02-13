# Note: These views are viewable only by people in the analyzers
# group. They should all have the analyzer_required decorator.
#
# Also, because we have this weird thing with new users,
# they should also have the check_new_user decorator.
#
# Thus each view should be structured like this:
#
#    @check_new_user
#    @analyzer_required
#    def my_view(request):
#        ...
#
# Also, since it's just analyzers, everyone is expected to speak
# English. Ergo, there's no localization here.

from collections import defaultdict
from datetime import datetime, timedelta

from elasticutils.contrib.django import F, es_required_or_50x

from django.shortcuts import render

from fjord.analytics.forms import OccurrencesComparisonForm
from fjord.analytics.tools import (
    generate_query_parsed,
    counts_to_options)
from fjord.base.helpers import locale_name
from fjord.base.util import (
    analyzer_required,
    check_new_user,
    smart_int,
    smart_date)
from fjord.feedback.models import Product, Response, ResponseMappingType


@check_new_user
@analyzer_required
def analytics_dashboard(request):
    """Main page for analytics related things"""
    template = 'analytics/analyzer/dashboard.html'
    return render(request, template)


@check_new_user
@analyzer_required
def analytics_products(request):
    """Products list view"""
    template = 'analytics/analyzer/products.html'
    products = Product.objects.all()
    return render(request, template, {
        'products': products
    })


@check_new_user
@analyzer_required
@es_required_or_50x(error_template='analytics/es_down.html')
def analytics_occurrences(request):
    template = 'analytics/analyzer/occurrences.html'

    first_facet_bi = None
    first_params = {}
    first_facet_total = 0

    second_facet_bi = None
    second_params = {}
    second_facet_total = 0

    if 'product' in request.GET:
        form = OccurrencesComparisonForm(request.GET)
        if form.is_valid():
            cleaned = form.cleaned_data

            # First item
            first_resp_s = (ResponseMappingType.search()
                            .filter(product=cleaned['product'])
                            .filter(locale__startswith='en'))

            first_params['product'] = cleaned['product']

            if cleaned['first_version']:
                first_resp_s = first_resp_s.filter(
                    version=cleaned['first_version'])
                first_params['version'] = cleaned['first_version']
            if cleaned['first_start_date']:
                first_resp_s = first_resp_s.filter(
                    created__gte=cleaned['first_start_date'])
                first_params['date_start'] = cleaned['first_start_date']
            if cleaned['first_end_date']:
                first_resp_s = first_resp_s.filter(
                    created__lte=cleaned['first_end_date'])
                first_params['date_end'] = cleaned['first_end_date']
            if cleaned['first_search_term']:
                first_resp_s = first_resp_s.query(
                    description__text=cleaned['first_search_term'])
                first_params['q'] = cleaned['first_search_term']

            if ('date_start' not in first_params
                and 'date_end' not in first_params):

                # FIXME - If there's no start date, then we want
                # "everything" so we use a hard-coded 2013-01-01 date
                # here to hack that.
                #
                # Better way might be to change the dashboard to allow
                # for an "infinite" range, but there's no other use
                # case for that and the ranges are done in the ui--not
                # in the backend.
                first_params['date_start'] = '2013-01-01'

            # Have to do raw because we want a size > 10.
            first_resp_s = first_resp_s.facet_raw(
                description_bigrams={
                    'terms': {
                        'field': 'description_bigrams',
                        'size': '30',
                    },
                    'facet_filter': first_resp_s._build_query()['filter']
                }
            )
            first_resp_s = first_resp_s[0:0]

            first_facet_total = first_resp_s.count()
            first_facet = first_resp_s.facet_counts()

            first_facet_bi = first_facet['description_bigrams']
            first_facet_bi = sorted(
                first_facet_bi, key=lambda item: -item['count'])

            if (cleaned['second_version']
                or cleaned['second_search_term']
                or cleaned['second_start_date']):

                second_resp_s = (ResponseMappingType.search()
                                .filter(product=cleaned['product'])
                                .filter(locale__startswith='en'))

                second_params['product'] = cleaned['product']

                if cleaned['second_version']:
                    second_resp_s = second_resp_s.filter(
                        version=cleaned['second_version'])
                    second_params['version'] = cleaned['second_version']
                if cleaned['second_start_date']:
                    second_resp_s = second_resp_s.filter(
                        created__gte=cleaned['second_start_date'])
                    second_params['date_start'] = cleaned['second_start_date']
                if cleaned['second_end_date']:
                    second_resp_s = second_resp_s.filter(
                        created__lte=cleaned['second_end_date'])
                    second_params['date_end'] = cleaned['second_end_date']
                if form.cleaned_data['second_search_term']:
                    second_resp_s = second_resp_s.query(
                        description__text=cleaned['second_search_term'])
                    second_params['q'] = cleaned['second_search_term']

                if ('date_start' not in second_params
                    and 'date_end' not in second_params):

                    # FIXME - If there's no start date, then we want
                    # "everything" so we use a hard-coded 2013-01-01 date
                    # here to hack that.
                    #
                    # Better way might be to change the dashboard to allow
                    # for an "infinite" range, but there's no other use
                    # case for that and the ranges are done in the ui--not
                    # in the backend.
                    second_params['date_start'] = '2013-01-01'

                # Have to do raw because we want a size > 10.
                second_resp_s = second_resp_s.facet_raw(
                    description_bigrams={
                        'terms': {
                            'field': 'description_bigrams',
                            'size': '30',
                        },
                        'facet_filter': second_resp_s._build_query()['filter']
                    }
                )
                second_resp_s = second_resp_s[0:0]

                second_facet_total = second_resp_s.count()
                second_facet = second_resp_s.facet_counts()

                second_facet_bi = second_facet['description_bigrams']
                second_facet_bi = sorted(
                    second_facet_bi, key=lambda item: -item['count'])

        permalink = request.build_absolute_uri()

    else:
        permalink = ''
        form = OccurrencesComparisonForm()

    # FIXME - We have responses that have no product set. This ignores
    # those. That's probably the right thing to do for the Occurrences Report
    # but maybe not.
    products = [prod for prod in ResponseMappingType.get_products() if prod]

    return render(request, template, {
        'permalink': permalink,
        'form': form,
        'products': products,
        'first_facet_bi': first_facet_bi,
        'first_params': first_params,
        'first_facet_total': first_facet_total,
        'first_normalization': round(first_facet_total * 1.0 / 1000, 3),
        'second_facet_bi': second_facet_bi,
        'second_params': second_params,
        'second_facet_total': second_facet_total,
        'second_normalization': round(second_facet_total * 1.0 / 1000, 3),
        'render_time': datetime.now(),
    })


@check_new_user
@analyzer_required
@es_required_or_50x(error_template='analytics/es_down.html')
def analytics_duplicates(request):
    """Shows all duplicate descriptions over the last n days"""
    template = 'analytics/analyzer/duplicates.html'

    n = 14

    responses = (ResponseMappingType.search()
                 .filter(created__gte=datetime.now() - timedelta(days=n))
                 .values_dict('description', 'happy', 'created', 'locale',
                              'user_agent', 'id')
                 .order_by('created').all())

    total_count = len(responses)

    response_dupes = {}
    for resp in responses:
        response_dupes.setdefault(resp['description'], []).append(resp)

    response_dupes = [
        (key, val) for key, val in response_dupes.items()
        if len(val) > 1
    ]

    # convert the dict into a list of tuples sorted by the number of
    # responses per tuple largest number first
    response_dupes = sorted(response_dupes, key=lambda item: len(item[1]) * -1)

    # duplicate_count -> count
    # i.e. "how many responses had 2 duplicates?"
    summary_counts = defaultdict(int)
    for desc, responses in response_dupes:
        summary_counts[len(responses)] = summary_counts[len(responses)] + 1
    summary_counts = sorted(summary_counts.items(), key=lambda item: item[0])

    return render(request, template, {
        'n': 14,
        'response_dupes': response_dupes,
        'render_time': datetime.now(),
        'summary_counts': summary_counts,
        'total_count': total_count,
    })


@check_new_user
@analyzer_required
@es_required_or_50x(error_template='analytics/es_down.html')
def analytics_search(request):
    template = 'analytics/analyzer/search.html'

    page = smart_int(request.GET.get('page', 1), 1)

    # Note: If we add additional querystring fields, we need to add
    # them to generate_dashboard_url.
    search_happy = request.GET.get('happy', None)
    search_platform = request.GET.get('platform', None)
    search_locale = request.GET.get('locale', None)
    search_product = request.GET.get('product', None)
    search_version = request.GET.get('version', None)
    search_query = request.GET.get('q', None)
    search_date_start = smart_date(
        request.GET.get('date_start', None), fallback=None)
    search_date_end = smart_date(
        request.GET.get('date_end', None), fallback=None)
    search_bigram = request.GET.get('bigram', None)
    selected = request.GET.get('selected', None)

    filter_data = []
    current_search = {'page': page}

    search = ResponseMappingType.search()
    f = F()
    # If search happy is '0' or '1', set it to False or True, respectively.
    search_happy = {'0': False, '1': True}.get(search_happy, None)
    if search_happy in [False, True]:
        f &= F(happy=search_happy)
        current_search['happy'] = int(search_happy)

    def unknown_to_empty(text):
        """Convert "Unknown" to "" to support old links"""
        return u'' if text.lower() == u'unknown' else text

    if search_platform is not None:
        f &= F(platform=unknown_to_empty(search_platform))
        current_search['platform'] = search_platform
    if search_locale is not None:
        f &= F(locale=unknown_to_empty(search_locale))
        current_search['locale'] = search_locale
    if search_product is not None:
        f &= F(product=unknown_to_empty(search_product))
        current_search['product'] = search_product

        if search_version is not None:
            # Note: We only filter on version if we're filtering on
            # product.
            f &= F(version=unknown_to_empty(search_version))
            current_search['version'] = search_version

    if search_date_start is None and search_date_end is None:
        selected = '7d'

    if search_date_end is None:
        search_date_end = datetime.now()
    if search_date_start is None:
        search_date_start = search_date_end - timedelta(days=7)

    current_search['date_end'] = search_date_end.strftime('%Y-%m-%d')
    # Add one day, so that the search range includes the entire day.
    end = search_date_end + timedelta(days=1)
    # Note 'less than', not 'less than or equal', because of the added
    # day above.
    f &= F(created__lt=end)

    current_search['date_start'] = search_date_start.strftime('%Y-%m-%d')
    f &= F(created__gte=search_date_start)

    if search_query:
        current_search['q'] = search_query
        es_query = generate_query_parsed('description', search_query)
        search = search.query_raw(es_query)

    if search_bigram is not None:
        f &= F(description_bigrams=search_bigram)
        filter_data.append({
            'display': 'Bigram',
            'name': 'bigram',
            'options': [{
                'count': 'all',
                'name': search_bigram,
                'display': search_bigram,
                'value': search_bigram,
                'checked': True
            }]
        })

    search = search.filter(f).order_by('-created')

    # FIXME - Links to output formats here

    # Search results and pagination
    if page < 1:
        page = 1
    page_count = 50
    start = page_count * (page - 1)
    end = start + page_count

    search_count = search.count()
    opinion_page_ids = [mem[0] for mem in search.values_list('id')[start:end]]

    # We convert what we get back from ES to what's in the db so we
    # can get all the information.
    opinion_page = Response.objects.filter(id__in=opinion_page_ids)

    # Navigation facet data
    facets = search.facet(
        'happy', 'platform', 'locale', 'product', 'version',
        filtered=bool(search._process_filters(f.filters)))

    # This loop does two things. First it maps 'T' -> True and 'F' ->
    # False.  This is probably something EU should be doing for
    # us. Second, it restructures the data into a more convenient
    # form.
    counts = {
        'happy': {},
        'platform': {},
        'locale': {},
        'product': {},
        'version': {}
    }
    for param, terms in facets.facet_counts().items():
        for term in terms:
            name = term['term']
            if name == 'T':
                name = True
            elif name == 'F':
                name = False

            counts[param][name] = term['count']

    def empty_to_unknown(text):
        return 'Unknown' if text == u'' else text

    filter_data.extend([
        counts_to_options(
            counts['happy'].items(),
            name='happy',
            display='Sentiment',
            display_map={True: 'Happy', False: 'Sad'},
            value_map={True: 1, False: 0},
            checked=search_happy),
        counts_to_options(
            counts['product'].items(),
            name='product',
            display='Product',
            display_map=empty_to_unknown,
            checked=search_product)
    ])
    # Only show the version if we're showing a specific
    # product.
    if search_product:
        filter_data.append(
            counts_to_options(
                counts['version'].items(),
                name='version',
                display='Version',
                display_map=empty_to_unknown,
                checked=search_version)
        )

    filter_data.extend(
        [
            counts_to_options(
                counts['platform'].items(),
                name='platform',
                display='Platform',
                display_map=empty_to_unknown,
                checked=search_platform),
            counts_to_options(
                counts['locale'].items(),
                name='locale',
                display='Locale',
                checked=search_locale,
                display_map=locale_name),
        ]
    )

    return render(request, template, {
        'opinions': opinion_page,
        'opinion_count': search_count,
        'filter_data': filter_data,
        'page': page,
        'prev_page': page - 1 if start > 0 else None,
        'next_page': page + 1 if end < search_count else None,
        'current_search': current_search,
        'selected': selected,
    })
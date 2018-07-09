#!/usr/bin/env python

import os
import inspect
import scrapy
import scrapy.crawler
import scrapy.exporters
import re
import argparse
import logging
import fnmatch
import json
import csv


# ---------- Utilities ----------

def split_url(url):
    match = re.search(r'^(?P<base>.*)\?(?P<params>.*)$', url, flags=re.I)
    return (
        match.group('base'),
        {k: v for (k, v) in (p.split('=') for p in match.group('params').split('&'))}
    )

def join_url(base, params):
    return "{base}?{params}".format(
        base=base,
        params='&'.join('%s=%s' % (k, v) for (k, v) in params.items()),
    )


# ---------- Scraper Spiders ----------

class BunningsProductSpider(scrapy.Spider):

    def parse(self, response):
        """Parse pagenated list of products"""

        # Check if page is out of range
        no_more_products = re.search(
            r'No matching products were found',
            response.css('div.paged-results').extract_first(),
            flags=re.I
        )
        if no_more_products:
            pass  # no more pages to populate, stop scraping

        else:
            # Scrape products list
            for product in response.css('article.product-list__item'):
                product_url = product.css('a::attr("href")').extract_first()
                yield response.follow(product_url, self.parse_detail)

            (base, params) = split_url(response.url)
            params.update({'page': int(params.get('page', '1')) + 1})
            next_page_url = join_url(base, params)
            self.logger.info(next_page_url)
            yield response.follow(next_page_url, self.parse)

    def parse_detail(self, response):
        """Parse individual product's detail"""
        # Product Information (a start)
        product_data = {
            'url': response.url,
            'name': response.css('div.page-title h1::text').extract_first(),
        }

        # Inventory Number
        inventory_number = re.search(
            r'(?P<inv_num>\d+)$',
            response.css('span.product-in::text').extract_first(),
        ).group('inv_num')
        product_data.update({'in': inventory_number})

        # Specifications (arbitrary key:value pairs)
        specs_table = response.css('#tab-specs dl')
        for row in specs_table.css('div.spec-row'):
            keys = row.css('dt::text').extract()
            values = row.css('dd::text').extract()
            product_data.update({
                key: value
                for (key, value) in zip(keys, values)
            })

        self.logger.info(product_data['name'])
        yield product_data

class ScrewSpider(BunningsProductSpider):
    name = 'screws'
    start_urls = [
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/decking?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/batten?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/wood?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/metal-fix?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/chipboard?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/treated-pine?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/plasterboard?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/roofing?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/screws/general-purpose?page=1',
    ]

class BoltSpider(BunningsProductSpider):
    name = 'bolts'
    start_urls = [
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/bolts/cup-head-bolts?page=1',
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/bolts/hex-head-bolts?page=1',
    ]

class NutSpider(BunningsProductSpider):
    name = 'nuts'
    start_urls = [
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/bolts/nuts?page=1',
    ]

class ThreadedRodSpider(BunningsProductSpider):
    name = 'threaded-rods'
    start_urls = [
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/bolts/threaded-rod?page=1',
    ]

class WasherSpider(BunningsProductSpider):
    name = 'washers'
    start_urls = [
        'https://www.bunnings.com.au/our-range/building-hardware/fixings-fasteners/bolts/washers?page=1',
    ]

SPIDERS = [
    ScrewSpider,
    BoltSpider,
    NutSpider,
    ThreadedRodSpider,
    WasherSpider,
]
SPIDER_MAP = {
    cls.name: cls
    for cls in SPIDERS
}

# ---------- Command-line Arguments Parser ----------
DEFAULT_PREFIX = os.path.splitext(os.path.basename(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
))[0] + '-'

parser = argparse.ArgumentParser(
    description='Build Bunnings catalogue by crawling their website',
    epilog="""
WORK IN PROGRESS
    At this time, this script will scrape the Bunnings website for fasteners,
    however it will not create a catalogue.
    This is because there is not enough information on the website to accurately
    determine fastener geometry.

Actions:
    scrape  scrape product details from website
    csv     convert scraped output to csv [optional]
    build   builds catalogue from scraped data

Note: Actions will always be performed in the order shown above,
      even if they're not listed in that order on commandline.
    """,
    formatter_class=argparse.RawTextHelpFormatter,
)

VALID_ACTIONS = set(['scrape', 'csv', 'build'])
def action_type(value):
    value = value.lower()
    if value not in VALID_ACTIONS:
        raise argparse.ArgumentError()
    return value

parser.add_argument(
    'actions', metavar='action', type=action_type, nargs='*',
    help='action(s) to perform'
)

# Scraper arguments
parser.add_argument(
    '--prefix', '-p', dest='prefix', default=DEFAULT_PREFIX,
    help="scraper file prefix (default: '%s')" % DEFAULT_PREFIX,
)

# Catalogues
parser.add_argument(
    '--list', '-l', dest='list',
    default=False, action='store_const', const=True,
    help="list catalogues to build",
)

def catalogues_list_type(value):
    catalogues_all = set(SPIDER_MAP.keys())
    catalogues = set()
    for filter_str in value.split(','):
        catalogues |= set(fnmatch.filter(catalogues_all, filter_str))
    return sorted(catalogues)

parser.add_argument(
    '--catalogues', '-c', dest='catalogues',
    type=catalogues_list_type, default=catalogues_list_type('*'),
    help="csv list of catalogues to act on",
)

args = parser.parse_args()

BunningsProductSpider.prefix = args.prefix

# list catalogues & exit
if args.list:
    for name in args.catalogues:
        print(name)
    exit(0)

# no actions, print help & exit
if not args.actions:
    parser.print_help()
    exit(1)


FEED_URI = "%(prefix)sscrape-%(name)s.json"

# ----- Start Crawl -----

if 'scrape' in args.actions:
    print("----- Scrape: %s" % (', '.join(args.catalogues)))


    # Clear feed files
    for name in args.catalogues:
        feed_filename = FEED_URI % {
            'prefix': args.prefix, 'name': name,
        }
        if os.path.exists(feed_filename):
            os.unlink(feed_filename)  # remove feed file to populate from scratch

    # Create Crawlers
    process = scrapy.crawler.CrawlerProcess(
        settings={
            'LOG_LEVEL': logging.INFO,
            'FEED_FORMAT': "json",
            'FEED_URI': FEED_URI,
        },
    )

    for name in args.catalogues:
        process.crawl(SPIDER_MAP[name])

    # Start Scraping
    process.start()


# ----- Convert to CSV -----

if 'csv' in args.actions:
    for name in args.catalogues:
        print("----- CSV: %s" % name)
        feed_json = FEED_URI % {
            'prefix': args.prefix, 'name': name,
        }
        with open(feed_json, 'r') as json_file:
            data = json.load(json_file)

        # Pull out headers
        headers = set()
        for item in data:
            headers |= set(item.keys())

        # Write Output
        def utf8encoded(d):
            return {k.encode('utf-8'): v.encode('utf-8') for (k, v) in d.items()}
        feed_csv = "%s.csv" % os.path.splitext(feed_json)[0]
        with open(feed_csv, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for item in data:
                writer.writerow(utf8encoded(item))


# ----- Build Catalogues -----

def build_screw(row):

    # Required Parameters:
    #   - drive
    #       -
    #   - head
    #       - <countersunk>
    #       - <>
    #   - thread <triangular>
    #       - diameter
    #       - diameter_core (defaults to 2/3 diameter)
    #       - pitch
    #       - angle (defaults to 30deg)
    #   - length
    #   - neck_diam
    #   - neck_length
    #   - neck_taper
    #   - tip_diameter
    #   - tip_length

    pass


if 'build' in args.actions:
    print("BUILD ACTION NOT IMPLEMENTED")
    print('\n'.join([
        "The information on conventional commercial web-pages is too iratic and",
        "innacurate to formulate a quality catalogue.",
        "At the time of writing this, I've abandoned this idea, (at least for the",
        "bunnings.com.au website anyway)"
    ]) + '\n')
    raise NotImplementedError("'build' action")

    #for name in args.catalogues:
    #    print("----- Build: %s" % name)

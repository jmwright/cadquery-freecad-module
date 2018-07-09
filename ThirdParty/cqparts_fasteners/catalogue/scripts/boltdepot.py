#!/usr/bin/env python

import os
import sys
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
import itertools
import six
import progressbar

# cqparts
import cqparts

# cqparts_fasteners
import cqparts_fasteners
import cqparts_fasteners.screws
import cqparts_fasteners.bolts
import cqparts_fasteners.nuts
import cqparts_fasteners.solidtypes
from cqparts_fasteners.solidtypes.fastener_heads import find as find_head
from cqparts_fasteners.solidtypes.screw_drives import find as find_drive
from cqparts_fasteners.solidtypes.threads import find as find_thread

# ---------- Constants ----------
STORE_NAME = 'BoltDepot'
STORE_URL = 'https://www.boltdepot.com'


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


def utf8encoded(d):
    return {k.encode('utf-8'): v.encode('utf-8') for (k, v) in d.items()}


def us2mm(value):
    if isinstance(value, six.string_types):
        # valid string formats include:
        #   1-3/4", 1/2", -5/9", 17/64", 1", 0.34", .34", 6ft
        match = re.search(
            r'''^
                (?P<neg>-)?
                (?P<whole>(\d+)?(\.\d+)?)??
                -?
                ((?P<numerator>\d+)/(?P<denominator>\d+))?
                \s*(?P<unit>("|ft))
            $''',
            value,
            flags=re.MULTILINE | re.VERBOSE,
        )
        # calculate value (as decimal quantity)
        value = float(match.group('whole') or 0) + (
            float(match.group('numerator') or 0) / \
            float(match.group('denominator') or 1)
        )
        if match.group('neg'):
            value *= -1

        if match.group('unit') == 'ft':
            value *= 12

    else:
        # numeric value given:
        # assumption: value given in inches
        pass

    return value * 25.4


def mm2mm(value):
    if isinstance(value, six.string_types):
        # valid string formats include:
        #   1mm, -4mm, -0.3mm, -.3mm, 1m
        match = re.search(r'^(?P<value>[\-0-9\.]+)\s*(?P<unit>(mm|m|))$', value.lower())
        value = float(match.group('value'))
        if match.group('unit') == 'm':
            value *= 1000
    return float(value)


UNIT_FUNC_MAP = {
    'metric': mm2mm,
    'us': us2mm,
}

def unit2mm(value, unit):
    unit = unit.strip().lower()
    if unit in UNIT_FUNC_MAP:
        return UNIT_FUNC_MAP[unit](value)
    else:
        raise ValueError("invalid unit: %r" % unit)



# ---------- Scraper Spiders ----------

class BoltDepotSpider(scrapy.Spider):
    prefix = ''  # no prefix by default
    name = None  # no name, should raise exception if not set

    FEED_URI = "%(prefix)sscrape-%(name)s.json"

    @classmethod
    def get_feed_uri(cls):
        return cls.FEED_URI % {k: getattr(cls, k) for k in dir(cls)}

    @classmethod
    def get_data(cls):
        if not hasattr(cls, '_data'):
            with open(cls.get_feed_uri(), 'r') as fh:
                setattr(cls, '_data', json.load(fh))
        return cls._data

    @classmethod
    def get_data_item(cls, key, criteria=lambda i: True, cast=lambda v: v):
        # utility function to get data out of a json dict list easily
        valid_data = []
        for item in cls.get_data():
            if criteria(item):
                try:
                    valid_data.append(cast(item[key]))
                except AttributeError:
                    raise ValueError("%r value %r invalid (cannot be cast)" % (key, item[key]))

        assert len(valid_data) == 1, "%r" % valid_data
        return valid_data[0]


class BoltDepotProductSpider(BoltDepotSpider):

    # criteria added to every cqparts.catalogue.JSONCatalogue entry
    common_catalogue_criteria = {
        'store': STORE_NAME,
        'store_url': STORE_URL,
    }

    def parse(self, response):
        # Look for : Product catalogue table
        product_catalogue = response.css('table.product-catalog-table')
        if product_catalogue:
            for catalogue_link in product_catalogue.css('li a'):
                next_page_url = catalogue_link.css('::attr("href")').extract_first()
                yield response.follow(next_page_url, self.parse)

        # Look for : Product list table
        product_list = response.css('#product-list-table')
        if product_list:
            for product in product_list.css('td.cell-prod-no'):
                next_page_url = product.css('a::attr("href")').extract_first()
                yield response.follow(next_page_url, self.parse_product_detail)

    def parse_product_detail(self, response):
        heading = response.css('#catalog-header-title h1::text').extract_first()
        print("Product: %s" % heading)
        sys.stdout.flush()

        (url_base, url_params) = split_url(response.url)

        # details table
        detail_table = response.css('#product-property-list')
        details = {}
        for row in detail_table.css('tr'):
            key = row.css('td.name span::text').extract_first()
            value = row.css('td.value span::text').extract_first()
            if key and value:
                (key, value) = (key.strip('\n\r\t '), value.strip('\n\r\t '))
                if key and value:
                    details[key] = value

        product_data = {
            'id': url_params['product'],
            'name': heading,
            'url': response.url,
            'details': details,
        }

        # Image url
        image_url = response.css('.catalog-header-product-image::attr("src")').extract_first()
        if image_url:
            product_data.update({'image_url': image_url})

        yield product_data

    # --- cqparts catalogue building specific functions
    # These functions are kept with the spider as a means to encapsulate
    # component-specific logic.

    @classmethod
    def add_to_catalogue(cls, data, catalogue):
        criteria = cls.item_criteria(data)
        criteria.update(cls.common_catalogue_criteria)
        criteria.update({'scraperclass': cls.__name__})
        catalogue.add(
            id=data['id'],
            obj=cls.build_component(data),
            criteria=criteria,
            _check_id=False,
        )

    @classmethod
    def item_criteria(cls, data):
        return {}  # should be overridden

    @classmethod
    def build_component(cls, data):
        from cqparts_misc.basic.primatives import Cube
        return Cube()  # should be overridden

    CATALOGUE_URI = "%(prefix)s%(name)s.json"
    CATALOGUE_CLASS = cqparts.catalogue.JSONCatalogue

    @classmethod
    def get_catalogue_uri(cls):
        filename = cls.CATALOGUE_URI % {k: getattr(cls, k) for k in dir(cls)}
        return os.path.join('..', filename)

    @classmethod
    def get_catalogue(cls, **kwargs):
        return cls.CATALOGUE_CLASS(cls.get_catalogue_uri(), **kwargs)

    @classmethod
    def get_item_str(cls, data):
        return "[%(id)s] %(name)s" % data


class WoodScrewSpider(BoltDepotProductSpider):
    name = 'woodscrews'
    start_urls = [
        'https://www.boltdepot.com/Wood_screws_Phillips_flat_head.aspx',
        'https://www.boltdepot.com/Wood_screws_Slotted_flat_head.aspx',
    ]

    @classmethod
    def item_criteria(cls, data):
        criteria = {
            'name': data['name'],
            'url': data['url'],
        }
        criteria_content = [  # (<key>, <header>), ...
            ('units', 'Units:'),
            ('diameter', 'Diameter:'),
            ('material', 'Material:'),
            ('plating', 'Plating:'),
        ]
        for (key, header) in criteria_content:
            value = data['details'].get(header, None)
            if value is not None:
                criteria[key] = value.lower()
        return criteria

    @classmethod
    def build_component(cls, data):
        details = data['details']

        # --- Head
        head = None
        if details['Head style:'] == 'Flat':  # countersunk
            head_diam = (  # averaged min/max
                unit2mm(details['Head diameter Min:'], details['Units:']) + \
                unit2mm(details['Head diameter Max:'], details['Units:'])
            ) / 2

            head = find_head(name='countersunk')(
                diameter=head_diam,
                bugle=False,
                raised=0,
                # TODO: details['Head angle:'] usually 82deg
            )

        else:
            raise ValueError("head style %r not supported" % details['Head style:'])

        # --- Drive
        drive = None
        if details['Drive type:'] == 'Phillips':
            # FIXME: use actual drive sizes from DataPhillipsDriveSizes to shape
            drive = find_drive(name='phillips')(
                diameter=head_diam * 0.6
            )

        elif details['Drive type:'] == 'Slotted':
            drive = find_drive(name='slot')(
                diameter=head_diam,
            )

        else:
            raise ValueError("drive type %r not supported" % details['Drive type:'])

        # --- Thread
        # Accuracy is Questionable:
        #   Exact screw thread specs are very difficult to find, so some
        #   of this is simply observed from screws I've salvaged / bought.
        thread_diam = DataWoodScrewDiam.get_data_item(
            'Decimal',
            criteria=lambda i: i['Size'] == details['Diameter:'],
            cast=lambda v: unit2mm(v, 'us'),
        )

        thread = find_thread(name='triangular')(
            diameter=thread_diam,
            pitch=thread_diam * 0.6,
        )

        # --- Build screw
        screw_length = unit2mm(details['Length:'], details['Units:'])
        screw = cqparts_fasteners.screws.Screw(
            drive=drive,
            head=head,
            thread=thread,

            length=screw_length,
            neck_length=screw_length * 0.25,
            tip_length=1.5 * thread_diam,
        )

        return screw


class BoltSpider(BoltDepotProductSpider):
    name = 'bolts'
    start_urls = [
        'https://www.boltdepot.com/Hex_bolts_2.aspx',
        'https://www.boltdepot.com/Metric_hex_bolts_2.aspx',
    ]

    @classmethod
    def item_criteria(cls, data):
        criteria = {
            'name': data['name'],
            'url': data['url'],
        }
        criteria_content = [  # (<key>, <header>), ...
            ('units', 'Units:'),
            ('diameter', 'Diameter:'),
            ('material', 'Material:'),
            ('plating', 'Plating:'),
            ('finish', 'Finish:'),
            ('color', 'Color:'),
        ]
        for (key, header) in criteria_content:
            value = data['details'].get(header, None)
            if value is not None:
                criteria[key] = value.lower()
        return criteria

    @classmethod
    def build_component(cls, data):
        details = data['details']

        # --- Thread
        thread = None
        thread_diam = unit2mm(details['Diameter:'], details['Units:'])
        if details['Units:'].lower() == 'us':
            thread_pitch = unit2mm(1, 'us') / int(details['Thread count:'])
        elif details['Units:'].lower() == 'metric':
            thread_pitch = unit2mm(details['Thread pitch:'], details['Units:'])

        # ISO 68 thread: not accurate for imperial bolts, but close enough
        # FIXME: imperial threads?
        thread = find_thread(name='iso68')(
            diameter=thread_diam,
            pitch=thread_pitch,
            lefthand=details['Thread direction:'] == 'Left hand',
        )

        # --- Head
        head = None
        if details['Head style:'].lower() == 'hex':  # countersunk

            # Width Across Flats
            try:
                if details['Units:'].lower() == 'us':
                    across_flats = DataUSBoltHeadSize.get_data_item(
                        'Hex Bolt - Lag Bolt - Square Bolt',
                        criteria=lambda i: i['Bolt Diameter'] == details['Diameter:'],
                        cast=lambda v: DataUSBoltHeadSize.unit_cast(v),
                    )
                elif details['Units:'].lower() == 'metric':
                    try:
                        across_flats = DataMetricBoltHeadSize.get_data_item(
                            'ANSI/ISO',
                            criteria=lambda i: i['Bolt Diameter  (mm)'] == ("%g" % unit2mm(details['Diameter:'], 'metric')),
                            cast=lambda v: unit2mm(v, 'metric'),
                        )
                    except (ValueError, AttributeError):
                        # assumption: 'ANSI/ISO' field is non-numeirc, use 'DIN' instead
                        across_flats = DataMetricBoltHeadSize.get_data_item(
                            'DIN',
                            criteria=lambda i: i['Bolt Diameter  (mm)'] == ("%g" % unit2mm(details['Diameter:'], 'metric')),
                            cast=lambda v: unit2mm(v, 'metric'),
                        )
                else:
                    raise ValueError('unsupported units %r' % details['Units:'])
            except (AssertionError, AttributeError):
                # assumption: table lookup unsuccessful, see if it's explicitly specified
                across_flats = unit2mm(details['Width across the flats:'], details['Units:'])
                # raises KeyError if 'Width across the flats:' is not specified

            # Head Height
            head_height = 0.63 * thread_diam  # average height of all bolts with a defined head height

            head = find_head(name='hex')(
                width=across_flats,
                height=head_height,
                washer=False,
                # TODO: details['Head angle:'] usually 82deg
            )

        else:
            raise ValueError("head style %r not supported" % details['Head style:'])

        # --- Build bolt
        length = unit2mm(details['Length:'], details['Units:'])

        # Neck & Thread length
        neck_len = None
        try:
            neck_len = unit2mm(details['Body length Min:'], details['Units:'])
        except KeyError:
            pass  # 'Body length Min:' not specified

        thread_len = length
        try:
            thread_len = unit2mm(details['Thread length Min:'], details['Units:'])
            if neck_len is None:
                neck_len = length - thread_len
            else:
                neck_len = (neck_len + (length - thread_len)) / 2
        except KeyError:
            if neck_len is None:
                neck_len = 0

        bolt = cqparts_fasteners.bolts.Bolt(
            head=head,
            thread=thread,

            length=length,
            neck_length=neck_len,
        )

        return bolt


class NutSpider(BoltDepotProductSpider):
    name = 'nuts'
    start_urls = [
        'https://www.boltdepot.com/Hex_nuts.aspx',
        'https://www.boltdepot.com/Square_nuts.aspx',
        'https://www.boltdepot.com/Metric_hex_nuts.aspx',
    ]

    @classmethod
    def item_criteria(cls, data):
        criteria = {
            'name': data['name'],
            'url': data['url'],
        }
        criteria_content = [  # (<key>, <header>), ...
            ('units', 'Units:'),
            ('diameter', 'Diameter:'),
            ('material', 'Material:'),
            ('plating', 'Plating:'),
            ('finish', 'Finish:'),
            ('color', 'Color:'),
        ]
        for (key, header) in criteria_content:
            value = data['details'].get(header, None)
            if value is not None:
                criteria[key] = value.lower()
        return criteria

    @classmethod
    def build_component(cls, data):
        details = data['details']

        # --- Thread
        thread = None
        # diameter
        try:
            thread_diam = unit2mm(details['Diameter:'], details['Units:'])
        except AttributeError: # assumption: non-numeric diameter
            if details['Units:'] == 'US':
                thread_diam = DataUSThreadSize.get_data_item(
                    'Decimal',
                    criteria=lambda i: i['Size'] == details['Diameter:'],
                    cast=lambda v: unit2mm(v, 'us'),
                )
            else:
                raise

        # pitch
        if details['Units:'].lower() == 'us':
            thread_pitch = unit2mm(1, 'us') / int(details['Thread count:'])
        elif details['Units:'].lower() == 'metric':
            thread_pitch = unit2mm(details['Thread pitch:'], details['Units:'])

        # ISO 68 thread: not accurate for imperial bolts, but close enough
        # FIXME: imperial threads?
        thread = find_thread(name='iso68')(
            diameter=thread_diam,
            pitch=thread_pitch,
            lefthand=details['Thread direction:'] == 'Left hand',
            inner=True,
        )

        # --- build nut
        try:
            nut_width = unit2mm(details['Width across the flats:'], details['Units:'])
        except KeyError: # assumption: 'Width across the flats:' not supplied
            if details['Units:'] == 'US':
                try:
                    nut_width = DataUSNutSize.get_data_item(
                        'Diameter*:Hex Nut',
                        criteria=lambda i: i['Size:Size'] == details['Diameter:'],
                        cast=lambda v: unit2mm(v, 'us'),
                    )
                except ValueError:
                    nut_width = DataUSNutSize.get_data_item(
                        'Diameter*:Machine Screw Nut',  # only use if 'Hex Nut' not avaliable
                        criteria=lambda i: i['Size:Size'] == details['Diameter:'],
                        cast=lambda v: unit2mm(v, 'us'),
                    )
            else:
                raise

        # height
        try:
            nut_height = unit2mm(details['Height:'], details['Units:'])
        except KeyError:  # assumption: 'Height:' not specified
            if details['Units:'] == 'US':
                try:
                    nut_height = DataUSNutSize.get_data_item(
                        'Height:Hex Nut',
                        criteria=lambda i: i['Size:Size'] == details['Diameter:'],
                        cast=lambda v: unit2mm(v, 'us'),
                    )
                except ValueError:
                    nut_height = DataUSNutSize.get_data_item(
                        'Height:Machine Screw Nut',  # only use if 'Hex Nut' not avaliable
                        criteria=lambda i: i['Size:Size'] == details['Diameter:'],
                        cast=lambda v: unit2mm(v, 'us'),
                    )
            else:
                raise

        if details['Subcategory:'] == 'Hex nuts':
            nut_class = cqparts_fasteners.nuts.HexNut
        elif details['Subcategory:'] == 'Square nuts':
            nut_class = cqparts_fasteners.nuts.SquareNut
        else:
            raise ValueError("unsupported nut class %r" % details['Subcategory:'])

        nut = nut_class(
            thread=thread,
            width=nut_width,
            height=nut_height,
            washer=False,
        )

        return nut


SPIDERS = [
    WoodScrewSpider,
    BoltSpider,
    NutSpider,
]
SPIDER_MAP = {
    cls.name: cls
    for cls in SPIDERS
}


class GrowingList(list):
    """
    A list that will automatically expand if indexed beyond its limit.
    (the list equivalent of collections.defaultdict)
    """

    def __init__(self, *args, **kwargs):
        self._default_type = kwargs.pop('default_type', lambda: None)
        super(GrowingList, self).__init__(*args, **kwargs)

    def __getitem__(self, index):
        if index >= len(self):
            self.extend([self._default_type() for i in range(index + 1 - len(self))])
        return super(GrowingList, self).__getitem__(index)

    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([self._default_type() for i in range(index + 1 - len(self))])
        super(GrowingList, self).__setitem__(index, value)


class BoltDepotDataSpider(BoltDepotSpider):

    # set to True if the last header row does not uniquely identify each column
    merge_headers = False

    @staticmethod
    def table_data(table):
        # Pull data out of a table into a 2d list.
        # Merged Cells:
        #   any merged cells (using rowspan / colspan) will have duplicate
        #   data over each cell.
        #   "merging cells does not a database make" said me, just now

        def push_data(row, i, val):
            # push data into next available slot in the given list
            # return the index used (will be >= i)
            assert isinstance(row, GrowingList), "%r" % row
            assert val is not None
            try:
                while row[i] is not None:
                    i += 1
            except IndexError:
                pass
            row[i] = val
            return i

        data = GrowingList(default_type=GrowingList)  # nested growing list
        header_count = 0
        for (i, row) in enumerate(table.css('tr')):
            j = 0
            is_header_row = True
            for cell in row.css('th, td'):
                # cell data
                value = ' '.join([v.strip() for v in cell.css('::text').extract()])
                if value is None:
                    value = ''
                value = value.rstrip('\r\n\t ')
                rowspan = int(cell.css('::attr("rowspan")').extract_first() or 1)
                colspan = int(cell.css('::attr("colspan")').extract_first() or 1)
                # is header row?
                if cell.root.tag != 'th':
                    is_header_row = False
                # populate data (duplicate merged content)
                j = push_data(data[i], j, value)
                for di in range(rowspan):
                    for dj in range(colspan):
                        data[i + di][j + dj] = value
                j += 1
            if is_header_row:
                header_count += 1

        return (data, header_count)

    def parse(self, response):
        table = response.css('table.fastener-info-table')
        (data, header_count) = self.table_data(table)

        if self.merge_headers:
            header = [ # join all headers per column
                ':'.join(data[i][j] for i in range(header_count))
                for j in range(len(data[0]))
            ]
        else:
            header = data[header_count - 1]  # last header row
        for row in data[header_count:]:
            row_data = dict(zip(header, row))
            if any(v for v in row_data.values()):
                # don't yield if there's no data
                yield row_data


class DataWoodScrewDiam(BoltDepotDataSpider):
    name = 'd-woodscrew-diam'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Wood-Screws/Wood-Screw-Diameter.aspx',
    ]

class DataUSBoltThreadLen(BoltDepotDataSpider):
    name = 'd-us-bolt-thread-len'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Bolts/US-Thread-Length.aspx',
    ]

class DataUSThreadPerInch(BoltDepotDataSpider):
    name = 'd-us-tpi'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Measuring/US-TPI.aspx',
    ]

class DataUSBoltHeadSize(BoltDepotDataSpider):
    name = 'd-us-boltheadsize'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Bolts/US-Bolt-Head-Size.aspx',
    ]

    @staticmethod
    def unit_cast(value):
        # special case for the '7/16" or 3/8"' cell
        return unit2mm(re.split('\s*or\s*', value)[-1], 'us')  # last value

class DataUSNutSize(BoltDepotDataSpider):
    name = 'd-us-nutsize'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Nuts-Washers/US-Nut-Dimensions.aspx',
    ]
    merge_headers = True  # header 'Hex Nut' is repeated

class DataUSThreadSize(BoltDepotDataSpider):
    name = 'd-us-threadsize'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Machine-Screws/Machine-Screw-Diameter.aspx',
    ]

class DataMetricThreadPitch(BoltDepotDataSpider):
    name = 'd-met-threadpitch'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Measuring/Metric-Thread-Pitch.aspx',
    ]

class DataMetricBoltHeadSize(BoltDepotDataSpider):
    name = 'd-met-boltheadsize'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Bolts/Metric-Bolt-Head-Size.aspx',
    ]

class DataPhillipsDriveSizes(BoltDepotDataSpider):
    name = 'd-drivesizes-phillips'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Driver-Bits/Phillips-Driver-Sizes.aspx',
    ]


METRICS_SPIDERS = [
    DataWoodScrewDiam,
    DataUSBoltThreadLen,
    DataUSThreadPerInch,
    DataUSBoltHeadSize,
    DataUSNutSize,
    DataUSThreadSize,
    DataMetricThreadPitch,
    DataMetricBoltHeadSize,
    DataPhillipsDriveSizes,
]

# ---------- Command-line Arguments Parser ----------
DEFAULT_PREFIX = os.path.splitext(os.path.basename(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
))[0] + '-'

parser = argparse.ArgumentParser(
    description='Build Bolt Depot catalogue by crawling their website',
    epilog="""
Actions:
    scrape  scrape product details from website
    csv     convert scraped output to csv [optional]
    build   builds catalogue from scraped data
    all     (run all above actions)

Note: Actions will always be performed in the order shown above,
      even if they're not listed in that order on commandline.
    """,
    formatter_class=argparse.RawTextHelpFormatter,
)

VALID_ACTIONS = set(['scrape', 'csv', 'build', 'all'])
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

parser.add_argument(
    '--onlymetrics', '-om', dest='onlymetrics',
    action='store_const', const=True, default=False,
    help="if set, when scraping, only metrics data is scraped"
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

parser.add_argument(
    '--strict', '-s', dest='strict',
    default=False, action='store_const', const=True,
    help="if set, exceptions during a build stop progress",
)

args = parser.parse_args()
args.actions = set(args.actions)  # convert to set

BoltDepotSpider.prefix = args.prefix


# list catalogues & exit
if args.list:
    print("Catalogues:")
    for name in args.catalogues:
        print("  - %s" % name)
    exit(0)

# no actions, print help & exit
if not args.actions:
    parser.print_help()
    exit(1)


# ----- Start Crawl -----

if {'all', 'scrape'} & args.actions:
    print("----- Scrape: %s (+ metrics)" % (', '.join(args.catalogues)))
    sys.stdout.flush()

    # --- Clear feed files
    feed_names = []
    if not args.onlymetrics:
        feed_names += args.catalogues
    feed_names += [cls.name for cls in METRICS_SPIDERS]

    for name in feed_names:
        feed_filename = BoltDepotSpider.FEED_URI % {
            'prefix': args.prefix, 'name': name,
        }
        if os.path.exists(feed_filename):
            os.unlink(feed_filename)  # remove feed file to populate from scratch


    # --- Create Crawlers
    process = scrapy.crawler.CrawlerProcess(
        settings={
            'LOG_LEVEL': logging.INFO,
            'FEED_FORMAT': "json",
            'FEED_URI': BoltDepotSpider.FEED_URI,
        },
    )

    # product crawlers
    if not args.onlymetrics:
        for name in args.catalogues:
            process.crawl(SPIDER_MAP[name])
    # metrics crawlers
    for metrics_spider in METRICS_SPIDERS:
        process.crawl(metrics_spider)

    # --- Start Scraping
    process.start()


# ----- Convert to CSV -----
# Conversion of json files to csv is optional, csv's are easy to open
# in a 3rd party application to visualise the data that was scraped.

if {'all', 'csv'} & args.actions:

    def flatten_dict(dict_in):
        # flatten nested dicts using '.' separated keys
        def inner(d, key_prefix=''):
            for (k, v) in d.items():
                if isinstance(v, dict):
                    for (k1, v1) in inner(v, k + '.'):
                        yield (k1, v1)
                else:
                    yield (key_prefix + k, v)

        return dict(inner(dict_in))

    for cls in itertools.chain([SPIDER_MAP[n] for n in args.catalogues], METRICS_SPIDERS):
        print("----- CSV: %s" % cls.name)
        feed_json = cls.get_feed_uri()
        feed_csv = "%s.csv" % os.path.splitext(feed_json)[0]
        print("   %s --> %s" % (feed_json, feed_csv))
        data = cls.get_data()

        # pull out all possible keys to build header row
        headers = set(itertools.chain(*[
            tuple(str(k) for (k, v) in flatten_dict(row).items())
            for row in data
        ]))

        # Write row by row
        with open(feed_csv, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for rowdata in data:
                writer.writerow(utf8encoded(flatten_dict(rowdata)))


# ----- Build Catalogues -----

if {'all', 'build'} & args.actions:
    for name in args.catalogues:
        cls = SPIDER_MAP[name]
        print("----- Build: %s" % name)
        catalogue_file = os.path.join(
            '..', "%s.json" % os.path.splitext(cls.get_feed_uri())[0]
        )
        catalogue = cls.get_catalogue(clean=True)
        data = cls.get_data()

        sys.stdout.flush()  # make sure prints come through before bar renders
        bar = progressbar.ProgressBar()

        for item_data in bar(data):
            try:
                cls.add_to_catalogue(item_data, catalogue)
            except Exception as e:
                print("couldn't add: %s" % cls.get_item_str(item_data))
                print("%s: %s" % (type(e).__name__, e))
                sys.stdout.flush()
                if args.strict:
                    raise

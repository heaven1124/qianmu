import logging
from collections import defaultdict
from datetime import datetime

from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class SpiderOpenCloseLogging:

    def __init__(self, item_count):
        self.item_count = item_count
        self.items_scraped = 0
        self.items_dropped = 0
        # 默认值设为0
        self.stats = defaultdict(int)
        self.error_stats = defaultdict(int)
        print("=="*20, "extension object created")

    @classmethod
    # 由crawler调用
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        # get the number of items from settings
        item_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

        # instantiate the extension object
        ext = cls(item_count)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)

        # return the extension object
        return ext

    def spider_opened(self, spider):
        print("=="*20, "opened spider %s" % spider.name)

    def spider_closed(self, spider):
        print("=="*20, "closed spider %s" % spider.name)

    def item_scraped(self, item, spider):
        self.items_scraped += 1
        if self.items_scraped % self.item_count == 0:
            print("=="*20, "scraped %d items" % self.items_scraped)

    def item_dropped(self, item, spider, response, exception):
        self.items_dropped += 1
        if self.items_dropped % self.item_count == 0:
            print("**"*20, "dropped %d items" % self.items_dropped)

    def response_received(self, request, spider, response):
        now = datetime.now().strftime('%Y%m%d%H%M')
        self.stats[now] += 1
        if response.status in [401, 403, 404, 500, 501, 502]:
            self.error_stats[now] += 1
        if self.error_stats[now] / float(self.stats[now]) > 0.2:
            logger.warning('received %s response, and %s of them are not 200 in %s' %
                           (self.stats[now], self.error_stats[now], now))

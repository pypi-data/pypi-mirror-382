from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.Crawler import Crawler

class BaseCrawler(Crawler):

  def _before_crawled(self):
    # main crawler
    self._crawler_meta = self._meta.get(CrawlerName.Field.CRAWLER.value)
    self._crawler_conf = self._conf.get(CrawlerName.Field.CRAWLER.value)


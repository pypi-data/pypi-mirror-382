from selenium.webdriver.remote.webelement import WebElement
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.page.PageCrawler import PageCrawler

class NextPageCrawler(PageCrawler):

  NAME = CrawlerName.Engine.NEXT_PAGE

  def _crawl_by_page(self)->list[dict]|None:
    rows:list[dict] = []
    # crawl the first page
    page_no:int = 1
    if page_rows:= self._crawl_next_page():
      rows.extend(page_rows)
    # crawl the next pages
    while self._has_next():
      page_no += 1
      self._next_page()
      if page_rows:= self._crawl_next_page():
        rows.extend(page_rows)
        
      if page_no >= self._max_page_no:
        break
      self._set_interval()
    return rows
    
  def _has_next(self)->bool:
    next_button:WebElement|None = self._browser.waiter.querier.query(self._page_selector)
    return next_button.is_enabled() if next_button else False


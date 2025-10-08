import time
from abc import abstractmethod
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.NestCrawler import NestCrawler

class PageCrawler(NestCrawler):

  NAME = CrawlerName.Engine.PAGE

  def _before_crawled(self):
    super()._before_crawled()
    self._page_selector:str = self._summary_conf.get(CrawlerName.Field.PAGE_SELECTOR.value)
    self._max_page_no:int = self._summary_conf.get(CrawlerName.Field.MAX_PAGE_NO.value) or 10

    self._page_crawl_conf:list[dict] = self._get_page_crawl_conf()
    self._child:dict = self._meta.get(CrawlerName.Field.CHILD.value)

    
  def _get_page_crawl_conf(self)->list[dict]:
    page_conf:list[dict] = self._conf.get(CrawlerName.Field.PAGE_CRAWL.value,[])
    page_conf.insert(0,{
			"_kind":"click",
			"target_CS_WE":self._page_selector,
		})
    return page_conf
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    @return {STDOut}
    '''
    if not self._child:
      message = f'[{self.NAME}] Failed to crawl - Missing child config'
      return STDOut(500,message)
    
    if not self._page_selector:
      message = f'[{self.NAME}] Failed to crawl - Missing page_selector config'
      return STDOut(500,message)

    try:
      rows:list[dict]|None = self._crawl_by_page()
      return STDOut(200,'success',rows)
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      return STDOut(500,message)

  @abstractmethod
  def _crawl_by_page(self)->list[dict]|None:
    pass

  def _next_page(self)->Model:
    model = Model(self._page_crawl_conf)
    self._invoke(model)
    
  def _crawl_next_page(self)->list[dict]|None:
    model = Model(self._child,self._bizdata)
    stdout:STDOut = self._crawl_by_meta(model,CrawlerName.Engine.URL.value)
    if not stdout.data:
      return None 
    
    if isinstance(stdout.data,list):
      return stdout.data
    else:
      return [stdout.data]

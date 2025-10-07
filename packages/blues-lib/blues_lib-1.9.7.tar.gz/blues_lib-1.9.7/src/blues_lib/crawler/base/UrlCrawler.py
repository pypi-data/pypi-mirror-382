from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.base.BaseCrawler import BaseCrawler

class UrlCrawler(BaseCrawler):

  NAME = CrawlerName.Engine.URL
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    @return {STDOut}
    '''
    if not self._crawler_meta:
      message = f'[{self.NAME}] Failed to crawl - Missing crawler config'
      return STDOut(500,message)

    # must pass the meta and bizdata, some behavior need to calculate the model
    model = Model(self._crawler_meta,self._bizdata)

    return self._invoke(model)

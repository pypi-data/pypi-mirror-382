from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.Crawler import Crawler
from blues_lib.crawler.base.BaseCrawlerFactory import BaseCrawlerFactory

class NestCrawler(Crawler):
  
  def _crawl_by_meta(self,model:Model,crawler_type:str='')->STDOut:
    # crawl : loop crawler will merge the entity to the output.data
    summary_conf:dict = model.config.get('summary',{})
    self._disable_quit(summary_conf)
    crawler_name:CrawlerName = self._get_crawler(summary_conf,crawler_type)
    crawler = BaseCrawlerFactory(model,self._browser).create(crawler_name)
    return crawler.execute()
  
  def _get_crawler(self,summary_conf:dict,crawler_type:str='')->CrawlerName:
    conf_crawler_type:str = summary_conf.get(CrawlerName.Field.TYPE.value)
    dft_crawler_type:str = CrawlerName.Engine.URL.value
    real_crawler_type:str = conf_crawler_type or crawler_type or dft_crawler_type
    return CrawlerName.Engine.from_value(real_crawler_type)
  
  def _disable_quit(self,summary_conf:dict):
    # 如何明确quit则保留，否则meta子crawler默认quit=False
    if summary_conf.get(CrawlerName.Field.QUIT.value)!= True:
      summary_conf[CrawlerName.Field.QUIT.value] = False

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model
from blues_lib.sele.browser.Browser import Browser 
from blues_lib.crawler.dfs.DepthCrawler import DepthCrawler
from blues_lib.namespace.CrawlerName import CrawlerName

class DfsCrawlerFactory(Factory):

  _crawlers = {
    DepthCrawler.NAME:DepthCrawler,
  }

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    self._model = model
    self._browser = browser

  def create(self,name:CrawlerName):
    crawler = self._crawlers.get(name)
    if not crawler:
      return None
    return crawler(self._model,self._browser)

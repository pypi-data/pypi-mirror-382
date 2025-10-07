from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model
from blues_lib.sele.browser.Browser import Browser 
from blues_lib.crawler.base.BaseCrawlerFactory import BaseCrawlerFactory
from blues_lib.crawler.dfs.DfsCrawlerFactory import DfsCrawlerFactory
from blues_lib.crawler.page.PageCrawlerFactory import PageCrawlerFactory

from blues_lib.namespace.CrawlerName import CrawlerName

class CrawlerFactory(Factory):

  _factory_classes = [BaseCrawlerFactory,DfsCrawlerFactory,PageCrawlerFactory]

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    self._model = model
    self._browser = browser

  def create(self,name:CrawlerName):
    for factory_class in self._factory_classes:
      factory:Factory = factory_class(self._model,self._browser)
      if crawler := factory.create(name):
        return crawler
    return None

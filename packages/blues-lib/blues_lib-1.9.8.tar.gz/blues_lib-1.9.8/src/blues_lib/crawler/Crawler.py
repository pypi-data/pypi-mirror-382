from abc import abstractmethod
from blues_lib.behavior.BhvExecutor import BhvExecutor
from blues_lib.type.executor.Executor import Executor
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.sele.browser.Browser import Browser 
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.util.BluesDateTime import BluesDateTime

class Crawler(Executor):

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    super().__init__()
    self._model:Model = model
    self._browser:Browser = browser

  def _setup(self):
    # model
    self._conf:dict = self._model.config 
    self._meta:dict = self._model.meta
    self._bizdata:dict = self._model.bizdata
    
    # summary
    self._summary_conf:dict = self._conf.get(CrawlerName.Field.SUMMARY.value,{})
    self._count :int = self._summary_conf.get(CrawlerName.Field.COUNT.value,-1)
    # by default, quit the browser after crawled
    self._quit :bool = self._summary_conf.get(CrawlerName.Field.QUIT.value,True)
    
    # hook
    self._before_crawled_conf = self._conf.get(CrawlerName.Field.BEFORE_CRAWLED.value,{})
    self._after_crawled_conf = self._conf.get(CrawlerName.Field.AFTER_CRAWLED.value,{})
    self._before_each_crawled_conf = self._conf.get(CrawlerName.Field.BEFORE_EACH_CRAWLED.value,{})
    self._after_each_crawled_conf = self._conf.get(CrawlerName.Field.AFTER_EACH_CRAWLED.value,{})
    
    # head crawler
    self._head_meta:dict = self._meta.get(CrawlerName.Field.HEAD_CRAWL.value)
    self._head_conf:dict = self._conf.get(CrawlerName.Field.HEAD_CRAWL.value)

    # foot crawler
    self._foot_meta:dict = self._meta.get(CrawlerName.Field.FOOT_CRAWL.value)
    self._foot_conf:dict = self._conf.get(CrawlerName.Field.FOOT_CRAWL.value)

  def execute(self)->STDOut:
    # Template method: define the cal structure
    self._setup()
    
    self._before_crawled()
    self._head()
    output:STDOut = self._crawl()
    self._foot(output)
    self._after_crawled(output)

    self._slice(output)
    self._close()
    self._log(output)
    return output
  
  def _before_crawled(self):
    pass

  def _head(self)->any:
    # execute the head crawler
    if self._head_meta:
      # must pass the meta and bizdata, some behavior need to calculate the model
      model = Model(self._head_meta,self._bizdata)
      return self._invoke(model)

  @abstractmethod
  def _crawl(self)->STDOut:
    pass
  
  def _foot(self,output:STDOut)->any:
    # execute the head crawler
    if self._foot_meta:
      # must pass the meta and bizdata, some behavior need to calculate the model
      model = Model(self._foot_meta,self._bizdata)
      return self._invoke(model)
  
  def _invoke(self,model:Model)->STDOut:
    # execute a base crawler
    try:
      bhv = BhvExecutor(model,self._browser)
      stdout:STDOut = bhv.execute()
      if isinstance(stdout.data,dict):
        stdout.data = stdout.data.get(CrawlerName.Field.DATA.value)
      return stdout
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
  def _after_crawled(self,output:STDOut):
    pass

  def _slice(self,output:STDOut):
    # slice the data by the config count

    if self._count==-1 or output.code!=200:
      return
    
    if not output.data or not isinstance(output.data,list):
      return

    output.data = output.data[:self._count]
  
  def _log(self,output:STDOut):
    if output.code != 200:
      message = f'[{self.NAME}] Failed to crawl - {output.message}'
      self._logger.error(message)
    else:
      message = f'[{self.NAME}] Managed to crawl'
      self._logger.info(message)

  def _open(self,url:str):
    self._browser.open(url)

  def _close(self):
    if self._quit and self._browser:
      self._browser.quit()

  def _set_interval(self):
    interval = self._summary_conf.get(CrawlerName.Field.LOOP_INTERVAL.value) or 1
    BluesDateTime.count_down({
      "duration":interval,
      "title":"loop interval",
    })

from blues_lib.type.output.STDOut import STDOut
from blues_lib.crawler.base.LoopCrawler import LoopCrawler
from blues_lib.material.MatHanderChain import MatHanderChain


from blues_lib.namespace.CrawlerName import CrawlerName

class MatLoopCrawler(LoopCrawler):

  NAME = CrawlerName.Engine.MAT_LOOP
  
  def _after_each_crawled(self,output:STDOut)->None:
    '''
    Format the rows after one loop, before count
    '''
    if output.code!=200 or not output.data:
      return 

    # deal with by each crawled conf
    if not self._after_each_crawled_conf:
      return

    request = {
      'config':self._after_each_crawled_conf,
      'entities':output.data,
    }
    handled_output:STDOut = MatHanderChain(request).handle()
    if handled_output.code == 200 and handled_output.data:
      output.code = 200
      output.data = handled_output.data
    else:
      output.code = 500
      output.message = handled_output.message
      output.data = []
      
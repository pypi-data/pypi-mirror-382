from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.base.BaseCrawler import BaseCrawler

class ForCrawler(BaseCrawler):

  NAME = CrawlerName.Engine.FOR
    
  def _before_crawled(self):
    super()._before_crawled()
    self._entities:list[dict] = self._get_entities()

  def _get_entities(self)->list[dict]|None:
    '''
    Set the entities for for crawler
    @return {None}
    '''
    entities:list[dict] = self._summary_conf.get(CrawlerName.Field.ENTITIES.value) 
    if entities:
      return entities

    for_count:int = self._summary_conf.get(CrawlerName.Field.FOR_COUNT.value) or 1
    # pad a empty entity for each for count
    return [{} for _ in range(for_count)]
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    execute the main crawler looply, by the entities or count
    @return {STDOut}
    '''
    if not self._crawler_meta:
      message = f'[{self.NAME}] Failed to crawl - Missing crawler config'
      return STDOut(500,message)

    if not self._entities:
      message = f'[{self.NAME}] Failed to crawl - Missing entities'
      return STDOut(500,message)
    
    results:list[STDOut] = []
    
    try:
      for entity in self._entities:
        # use the entity to cover the bizdata
        merged_entity = {**self._bizdata,**entity}
        model = Model(self._crawler_meta,merged_entity)
        results.append(self._invoke(model))
        self._set_interval()
        
      rows,messages = self._get_format_results(results)
      return STDOut(200,'ok',rows,messages)
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      return STDOut(500,message)
    
  def _get_format_results(self,results:list[STDOut])->tuple:
    # 分离成功数据与失败message
    rows:list[dict] = []
    messages:list[str] = []
    for result in results:
      if result.code == 200:
        if result.data:
          # 注意：如果单次获取的是数组要合并
          if isinstance(result.data,list):
            rows.extend(result.data)
          else:
            rows.append(result.data)
          messages.append(f'{result.code}:ok')
        else:
          messages.append(f'{result.code}:no data')
      else:
        messages.append(f'{result.code}:{result.message}')
    
    return (rows,messages)

import json
from blues_lib.behavior.hook.BhvProcessor import BhvProcessor
from blues_lib.util.html.HtmlExtractor import HtmlExtractor 

class HtmlFilter(BhvProcessor):
  
  def execute(self)->list[dict]|None:
    f'''
    @description: convert the answer to mat dict
    @return {list[dict]|None} the mat dict list
    '''
    if not self._value:
      self._logger.error(f'[{self.__class__.__name__}] Bhv getter value is None')
      return self._value

    return self._extract(self._value)
 
  def _extract(self,html:str):
    includes:list[str] = self._proc_conf.get('includes',[]) 
    excludes:list[str] = self._proc_conf.get('excludes',[])
    result:dict = HtmlExtractor().extract(html, includes,excludes)
    return result['html']


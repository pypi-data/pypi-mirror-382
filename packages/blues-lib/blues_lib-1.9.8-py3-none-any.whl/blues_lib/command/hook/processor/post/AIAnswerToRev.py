import json
from datetime import datetime

from blues_lib.command.hook.processor.post.AbsPostProc import AbsPostProc
from blues_lib.llm.revision.Extractor import Extractor

class AIAnswerToRev(AbsPostProc):
  # revision
  
  ANSWER_KEY = 'answer'
  
  def execute(self)->None:
    '''
    @description: Convert the AI answer to mat dict
    @return: None
    '''
    if not self._output.data:
      self._set_error(current_time,'no output.data.answer found')
      return

    answer:str = self._output.data.get(self.ANSWER_KEY)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not answer:
      self._set_error(current_time,'no answer found')
      return

    if material := self._load_from_json(current_time,answer):
      self._set_success(current_time,material)

  def _set_success(self,current_time:str,material:dict):
    material['rev_stat'] = "success"
    material['rev_time'] = current_time
    self._output.data = material
    
  def _set_error(self,current_time:str,message:str):
    self._output.code = 500
    self._output.message = f'{self.__class__.__name__} - {message}'
    self._output.data = {
      'rev_stat':"failure",
      'rev_time':current_time,
    }

  def _load_from_json(self,current_time:str,answer:str)->dict|None:
    try:
      item:dict =  json.loads(answer)
      # extractor or revision
      if item.get('rev_title') and item.get('rev_texts'):
        return item
      else:
        self._set_error(current_time,f'field missing: {item}')
        return None
    except Exception as error:
      self._set_error(current_time,f'json load error: {error}')
      return None

  def _load_from_text(self,answer:str)->dict:
    return Extractor().execute(answer) 

    
    
    
     

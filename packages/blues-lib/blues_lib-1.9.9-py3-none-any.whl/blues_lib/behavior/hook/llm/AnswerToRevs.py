from datetime import datetime
from blues_lib.behavior.hook.llm.AnswerParser import AnswerParser

class AnswerToRevs(AnswerParser):
  
  def _add_system_fields(self,revs:list[dict])->None:
    if not revs:
      return

    # 补充mat系统字段
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for rev in revs:
      system_fields:dict = self._get_system_fields(rev,current_time) 
      rev.update(system_fields)
      
  def _get_system_fields(self,rev:dict,current_time:str)->dict:
    stat:str = 'failure'
    if rev.get('rev_title') and rev.get('rev_texts'):
      stat = 'success'

    return {
      'rev_stat':stat,
      'rev_time':current_time,
    }
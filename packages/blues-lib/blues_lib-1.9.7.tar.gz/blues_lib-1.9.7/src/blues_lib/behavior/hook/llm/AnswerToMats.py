from datetime import datetime
from blues_lib.behavior.hook.llm.AnswerParser import AnswerParser

class AnswerToMats(AnswerParser):
  
  def _add_system_fields(self,mats:list[dict])->None:
    if not mats:
      return

    # 补充mat系统字段
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for mat in mats:
      system_fields = self._get_system_fields(mat,current_time)
      mat.update(system_fields)
      
  def _get_system_fields(self,mat:dict,current_time:str)->dict:
    fields:dict = {
      # 基于entities遍历的for crawler会更新entity到bizdata
      'mat_stat':"available",
      'mat_ctime':current_time,
    }
    # briefs场景补充为depth爬取的系统字段url，不可用bizdata中的覆盖
    if mat.get('mat_url'):
      fields['url'] = mat.get('mat_url')
    else:
      # mat场景本身没有url，必须从bizdata中获取
      fields['mat_url'] = self._bhv_model.bizdata.get('mat_url','')
    return fields
  
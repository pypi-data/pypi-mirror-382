from blues_lib.behavior.hook.llm.AnswerToMats import AnswerToMats

class AnswerToMatsRevs(AnswerToMats):
  # 接收的字段与extractor相同，但需要扩展出rev_字段
  
  
  def _get_system_fields(self,mat:dict,current_time:str)->dict:
    fields:dict = super()._get_system_fields(mat,current_time)
    rev_fields:dict = self._get_rev_fields(mat,current_time)
    return {**fields,**rev_fields}
  
  def _get_rev_fields(self,mat:dict,current_time:str)->dict:
    mat_title:str = mat.get('mat_title','')
    mat_paras:list[dict] = mat.get('mat_paras',[])
    rev_texts:list[str] = [para.get('value','') for para in mat_paras if para.get('type')=='text']
    return {
      'rev_title':mat_title,
      'rev_texts':rev_texts,
      'rev_stat':"success",
      'rev_time':current_time,
    }
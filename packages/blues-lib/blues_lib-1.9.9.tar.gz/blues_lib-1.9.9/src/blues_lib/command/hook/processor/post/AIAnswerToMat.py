import json
from datetime import datetime
from blues_lib.command.hook.processor.post.AbsPostProc import AbsPostProc
from blues_lib.llm.revision.Extractor import Extractor

class AIAnswerToMat(AbsPostProc):
  # extract
  
  ANSWER_KEY = 'answer'
  
  def execute(self)->None:
    '''
    @description: Convert the AI answer to mat dict
    @return: None
    '''
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not self._output.data:
      self._set_error(current_time,'no output.data.answer found')
      return
    
    rows:list[dict] = self._output.data if isinstance(self._output.data,list) else [self._output.data]
    # 只保留有效数据
    materials:list[dict] = []
    messages:list[str] = []
    for row in rows:
      if sub_materials := self._process_one(row,current_time,messages):
        materials.extend(sub_materials)
    if materials:
      # 保留数据输出类型不变
      self._output.data = materials if isinstance(self._output.data,list) else materials[0]
      self._output.detail = messages
    else:
      self._set_error(current_time,f'no valid material found: {messages}',messages)

  def _process_one(self,row:dict,current_time:str,messages:list[str])->list[dict]|None:
    answer:str = row.get(self.ANSWER_KEY)
    if not answer:
      messages.append('no answer found')
      return None

    if materials := self._load_from_json(current_time,answer,messages):
      return materials
    
  def _set_error(self,current_time:str,message:str,messages:list[str]):
    self._output.code = 500
    self._output.message = f'{self.__class__.__name__} - {message}'
    self._output.detail = messages
    self._output.data = {
      'mat_stat':"invalid",
      'mat_ctime':current_time,
    }

  def _load_from_json(self,current_time:str,answer:str,messages:list[str])->list[dict]|None:
    try:
      load_data:list[dict]|dict =  json.loads(answer)
      # extractor or revision
      return self._get_items(load_data,current_time)
    except Exception as error:
      messages.append(f'json load error: {error}')
      return None
    
  def _get_items(self,load_data:list[dict]|dict,current_time:str)->list[dict]|None:
    # answer解析内容可能是数组或字典
    items:list[dict] = load_data if isinstance(load_data,list) else [load_data]
    # 过滤与补充
    materials:list[dict] = []
    for item in items:
      # 使用标题做简单判断
      if item.get('mat_title'):
        item['mat_stat'] = "available"
        item['mat_ctime'] = current_time
        materials.append(item)
    return materials if materials else None

  def _load_from_text(self,answer:str)->dict:
    return Extractor().execute(answer) 

    
    
    
     

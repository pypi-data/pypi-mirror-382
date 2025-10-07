from blues_lib.type.model.Model import Model
from blues_lib.behavior.Bean import Bean
from blues_lib.behavior.BhvExecutor import BhvExecutor


class Richtext(Bean):

  def _set(self)->any:
    # [{'type':'text','value':'xxx'},{'type':'image','value':'c:/xx.png'}]
    paras:list[dict] = self._config.get('value')
    if not paras or not isinstance(paras,list):
      return

    frame_CS_WE:str = self._config.get('frame_CS_WE')
    if frame_CS_WE:
      self._switch(frame_CS_WE,'framein')
      
    self._setup()

    prev_para = {} 
    for para in paras:
      self._set_para(para,prev_para)
      prev_para = para

    if frame_CS_WE:
      self._switch(frame_CS_WE,'frameout')
      
  def _setup(self):
    conf:dict = self._config.get('setup',{})
    bhv_chain:list[dict] = conf.get('bhv_chain')
    if not conf or not bhv_chain:
      return

    frame_CS_WE:str = conf.get('frame_CS_WE')
    if frame_CS_WE:
      self._switch(frame_CS_WE,'framein')
      
    model = Model(bhv_chain)
    BhvExecutor(model,self._browser).execute()

    if frame_CS_WE:
      self._switch(frame_CS_WE,'frameout')
      

  def _set_para(self,para:dict,prev_para:dict)->None:
    type = para.get('type')
    prev_type = prev_para.get('type')
    value = para.get('value')
    conf:dict = self._config.get(type,{})
    
    meta:dict = self._meta.get(type,{})
    bhv_chain:list[dict] = meta.get('bhv_chain')
    if not value or not bhv_chain:
      return
    
    frame_CS_WE:str = conf.get('frame_CS_WE')
    if frame_CS_WE:
      self._switch(frame_CS_WE,'framein')
    
    # if the prev para is image, then add a empty line before the text
    if type=='text' and prev_type=='image':
      value = ['',value]

    bizdata = {
      **self._bizdata,
      "value":value
    }
    model = Model(bhv_chain, bizdata)
    BhvExecutor(model,self._browser).execute()

    if frame_CS_WE:
      self._switch(frame_CS_WE,'frameout')
  
  def _switch(self,frame_CS_WE:str,kind:str)->None:
    conf = {
      '_kind':kind,
      'target_CS_WE':frame_CS_WE
    }
    model = Model(conf)
    BhvExecutor(model,self._browser).execute()

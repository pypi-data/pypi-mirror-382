from blues_lib.command.hook.processor.prev.AbsPrevProc import AbsPrevProc
from blues_lib.llm.prompt.PromptFactory import PromptFactory
from blues_lib.util.NestedDataReader import NestedDataReader
from blues_lib.util.NestedDataWriter import NestedDataWriter
from blues_lib.command.hook.mapping.Mapper import Mapper

class TextToAIQuery(AbsPrevProc):
  
  def execute(self)->bool:
    '''
    @description: Convert the text to ai query, change the bizdata and refresh the Model
    @return: None
    '''
    mapper = Mapper(self._context,self._input,self._proc_conf)
    source_data,source_attr_chain = mapper.get_source()
    target_data,target_attr_chain = mapper.get_target()
    if not source_data or not target_data:
      return False

    text:str = NestedDataReader.read_by_path(source_data,source_attr_chain)
    query:str = self._get_prompt(text)
    # rewrite the source node data
    if has_written := NestedDataWriter.write_by_path(target_data,target_attr_chain,query):
      self._input.refresh()
    return has_written
  
  def _get_prompt(self,text:str)->str:
    if prompt_template := self._proc_conf.get('prompt_template'):
      return PromptFactory().create(prompt_template,text)

    if prompt := self._proc_conf.get('prompt'):
      return f"{prompt} {text}"

    return ''

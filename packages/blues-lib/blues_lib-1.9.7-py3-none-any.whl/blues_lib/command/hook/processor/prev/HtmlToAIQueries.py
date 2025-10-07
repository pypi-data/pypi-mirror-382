from blues_lib.command.hook.processor.prev.AbsPrevProc import AbsPrevProc
from blues_lib.llm.prompt.PromptFactory import PromptFactory
from blues_lib.util.NestedDataReader import NestedDataReader
from blues_lib.util.NestedDataWriter import NestedDataWriter
from blues_lib.command.hook.mapping.Mapper import Mapper

class HtmlToAIQueries(AbsPrevProc):
  # 基于多个html文档转为多个ai查询
  
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

    # html spider爬取的多个网页源码
    rows:list[dict] = NestedDataReader.read_by_path(source_data,source_attr_chain)
    entities:list[str] = []
    for row in rows:
      html:str = row.get('html','')
      if not html:
        continue

      if query:= self._get_prompt(html):
        # 创建包含query和系统字段的遍历列表，重点要获取 mat_url
        entity = {**row,
          'query':query,
        }
        del entity['html'] # 删除重复属性
        entities.append(entity)

    # 为bizdata设置queries节点数据
    if has_written := NestedDataWriter.write_by_path(target_data,target_attr_chain,entities):
      self._input.refresh()
    return has_written
  
  def _get_prompt(self,text:str)->str:
    if prompt_template := self._proc_conf.get('prompt_template'):
      return PromptFactory().create(prompt_template,text)

    if prompt := self._proc_conf.get('prompt'):
      return f"{prompt} {text}"

    return ''

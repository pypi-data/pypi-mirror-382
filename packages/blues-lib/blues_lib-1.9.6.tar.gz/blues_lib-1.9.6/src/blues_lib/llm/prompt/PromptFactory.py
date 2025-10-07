from blues_lib.llm.prompt.template.html.DetailExtractor import DetailExtractor
from blues_lib.llm.prompt.template.html.DetailRevision import DetailRevision
from blues_lib.llm.prompt.template.html.BriefExtractor import BriefExtractor
from blues_lib.llm.prompt.template.revision.ArticleRevision import ArticleRevision

class PromptFactory:
  
  templates:dict = {
    'DetailExtractor':DetailExtractor.MARKDOWN,
    'DetailRevision':DetailRevision.MARKDOWN,
    'BriefExtractor':BriefExtractor.MARKDOWN,
    'ArticleRevision':ArticleRevision.MARKDOWN,
  }
  
  def create(self,topic:str,text:str)->dict:
    prompt:dict = self.templates.get(topic)
    if not prompt:
      raise ValueError(f'Prompt topic {topic} not found')
    return f'{prompt}{text}'

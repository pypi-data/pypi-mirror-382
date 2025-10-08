import sys,os,re

from blues_lib.publisher.Publisher import Publisher       
from blues_lib.sele.behavior.FormBehavior import FormBehavior       

class ArticlePublisher(Publisher):

  def _execute(self):
    self._title()
    self._content()
    self._thumbnail() # must execute after the content
    self._others()

  def _title(self): 
    if self.schema.title_execution:
      handler = FormBehavior(self.browser,self.schema.title_execution)
      handler.handle()

  def _content(self):
    if self.schema.content_execution:
      handler = FormBehavior(self.browser,self.schema.content_execution)
      handler.handle()

  def _others(self):
    if self.schema.others_execution:
      handler = FormBehavior(self.browser,self.schema.others_execution)
      handler.handle()

  def _thumbnail(self):
    if self.schema.thumbnail_execution:
      handler = FormBehavior(self.browser,self.schema.thumbnail_execution)
      handler.handle()

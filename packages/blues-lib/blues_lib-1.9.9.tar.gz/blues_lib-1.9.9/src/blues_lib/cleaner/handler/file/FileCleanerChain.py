import sys,os,re

from blues_lib.cleaner.handler.CleanerHandler import CleanerHandler
from .MaterialHandler import MaterialHandler  
from .LogHandler import LogHandler  

class FileCleanerChain(CleanerHandler):

  kind = 'chain'

  def resolve(self,request):
    handler = self._get_chain()
    return handler.handle(request)

  def _get_chain(self):
    material_handler = MaterialHandler()
    log_handler = LogHandler()
    
    material_handler.set_next(log_handler)

    return material_handler

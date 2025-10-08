import sys,os,re

from blues_lib.material.file.MatFile import MatFile
from blues_lib.cleaner.handler.CleanerHandler import CleanerHandler
from blues_lib.util.BluesFiler import BluesFiler
from blues_lib.deco.LogDeco import LogDeco

class LogHandler(CleanerHandler):

  kind = 'handler'

  @LogDeco()
  def resolve(self,request):
    '''
    Args:
      {dict} request : 
        - {dict} log 
          - {int} validity_days : by default is 100
          - {dict} response : cleared response
    Returns {dict} response
      - {int} code
      - {int} count
      - {str} message
    '''
    main_req = request.get('file')
    if not main_req:
      return 

    sub_req = main_req.get('log')
    if not sub_req:
      return 

    root = MatFile.get_log_root()
    validity_days = sub_req.get('validity_days',30)
    count = BluesFiler.removedirs(root,validity_days)
    response = {
      'code':200,
      'count':count,
      'message':'Deleted logs.',
    }
    sub_req['response'] = response
    self.set_message(response)
    return response
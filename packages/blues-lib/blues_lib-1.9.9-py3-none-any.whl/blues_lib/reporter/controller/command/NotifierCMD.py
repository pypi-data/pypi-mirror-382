import sys,os,re


from blues_lib.type.executor.Command import Command
from blues_lib.reporter.handler.PubNotifierHandler import PubNotifierHandler   

class NotifierCMD(Command):

  name = __name__

  def execute(self):
    # base on the publisher material entity
    request = self._context.get('publisher')
    if not request:
      raise Exception('The param context.publisher is missing')

    response = PubNotifierHandler().handle(request)

    if response['code']!=200 :
      raise Exception('Failed to notify by the mailer - %s!' % response['message'])

    self._context['reporter'] = {
      'response':response,
    }
    


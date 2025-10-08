import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.chain.Handler import Handler

class FirstMatchHandler(Handler):

  def handle(self):
    stdout = self.resolve()
    if stdout.code==200:
      return stdout

    if self._next_handler:
      return self._next_handler.handle()

    return STDOut(500,'Failed to handle the request',None)

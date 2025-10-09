import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.chain.Handler import Handler

class AllMatchHandler(Handler):

  def handle(self)->STDOut:
    stdout = self.resolve()

    if self._next_handler:
      return self._next_handler.handle()
    else:
      return stdout


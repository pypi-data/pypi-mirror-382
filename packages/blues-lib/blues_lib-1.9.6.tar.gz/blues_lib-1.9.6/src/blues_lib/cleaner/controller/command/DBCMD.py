import sys,os,re


from blues_lib.type.executor.Command import Command
from blues_lib.cleaner.handler.db.DBCleanerChain import DBCleanerChain   

class DBCMD(Command):

  name = __name__

  def execute(self):
    DBCleanerChain().handle(self._context)

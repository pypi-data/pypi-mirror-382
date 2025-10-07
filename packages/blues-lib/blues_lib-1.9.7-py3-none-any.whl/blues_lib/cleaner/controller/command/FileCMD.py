import sys,os,re


from blues_lib.type.executor.Command import Command
from blues_lib.cleaner.handler.file.FileCleanerChain import FileCleanerChain   

class FileCMD(Command):

  name = __name__

  def execute(self):
    FileCleanerChain().handle(self._context)



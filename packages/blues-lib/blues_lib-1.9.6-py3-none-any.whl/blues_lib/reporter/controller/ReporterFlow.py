import sys,os,re

from blues_lib.type.executor.CommandFlow import CommandFlow
from blues_lib.reporter.controller.command.NotifierCMD import NotifierCMD

class ReporterFlow(CommandFlow):
  
  def load(self):

    notifier_cmd = NotifierCMD(self._context)
    self.add(notifier_cmd)
  





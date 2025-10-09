import os,sys,re

from blues_lib.util.BluesMailer import BluesMailer
from blues_lib.logger.FileLogger import FileLogger

class MailLogger(FileLogger):

  def info(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().info(message)
    BluesMailer.send(payload)

  def warning(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().warning(message)
    BluesMailer.send(payload)
  
  def error(self,message:str,payload:dict):
    '''
    @description write log
    @param {MailPayload}
    '''
    super().error(message)
    BluesMailer.send(payload)

  def debug(self,message:str,payload:dict):
    super().debug(message)
    BluesMailer.send(payload)
    
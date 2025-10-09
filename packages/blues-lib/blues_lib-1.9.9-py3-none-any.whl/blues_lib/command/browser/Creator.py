import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.sele.browser.chrome.ChromeFactory import ChromeFactory   
from blues_lib.namespace.CommandName import CommandName
from blues_lib.config.ConfigManager import config

class Creator(NodeCommand):

  NAME = CommandName.Browser.CREATOR
  TYPE = CommandName.Type.ACTION

  def _invoke(self)->STDOut:
    driver_config =  self._node_conf.get('driver_config')
    driver_options = self._node_conf.get('driver_options') or {}
    browser = ChromeFactory(**driver_options).create(driver_config)
    return STDOut(200,'ok',browser) if browser else STDOut(500,'failed to create the browser')
import sys,os,re

from blues_lib.type.executor.Command import Command
from blues_lib.sele.browser.BrowserFactory import BrowserFactory   

class BrowserCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['publisher']['schema'].get('executor')
    executable_path = executor_schema.browser.get('path')
    browser_mode = executor_schema.browser.get('mode') # login or headlesslogin

    loginer_schema = self._context['publisher']['schema'].get('loginer')
    browser = BrowserFactory(browser_mode).create(executable_path=executable_path,loginer_schema=loginer_schema)

    if not browser:
      raise Exception('[Publisher] Failed to create a browser!')

    self._context['publisher']['browser'] = browser

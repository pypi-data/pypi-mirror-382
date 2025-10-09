import sys,os,re

from blues_lib.behavior.Bean import Bean

class Url(Bean):

  def _get(self)->str:
    return self._browser.interactor.document.get_url()

import sys,os,re

from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.formatter.Normalizer import Normalizer
from blues_lib.material.formatter.Validator import Validator
from blues_lib.material.formatter.Deduplicator import Deduplicator
from blues_lib.material.privatizer.Localizer import Localizer
from blues_lib.material.sinker.Sinker import Sinker

class MatHanderChain(AllMatchHandler):
  
  def resolve(self)->STDOut:
    try:
      chain = self._get_chain()
      stdout = chain.handle()
      # parse the request entities
      if stdout.code!=200:
        return stdout
      else:
        return STDOut(200,'ok',self._request['entities'])
    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to format - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
  def _get_chain(self)->AllMatchHandler:
    normalizer = Normalizer(self._request)
    deduplicator = Deduplicator(self._request)
    validator = Validator(self._request)
    localizer = Localizer(self._request)
    sinker = Sinker(self._request)
    
    normalizer.set_next(deduplicator).set_next(validator).set_next(localizer).set_next(sinker)
    return normalizer

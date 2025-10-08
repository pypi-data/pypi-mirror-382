import sys,os,re

from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.privatizer.image.Downloader import Downloader
from blues_lib.material.privatizer.image.Formatter import Formatter

class Localizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    config = self._config.get('privatizer')
    if not config:
      return STDOut(200,'no privatizer config')

    avail_entities = []
    for entity in self._entities:
      request = {
        'entity':entity,
        'config':config,
      }
      if self._handle(request):
        avail_entities.append(entity)
      else:
        # mark the invalid mat to the DB
        self._mark(entity)
    
    self._request['entities'] = avail_entities
    stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are unlocalized')
    self._log(stdout)
    return stdout

  def _handle(self,request:dict)->bool:
    try:
      downloader = Downloader(request)
      formatter = Formatter(request)
      downloader.set_next(formatter)
      downloader.handle()
      return True
    except Exception as e:
      self._logger.warning(f'localize error: {e}')
      return False

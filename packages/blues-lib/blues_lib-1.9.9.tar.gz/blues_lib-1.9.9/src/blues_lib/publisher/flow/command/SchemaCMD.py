import sys,os,re

from blues_lib.type.executor.Command import Command
from blues_lib.schema.factory.LoginerSchemaFactory import LoginerSchemaFactory
from blues_lib.schema.factory.PublisherSchemaFactory import PublisherSchemaFactory

class SchemaCMD(Command):

  name = __name__

  def execute(self):
    loginer_stereotype = self._context['publisher']['stereotype'].get('loginer')
    loginer_mode = loginer_stereotype['basic'].get('mode')
    loginer_schema = LoginerSchemaFactory(loginer_stereotype).create(loginer_mode)
    if not loginer_schema:
      raise Exception('[Publisher] Failed to create the loginer schema!')

    executor_stereotype = self._context['publisher']['stereotype'].get('executor')
    executor_mode = executor_stereotype['basic'].get('mode')
    executor_schema = PublisherSchemaFactory(executor_stereotype).create(executor_mode)
    if not executor_schema:
      raise Exception('[Publisher] Failed to create the executor schema!')

    self._context['publisher']['schema'] = {
      'loginer':loginer_schema,
      'executor':executor_schema,
    }
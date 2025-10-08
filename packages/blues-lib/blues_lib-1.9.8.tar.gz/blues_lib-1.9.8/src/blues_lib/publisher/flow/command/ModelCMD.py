import sys,os,re

from blues_lib.type.executor.Command import Command
from blues_lib.model.MaterialModel import MaterialModel

class ModelCMD(Command):

  name = __name__

  def execute(self):
    executor_schema = self._context['publisher']['schema'].get('executor')
    material = self._context['publisher'].get('material')
    model = MaterialModel(executor_schema,material).first()
    # override the placeholder schema
    model_schema = model.get('schema')

    if not model_schema:
      raise Exception('[Publisher] Failed to create a model publishing schema!')

    self._context['publisher']['schema']['executor'] = model_schema 

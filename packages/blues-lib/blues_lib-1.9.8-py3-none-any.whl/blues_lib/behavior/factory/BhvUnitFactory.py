from typing import Any
import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model

from blues_lib.behavior.unit.Row import Row
from blues_lib.behavior.unit.Richtext import Richtext


class BhvUnitFactory(Factory):
  def __init__(self,model:Model,browser=None):
    self._model = model
    self._browser = browser

  def create_row(self):
    return Row(self._model,self._browser)
  
  def create_richtext(self):
    return Richtext(self._model,self._browser)

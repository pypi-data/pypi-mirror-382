import sys,os,re

from blues_lib.dao.sql.TableMutator import TableMutator

class MatMutator(TableMutator):
  
  _TABLE = 'ap_mat'

  def __init__(self) -> None:
    super().__init__(self._TABLE)
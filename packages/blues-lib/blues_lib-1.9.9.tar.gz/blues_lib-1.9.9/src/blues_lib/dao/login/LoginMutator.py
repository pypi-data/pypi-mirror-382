import sys,os,re

from blues_lib.dao.sql.TableMutator import TableMutator

class LoginMutator(TableMutator):
  
  _TABLE = 'naps_loginer'

  def __init__(self) -> None:
    super().__init__(self._TABLE)



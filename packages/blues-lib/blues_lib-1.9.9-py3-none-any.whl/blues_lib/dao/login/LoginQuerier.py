import sys,os,re

from blues_lib.dao.sql.TableQuerier import TableQuerier

class LoginQuerier(TableQuerier):

  _TABLE = 'naps_loginer'

  def __init__(self) -> None:
    super().__init__(self._TABLE)

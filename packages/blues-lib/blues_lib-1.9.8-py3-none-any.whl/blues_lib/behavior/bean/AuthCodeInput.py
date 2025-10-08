import sys,os,re

from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.behavior.Bean import Bean
from blues_lib.dao.login.LoginQuerier import LoginQuerier
from blues_lib.type.model.Model import Model
from blues_lib.type.output.STDOut import STDOut

class AuthCodeInput(Bean):

  def _set(self)->bool:
    code = self._config['value']
    if not code or code == '__sentinel__':
      code = self._get()

    if not code:
      self._logger.error(f'[{self.__class__.__name__}] Failed to fetch the auth code')
      return False

    stdout = self._input(code)
    
    if stdout.code==200:
      self._logger.info(f'[{self.__class__.__name__}] Managed to fetch and input the auth code - {code}')
      return True
    else:
      self._logger.error(f'[{self.__class__.__name__}] Failed to input the auth code - {code} - {stdout.message}')
      return False

  def _input(self,code)->STDOut:
    from blues_lib.behavior.BhvExecutor import BhvExecutor

    resetable = self._config.get('resetable',False)
    input_conf = {
      '_kind':'reset_char' if resetable else 'write_char',
      'target_CS_WE':self._config.get('target_CS_WE'),
      'value':code,
    }

    model = Model(input_conf)
    executor = BhvExecutor(model,self._browser)
    return executor.execute()

  def _get(self)->str:
    '''
    Wait the code upload and continue
    '''
    step = 10
    code_expire = self._config.get('code_expire',300)
    domain = self._config.get('domain')
    ts = self._config.get('timestamp')
    steps =  list(range(0,code_expire,step)) 
    i = 0
    for s in steps:
      i+=1
      
      if code := self._get_code(domain,ts):
        return str(code) # must be a str

      BluesDateTime.count_down({
        'duration':step,
        'title':f'[{self.__class__.__name__}] Wait for the auth code {i*step}/{code_expire} - {domain} {ts}'
      })
    return ''

  def _get_code(self,domain,ts)->str:
    conditions = [
      {'field':'login_ts','comparator':'=','value':ts},
      {'field':'login_site','comparator':'=','value':domain},
    ]
    querier = LoginQuerier()
    stdout:STDOut = querier.get('*',conditions)
    data = stdout.data
    return data[0]['login_sms_code'] if data else ''


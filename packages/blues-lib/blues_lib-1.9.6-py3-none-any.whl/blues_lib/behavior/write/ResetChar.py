import random,time
from blues_lib.behavior.write.Write import Write

class ResetChar(Write):

  _set_keys = ['target_CS_WE','value','parent_CS_WE','timeout']

  def _set(self)->any:
    # clear the input and input a new char
    value:str = str(self._config.get('value'))  or ''
    scope:list[int|float] = self._get_interval_scope([0.5,0.5])
    return self._input_char(value,scope)

  def _input_char(self,value:str,scope:list[int|float])->any:
    # 这里必须重新选择元素，应对豆包登录，输入一个字符后元素重新绘制问题
    for char in value:
      config = {
        'value':char
      }
      kwargs = self._get_kwargs(self._set_keys,config)

      # must wait some seconds, to wait the element replaced
      interval = random.uniform(*scope)
      time.sleep(interval)

      # select the element again
      if self._to_be_visible():
        # the element always only has one char
        self._browser.element.input.write(**kwargs)
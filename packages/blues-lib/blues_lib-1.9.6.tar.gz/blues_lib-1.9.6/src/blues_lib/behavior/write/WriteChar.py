from blues_lib.behavior.write.Write import Write

class WriteChar(Write):
  _set_keys = ['target_CS_WE','value','parent_CS_WE','timeout']

  def _set(self)->any:
    # select the element once and input all chars
    kwargs = self._get_kwargs(self._set_keys)
    clearable:bool = self._config.get('clearable',False)
    scope:list[int|float] = self._get_interval_scope()
    if scope:
      kwargs = {**kwargs,'interval':scope}

    if self._to_be_visible():
      if clearable:
        return self._browser.element.input.write_discontinuous(**kwargs)
      else:
        return self._browser.element.input.append_discontinuous(**kwargs)
      
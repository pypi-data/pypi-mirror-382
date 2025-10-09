from blues_lib.behavior.write.Write import Write

class WriteText(Write):

  _set_keys = ['target_CS_WE','value','parent_CS_WE','timeout']

  def _set(self)->any:
    kwargs = self._get_kwargs(self._set_keys)
    clearable:bool = self._config.get('clearable',False)
    # must wait the element visible, or can't use the send_keys method
    if self._to_be_visible():
      if clearable:
        return self._browser.element.input.write(**kwargs)
      else:
        return self._browser.element.input.append(**kwargs)
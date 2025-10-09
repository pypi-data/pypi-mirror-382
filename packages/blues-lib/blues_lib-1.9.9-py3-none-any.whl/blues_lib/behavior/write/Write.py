from blues_lib.behavior.Bean import Bean

class Write(Bean):

  def _get_interval_scope(self,dft_scope:int|float|list[int|float]|None=None)->list[int|float]:
    interval:int|float|list[int|float]|None = self._config.get('interval')
    if not interval:
      return dft_scope

    if isinstance(interval,list):
      if len(interval) >= 2:
        return interval
      else:
        return [interval,interval]

    return [interval,interval]



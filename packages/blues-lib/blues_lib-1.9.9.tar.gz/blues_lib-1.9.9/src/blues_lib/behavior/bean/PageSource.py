from blues_lib.behavior.Bean import Bean

class PageSource(Bean):

  def _get(self)->str:
    self._scroll_to_bottom()
    return self._browser.interactor.document.get_page_source()
  
  def _scroll_to_bottom(self):
    # 必须先滚动到底部，确保滚动懒加载资源更新，例如图片，只滚动4次
    scroll_conf=self._config.get('scroll') or {}
    step = scroll_conf.get('step') or 1000
    interval = scroll_conf.get('interval') or 1000
    # 必须至少滚2次/2秒，因为之前名没有设置其他等待或检查
    max_step = scroll_conf.get('max_step') or 2
    self._browser.script.javascript.lazy_scroll_bottom(step,interval,max_step)
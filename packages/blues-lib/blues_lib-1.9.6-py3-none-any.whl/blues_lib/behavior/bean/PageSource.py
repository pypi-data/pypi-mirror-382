from blues_lib.behavior.Bean import Bean

class PageSource(Bean):

  def _get(self)->str:
    return self._browser.interactor.document.get_page_source()
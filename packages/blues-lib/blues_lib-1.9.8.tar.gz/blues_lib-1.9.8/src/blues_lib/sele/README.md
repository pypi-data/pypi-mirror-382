# webdriver methods

## interactor

### navi
- browser.interactor.navi.open(url:str)
- browser.interactor.navi.get(url:str) # alias a the open
- browser.interactor.navi.close()
- browser.interactor.navi.quit()
- browser.interactor.navi.back()
- browser.interactor.navi.forward()
- browser.interactor.navi.refresh()

### window
- browser.interactor.window.maximize()
- browser.interactor.window.minimize()
- browser.interactor.window.fullscreen()

- browser.interactor.window.screenshot(file_path:str)

- browser.interactor.window.get_size()
- browser.interactor.window.set_size(width:int,height:int)

- browser.interactor.window.get_position()
- browser.interactor.window.set_position(x:int,y:int)

- browser.interactor.window.get_handle() -> str
- browser.interactor.window.get_handles() -> list[str]
- browser.interactor.window.get_latest_handle() -> str

- browser.interactor.window.new_window(url:str) -> str
- browser.interactor.window.new_tab(url:str) -> str

- browser.interactor.window.switch_to(handle:str)
- browser.interactor.window.switch_to_latest()
- browser.interactor.window.switch_to_default()
- browser.interactor.window.switch_to_prev()
- browser.interactor.window.switch_to_next()

### document
- browser.interactor.document.get_title() -> str
- browser.interactor.document.get_name() -> str
- browser.interactor.document.get_url() -> str
- browser.interactor.document.get_source() -> str
- browser.interactor.document.set_page_timeout(timeout:int=20)
- browser.interactor.document.set_script_timeout(timeout:int=20)
- browser.interactor.document.set_implicitly_wait(timeout:int=20)

### frame
- browser.interactor.frame.switch_to(target_CS_WE:str) -> bool
- browser.interactor.frame.switch_to_default() -> bool
- browser.interactor.frame.switch_to_parent() -> bool
- browser.interactor.frame.execute(target_CS_WE,func) -> Any


## element
### finder
- browser.element.finder.find(target_CS_WE:str) -> WebElement
- browser.element.finder.find_all(target_CS_WE:str) -> list[WebElement]
- browser.element.finder.find_by_link(text:str) -> WebElement
- browser.element.finder.find_by_partial_link(text:str) -> WebElement
- browser.element.finder.above(target_CS_WE:str,anchor_cs:str) -> WebElement
- browser.element.finder.below(target_CS_WE:str,anchor_cs:str) -> WebElement
- browser.element.finder.left(target_CS_WE:str,anchor_cs:str) -> WebElement
- browser.element.finder.right(target_CS_WE:str,anchor_cs:str) -> WebElement
- browser.element.finder.near(target_CS_WE:str,anchor_cs:str) -> WebElement

### xpath_finder
- browser.element.xpath_finder.find(target_xpath:str,parent_element:WebElement) -> WebElement
- browser.element.xpath_finder.find_all(target_xpath:str,parent_element:WebElement) -> list[WebElement]


### info
- browser.element.info.get_attr(target_CS_WE:str,key:str) -> str
- browser.element.info.get_value(target_CS_WE:str) -> str
- browser.element.info.get_text(target_CS_WE:str) -> str
- browser.element.info.get_html(target_CS_WE:str) -> str
- browser.element.info.get_outer_html(target_CS_WE:str) -> str
- browser.element.info.get_tag_name(target_CS_WE:str) -> str
- browser.element.info.get_css(target_CS_WE:str,key:str) -> str
- browser.element.info.get_size(target_CS_WE:str) -> dict
- browser.element.info.get_position(target_CS_WE:str) -> dict


### state
- browser.element.state.is_presence(target_CS_WE:str) -> bool
- browser.element.state.is_displayed(target_CS_WE:str) -> bool
- browser.element.state.is_enabled(target_CS_WE:str) -> bool
- browser.element.state.is_selected(target_CS_WE:str) -> bool



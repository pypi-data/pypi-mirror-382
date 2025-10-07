## Not found
1. `NoSuchElementException`
  - 定位器错误
  - 元素还未渲染
  - 页面出错，未渲染

2. `NoSuchFrameException`
  - 目标frame不存在
    ```py
    self.driver.switch_to.frame(locator)
    ```

3. `NoSuchWindowException`
  - 目标window不存在
    ```py
    self.driver.switch_to.window(handler_id)
    ```

4. `NoAlertPresentExcepton`
  - alert不存在
    ```py
    self.driver.switch_to.alert
    ```

## Error state
1. `ElementNotVisibleException` 存在但不可见
  - 元素在窗口外
  - 元素是隐藏的
  - 元素被覆盖
  - 元素尺寸太小

2. `InvalidElementStateException`
  - 当前状态不适合当前操作，例如给disabled状态input框输入

3. `WebDriverException` Chrome私有，元素无法被点击
   - 元素被覆盖
   - 元素还未被渲染


## Reference error
1. `StaleElementReferenceException`
  - Dom被重新渲染，之前的引用失效
  - 使用`stalenessOf`等待引用元素被销毁

## System error
1. `UnsupportedCommandException`
  - WebDriver不支持当前调用的API

2. `UnreachableBrowserException` WebDriver无法被连接
  - 浏览器未启动
  - 浏览器崩溃
  - 网络异常
  - debug模式的地址或端口错误

3. `SessionNotFoundException` 之前连接正常的WebDriver失效
  - 浏览器崩溃
  - driver已经退出
## 自动查找 Chrome 执行文件路径
Selenium 之所以不需要显式设置 binary_location 参数也能找到 Chrome 执行文件，是因为它会遵循一套自动查找规则，这依赖于操作系统的默认应用程序路径和环境变量配置。具体规则如下：
1. 依赖操作系统的默认安装路径
不同操作系统对应用程序有默认的安装目录规范，Selenium 会自动扫描这些常见路径：
Windows：通常检查 C:\Program Files\Google\Chrome\Application\chrome.exe 或 C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
macOS：检查 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome（就是你之前用到的路径）
Linux：检查 /usr/bin/google-chrome 或 /usr/local/bin/google-chrome 等
2. 依赖系统的环境变量（PATH）
如果 Chrome 安装在非默认路径，但已将其可执行文件路径添加到系统的 PATH 环境变量中，Selenium 也能通过搜索 PATH 找到它。
例如，在 macOS 或 Linux 中，若 PATH 包含 Chrome 可执行文件的目录，终端输入 google-chrome 能启动浏览器，Selenium 也能同理找到。
3. 依赖浏览器驱动（chromedriver）的关联
Selenium 启动 Chrome 时，会通过 chromedriver（Chrome 驱动）间接查找浏览器。chromedriver 本身也会遵循上述路径规则，甚至会优先匹配与自己版本兼容的 Chrome 可执行文件。
什么时候需要手动设置 binary_location？
Chrome 安装在非默认路径（如自定义目录、便携版 Chrome）
系统中安装了多个 Chrome 版本，需要指定特定版本
环境变量配置有误，导致自动查找失败
大多数情况下，默认安装的 Chrome 不需要手动设置，Selenium 能通过上述规则自动定位。
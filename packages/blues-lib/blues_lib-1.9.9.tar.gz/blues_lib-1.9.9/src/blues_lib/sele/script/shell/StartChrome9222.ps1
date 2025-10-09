# Close all alive Chrome process
Stop-Process -Name 'chrome' -Force -ErrorAction SilentlyContinue

# 启动 Chrome 并设置调试端口
$chromePath = 'C:\Program Files\Google\Chrome\Application\chrome.exe' 
$argList = @(
  # debug 
  '--remote-debugging-address=0.0.0.0',
  '--remote-debugging-port=9222',

  # 窗口设置
  '--start-maximized', # 启动浏览器时最大化窗口。在自动化测试中，最大化窗口可以确保页面元素完全可见，避免因分辨率问题导致的元素定位失败。
  
  # 安全设置
  '--ignore-ssl-errors', # 忽略 SSL 证书错误。在测试或爬虫中，访问使用自签名证书的网站时使用。
  # '--ignore-certificate-errors', # cmd don't support 忽略证书错误。在测试或爬虫中，访问使用无效证书的网站时使用。
  '--disable-web-security', # 禁用同源策略（用于测试跨域请求）。
  '--allow-running-insecure-content', # 允许运行不安全的内容。

  # 性能设置
  '--disable-extensions', # 禁用所有 Chrome 扩展程序。在测试中，避免扩展程序干扰浏览器行为。
  '--disable-extensions-api', # 禁用 Chrome 扩展程序的 API。在测试中，避免扩展程序干扰浏览器行为。
  '--disable-popup-blocking', # 禁用浏览器的弹出窗口阻止功能。在测试需要弹出窗口的功能时使用，如广告或登录窗口。
  '--disable-dev-shm-usage', # 禁用 /dev/shm 的使用（适用于 Docker 或内存受限环境）。

  # 自动化相关设置
  #'--disable-blink-features=AutomationControlled', # 禁用自动化控制检测（避免被网站识别为自动化工具）。
  '--disable-infobars', # 隐藏 Chrome 顶部的“Chrome 正受到自动测试软件控制”提示栏。在自动化测试中，避免提示栏干扰页面布局或测试逻辑。
  '--enable-clipboard-features=AllowDirectSAP', # 支持剪切板复制 

  # 系统通知检查类设置
  '--disable-notifications', # 禁用浏览器的通知功能。在测试或爬虫中，避免网站弹出通知干扰操作。
  '--hide-crash-restore-bubble', # 隐藏浏览器崩溃后恢复页面的提示气泡。在自动化测试中，避免崩溃恢复提示干扰测试逻辑。
  '--disable-application-install-prompt', # 禁用应用安装提示。在测试中，避免网站提示安装应用干扰测试流程。
  '--no-first-run', # 跳过 Chrome 的首次运行向导。在自动化测试中，避免首次运行向导干扰测试流程。
  '--disable-first-run-ui', # 禁用首次运行时的用户界面（如欢迎页面）。在自动化测试中，避免首次运行界面干扰测试流程。
  '--no-default-browser-check', # 禁止 Chrome 检查是否设置为默认浏览器。在自动化测试中，避免浏览器弹出提示框干扰测试流程。
  '--disable-default-apps', # 禁用默认应用。
  '--disable-geolocation', # 禁用地理位置请求
  '--disable-save-password-bubble', # 禁用保存密码提示
  '--disable-translate', # 禁用翻译提示

  # 环境兼容设置 
  '--disable-gpu' # 禁用 GPU 加速，避免某些环境下的兼容性问题。在无头模式下运行时，某些系统可能会报错，禁用 GPU 可以规避这些问题。
  # '--no-sandbox' # cmd don't support this arg禁用沙盒模式，避免某些环境下的权限问题。在 Linux 或 Docker 环境中运行时，沙盒模式可能会导致浏览器无法启动。
)
$args = $argList -join ' '

# Write-output $args
Start-Process $chromePath -ArgumentList $args

# PlaywrightInstaller
手动安装：
```
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
uv run playwright install chromium
```
得到路径：
```
# windows示例
C:\Users\BluesLiu\AppData\Local\ms-playwright\chromium-1187\chrome-win\chrome.exe
```
查看build版本号与chromiumVersion版本对照关系(在playwright安装目录下)
```
.venv\Lib\site-packages\playwright\driver\package\browser\chromium\builds\browsers.json
```
- chromium-1187 是 Playwright 团队测试通过的一个稳定版本
- 它对应的 Chromium 版本是：140.0.7339.16（发布于 2025 年初）
- 这个版本是 Playwright 1.44 ~ 1.45 系列锁定的版本

可以依赖这种稳定性，只要满足以下条件：
- 不升级 playwright 包
- 不手动执行 playwright install，不升级playwright不会重新安装
- 不手动删除 ~/.cache/ms-playwright/ 或 %LOCALAPPDATA%\ms-playwright\，不升级playwright重新按照还是之前的版本

```json
"chromium": {
  "1187": {
    "revision": 1187,
    "downloads": {
      "chromium": {
        "url": "https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1187/chromium-win64.zip",
        "size": 156123456
      }
    },
    "chromiumVersion": "140.0.7339.16"
  }
}
```

下载对应版本`140.0.7339.16`的chromedriver
- 从 Chrome 115 开始，chromedriver 的版本号与 Chrome 版本号完全一致
```
https://chromedriver.storage.googleapis.com/index.html?path=140.0.7339.16/
https://registry.npmmirror.com/binary.html?path=chromedriver/
```


# 如果配置不生效
```
WDM - ====== WebDriver manager ======
WDM - Get LATEST chromedriver version for google-chrome
WDM - Get LATEST chromedriver version for google-chrome
WDM - There is no [win64] chromedriver "140.0.7339.207" for browser google-chrome "140.0.7339" in cache
WDM - Get LATEST chromedriver version for google-chrome
WDM - WebDriver version 140.0.7339.207 selected
WDM - Modern chrome version https://storage.googleapis.com/chrome-for-testing-public/140.0.7339.207/win32/chromedriver-win32.zip
WDM - About to download new driver from https://storage.googleapis.com/chrome-for-testing-public/140.0.7339.207/win32/chromedriver-win32.zip
```

# 如果发现本地有可用缓存
```
WDM - ====== WebDriver manager ======
WDM - Get LATEST chromedriver version for google-chrome
WDM - Get LATEST chromedriver version for google-chrome
WDM - Driver [C:\Users\BluesLiu\.wdm\drivers\chromedriver\win64\140.0.7339.207\chromedriver-win32/chromedriver.exe] found in cache
```
## WebDriver
Selenium对浏览器的操作需要 webdriver 的支持：
1. webdriver是exe程序，并不是python包，需要单独下载或安装
  - 下载地址：https://blog.csdn.net/mingfeng4923/article/details/130989513
  - 官方地址：https://googlechromelabs.github.io/chrome-for-testing/
  - 下载的driver是一个单文件，例如：`chromedriver.exe`，所以很方便迁移位置
2. 不同浏览器有不同的 webdriver，例如chrome的是`chromedriver.exe`
3. webdriver要与浏览器版本一致，比如chrome经常自动升级，可能导致旧的webdriver失效，需要安装新版

## WebDriver使用
有三种方式，已将driver下载到：
```py
driver_path = r'D:\devsoftware\Python38\webdriver\chrome\121.0.6167.85\chromedriver.exe'
```

##### 环境变量
1. 将`chromedriver.exe`所在目录添加到系统环境变量`path`
2. 将其直接放在python安装目录下 `D:\devsoftware\Python38\chromedriver.exe` (假设python安装目录已设置到环境变量`path`中)
3. 这样在实例化时，不需要显示指出其位置
```py
from selenium import webdriver
self.driver = webdriver.Chrome( options = chrome_options)
```

##### 本地文件
1. 将驱动文件下载到本地目录
2. 不依赖环境变量，直接将其绝对路径作为参数传入
```py
from selenium import webdriver
self.driver = webdriver.Chrome( service = driver_path, options = chrome_options)
```

##### 动态安装
1. 不提前安装，每次启动动态检查安装
2. 工程迁移性好，不依赖外部exe文件
3. 每次启动都要检查或更新，启动很慢（受限于国内下载速度）
```py
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
self.driver = webdriver.Chrome( service = ChromeDriverManager().install(), options = chrome_options)
```

## headless browser
1. 2017.8.5 PhantomJS停止维护
2. selenium 3.8.1 弃用 PhantomJS
3. selenium 推荐使用 官方Chrome或Firefox headless模式
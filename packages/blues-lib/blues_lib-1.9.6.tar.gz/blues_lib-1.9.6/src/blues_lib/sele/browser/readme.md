### Download webdriver
- chrome v125+ `https://googlechromelabs.github.io/chrome-for-testing/#stable` #只有少量最新版本
- chrome v114- `https://chromedriver.storage.googleapis.com/index.html`
- selenium默认值支持 firefox，可以不下载驱动
- 也可以为firefox下载最新的 `geckodriver`

下载解压后得到`chromedriver.exe`
- 直接放在python安装目录`scripts`下（例如：`D:\devsoftware\Python38\Scripts`）,会默认获取，实例化webdriver时不用传地址参数

#### Using parameter
Put chromedriver `D:\devsoftware\Python38\webdriver\chrome\128.0.6613.86\chromedriver.exe`


### Default Mode
- 无论是否quit，甚至手动关闭浏览器，登录信息都无法保存

### Debug Mode
- 无法通过 `--no-first-run` 关闭首次打开弹出的 广告隐私设置弹框
- 不要通过`driver.quit`关闭浏览器，否则会无法保存用户登录状态，直接用PS脚本关闭进程
- 有些网站必须手动勾选 remember me，否则关闭浏览器后会自动清空登录信息

### Proxy Mode
- 手动打开tab页，无法连接访问访问页面（代理导致）
- 登录后获取cookie，并保存，然后关闭浏览器 （登录信息一般都设置了 http only，selenium无法直接获取用户登录信息cookie）
- 重新用 default mode打开，并添加cookie

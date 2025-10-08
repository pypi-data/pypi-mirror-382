import os
import platform
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

class PlaywrightInstaller:
    # 国内镜像地址
    __PLAYWRIGHT_MIRROR = "https://npmmirror.com/mirrors/playwright"

    @classmethod
    def install(cls) -> str:
        """使用uv命令安装Playwright浏览器
        以下场景会重新安装：
        1. Playwright 升级了，需要新版本浏览器
        2. 手动删除了 ms-playwright 缓存目录
        3. 强制执行 playwright install --force-deinstall
        
        Playwright 是按“build 版本号”管理浏览器的，不是按 Chrome 官方版本号。
        Chromium 140.0.7339.16 (playwright build v1187)
        Returns:
            str: Chrome浏览器的可执行路径
        """
        try:
            # 设置国内镜像环境变量
            os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = cls.__PLAYWRIGHT_MIRROR
            
            print(f"正在通过Playwright下载Chrome (使用镜像: {cls.__PLAYWRIGHT_MIRROR})...")

            # 直接使用uv命令安装，因为用户确认此命令在其环境中可用
            print("使用uv命令安装chromium...")
            subprocess.run(
                "uv run playwright install chromium",
                env=os.environ.copy(), check=True, shell=True)
            
            # 获取浏览器可执行路径
            with sync_playwright() as p:
                browser_type = p.chromium
                chrome_path = browser_type.executable_path
            
            print(f"Chrome安装成功，路径: {chrome_path}")
            
            return chrome_path
            
        except subprocess.CalledProcessError as e:
            print(f"安装失败 ❌: {e}")
            print("请手动运行: uv run playwright install chromium")
            raise
        except Exception as e:
            print(f"未知错误: {e}")
            raise

    @classmethod
    def download_chrome_driver(cls, driver_version: str) -> str:
        """根据指定的版本号下载chromedriver
        
        Args:
            driver_version: ChromeDriver的版本号，如"140.0.7339.16"
            
        Returns:
            str: chromedriver的本地路径
        """
        try:
            # 设置国内镜像环境变量
            os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = cls.__PLAYWRIGHT_MIRROR
            
            print(f"正在下载ChromeDriver {driver_version} (使用镜像: {cls.__PLAYWRIGHT_MIRROR})...")
            
            # 使用Playwright的同步API下载chromium（包含对应的chromedriver）
            with sync_playwright() as p:
                browser_type = p.chromium
                browser_type.install()
            
            # 根据系统确定Playwright缓存目录
            if sys.platform == "win32":
                cache_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
            elif sys.platform == "darwin":
                cache_dir = Path.home() / "Library" / "Caches" / "ms-playwright"
            else:
                cache_dir = Path.home() / ".cache" / "ms-playwright"
            
            # 查找chromium目录
            chromium_dir = None
            for d in cache_dir.glob("chromium-*"):
                if d.is_dir():
                    chromium_dir = d
                    break
            
            if not chromium_dir:
                raise RuntimeError("未找到已下载的Chromium目录")
            
            # 根据系统拼接chromedriver路径
            if sys.platform == "win32":
                driver_path = chromium_dir / "chrome-win" / "chromedriver.exe"
            elif sys.platform == "darwin":
                driver_path = chromium_dir / "chrome-mac" / "chromedriver"
            else:
                driver_path = chromium_dir / "chrome-linux" / "chromedriver"
            
            # 验证driver文件是否存在
            if not driver_path.exists():
                raise RuntimeError(f"未找到chromedriver: {driver_path}")
            
            print(f"ChromeDriver {driver_version} 下载成功，路径: {driver_path}")
            
            return str(driver_path)
            
        except Exception as e:
            print(f"下载ChromeDriver失败: {e}")
            raise
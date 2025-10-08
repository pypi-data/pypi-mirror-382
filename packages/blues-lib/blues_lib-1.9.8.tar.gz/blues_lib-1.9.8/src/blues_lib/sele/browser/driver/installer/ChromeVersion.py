import re
import os
import platform
import subprocess

class ChromeVersion:
  @classmethod
  def get_default_path(cls) -> str:
    """Get default Chrome browser installation path based on the operating system
    
    Returns:
        str: Default Chrome browser installation path, returns empty string if cannot be found
    """
    try:
      system = platform.system().lower()
      
      if system == 'windows':
        # Windows default paths
        # Check registry for Chrome installation path
        try:
          cmd = "powershell ""(Get-ItemProperty \"HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\").'(Default)'"""
          result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
          chrome_exe_path = result.stdout.strip()
          if chrome_exe_path and os.path.exists(chrome_exe_path):
            return chrome_exe_path
        except Exception:
          pass
          
        # Try 32-bit registry path
        try:
          cmd = "powershell ""(Get-ItemProperty \"HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\").'(Default)'"""
          result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
          chrome_exe_path = result.stdout.strip()
          if chrome_exe_path and os.path.exists(chrome_exe_path):
            return chrome_exe_path
        except Exception:
          pass
          
        # Common installation paths
        common_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\Program Files'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\Program Files (x86)'), 'Google', 'Chrome', 'Application', 'chrome.exe')
        ]
        
        for path in common_paths:
          if os.path.exists(path):
            return path
            
      elif system == 'darwin':
        # macOS default paths
        common_paths = [
            '/Applications/Google Chrome.app',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            os.path.expanduser('~/Applications/Google Chrome.app')
        ]
        
        for path in common_paths:
          if os.path.exists(path):
            return path
            
      else:
        # Linux default paths
        common_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/opt/google/chrome/google-chrome'
        ]
        
        for path in common_paths:
          if os.path.exists(path):
            return path
            
    except Exception as e:
      print(f"Error getting default Chrome path: {str(e)}")
      pass
      
    return ""

  @classmethod
  def get(cls, chrome_path: str) -> str:
    """Get Chrome browser version
    
    Args:
        chrome_path: Path to Chrome browser
    
    Returns:
        str: Chrome browser version in x.x.x.x format, returns empty string if cannot be obtained
    """
    try:
      system = platform.system().lower()
      
      if system == 'windows':
        return cls._get_windows_chrome_version(chrome_path)
      elif system == 'darwin':
        return cls._get_macos_chrome_version(chrome_path)
      else:
        # For other systems, try basic method
        return cls._get_linux_chrome_version(chrome_path)

    except Exception as e:
      print(f"Error getting Chrome version: {str(e)}")
      return ""
  
  @classmethod
  def _get_windows_chrome_version(cls, chrome_path: str) -> str:
    """Get Chrome version on Windows system"""
    try:
      # Method 1: Query Chrome installation path via PowerShell
      cmd = "powershell ""(Get-ItemProperty \"HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\").'(Default)'"""
      result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
      chrome_exe_path = result.stdout.strip()
      
      if chrome_exe_path and os.path.exists(chrome_exe_path):
        # Try to get version from registry BLBeacon key
        try:
          import winreg
          with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon", 0, winreg.KEY_READ) as key:
            version = winreg.QueryValueEx(key, "version")[0]
            if version and re.match(r'\d+\.\d+\.\d+\.\d+', version):
              return version
        except Exception:
          pass
      
      # Method 2: Alternative registry path
      cmd = "powershell ""(Get-ItemProperty \"HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\").'(Default)'"""
      result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
      chrome_exe_path = result.stdout.strip()
      
      if chrome_exe_path and os.path.exists(chrome_exe_path):
        try:
          import winreg
          with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon", 0, winreg.KEY_READ) as key:
            version = winreg.QueryValueEx(key, "version")[0]
            if version and re.match(r'\d+\.\d+\.\d+\.\d+', version):
              return version
        except Exception:
          pass
      
      # Method 3: Check version folders in common installation directories
      common_paths = [
          os.path.join(os.environ.get('ProgramFiles', 'C:\Program Files'), 'Google', 'Chrome', 'Application'),
          os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\Program Files (x86)'), 'Google', 'Chrome', 'Application')
      ]
      
      for path in common_paths:
        if os.path.exists(path):
          for item in os.listdir(path):
            if re.match(r'\d+\.\d+\.\d+\.\d+', item) and os.path.isdir(os.path.join(path, item)):
              return item
      
      # Method 4: Use wmic command to get file version information
      try:
        cmd = f'wmic datafile where name="{chrome_path.replace("\\", "\\\\")}" get Version /value'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        version_line = result.stdout.strip()
        version_match = re.search(r'Version=(\d+\.\d+\.\d+\.\d+)', version_line)
        if version_match:
          return version_match.group(1)
      except Exception:
        pass
      
    except Exception:
      pass
      
    return ""
  
  @classmethod
  def _get_macos_chrome_version(cls, chrome_path: str) -> str:
    """Get Chrome version on macOS system"""
    try:
      # Check if it's an application bundle
      if chrome_path.endswith('.app'):
        cmd = f'mdls -name kMDItemVersion "{chrome_path}"'  # For .app bundle
      else:
        # For executable path
        app_path = os.path.join(os.path.dirname(os.path.dirname(chrome_path)), 'Info.plist')
        if os.path.exists(app_path):
          cmd = f'/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "{app_path}"'  # Read plist file
        else:
          cmd = f'"{chrome_path}" --version'  # As last option
          
      result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
      version_line = result.stdout.strip()
      
      # Extract version number
      version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
      if version_match:
        return version_match.group(0)
      
      # Try other possible version formats
      version_match = re.search(r'\d+\.\d+\.\d+', version_line)
      if version_match:
        # Add fourth number to maintain consistent format
        return version_match.group(0) + '.0'
    except Exception:
      pass
      
    return ""
  
  @classmethod
  def _get_linux_chrome_version(cls, chrome_path: str) -> str:
    """Get Chrome version on Linux systems"""
    try:
      # Method 1: Use --version command on the provided chrome_path
      if chrome_path and os.path.exists(chrome_path):
        cmd = f'"{chrome_path}" --version'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        version_line = result.stdout.strip() or result.stderr.strip()
        
        # Extract version number
        version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
        if version_match:
          return version_match.group(0)
      
      # Method 2: Try common Chrome executable paths
      common_paths = [
          '/usr/bin/google-chrome',
          '/usr/bin/google-chrome-stable',
          '/usr/bin/chromium',
          '/usr/bin/chromium-browser'
      ]
      
      for path in common_paths:
        if os.path.exists(path):
          cmd = f'"{path}" --version'
          result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
          version_line = result.stdout.strip() or result.stderr.strip()
          
          version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
          if version_match:
            return version_match.group(0)
      
      # Method 3: Check package manager for installed version
      # For Debian/Ubuntu based systems
      try:
        cmd = 'dpkg -l google-chrome-stable | grep ^ii'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        version_line = result.stdout.strip()
        
        # Extract version from dpkg output
        version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
        if version_match:
          return version_match.group(0)
      except Exception:
        pass
      
      # For RedHat/CentOS/Fedora based systems
      try:
        cmd = 'rpm -q google-chrome-stable --qf "%{VERSION}\n"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        version_line = result.stdout.strip()
        
        # Ensure version is in correct format
        version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
        if version_match:
          return version_match.group(0)
        else:
          # Add fourth number to maintain consistent format
          version_match = re.search(r'\d+\.\d+\.\d+', version_line)
          if version_match:
            return version_match.group(0) + '.0'
      except Exception:
        pass
      
    except Exception as e:
      print(f"Error getting Chrome version on Linux: {str(e)}")
      pass
      
    return ""
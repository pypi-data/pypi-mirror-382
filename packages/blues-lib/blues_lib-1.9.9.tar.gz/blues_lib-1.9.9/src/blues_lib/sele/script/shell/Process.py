import os
import platform

class Process:
  # 提供跨系统进程操作的方法
  
  @classmethod
  def kill_chrome(cls):
    '''
    Stop all chrome process
    @returns {int} : 0-success >0- failure
    '''
    return cls.kill('chrome')
  
  @classmethod
  def kill(cls, task_name:str):
    '''
    Stop a app's all process
    @param {str} task_name : the app's process name
    @returns {int} : 0-success >0- failure
    '''
    system = platform.system().lower()
    
    try:
      if 'windows' in system:
        # Windows system
        return os.system(f'taskkill /F /IM {task_name}.exe')
      elif 'darwin' in system:
        # macOS system
        return os.system(f'pkill -f {task_name}')
      elif 'linux' in system:
        # Linux system
        return os.system(f'pkill -f {task_name}')
      else:
        # Unsupported system
        print(f"Unsupported operating system: {system}")
        return 1
    except Exception as e:
      print(f"Error occurred while killing process: {e}")
      return 1

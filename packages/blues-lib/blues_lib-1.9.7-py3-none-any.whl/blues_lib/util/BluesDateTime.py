import time,datetime,random
from blues_lib.util.BluesConsole import BluesConsole
import random
import time
import datetime

class BluesDateTime():

  spend = 0

  @classmethod
  def get_random_seconds(cls,min_seconds: float, max_seconds: float) -> float:
    """
    生成指定范围内的随机等待时间（秒）
    
    参数:
      min_seconds (float): 最小等待时间（秒）
      max_seconds (float): 最大等待时间（秒）
      
    返回:
      float: 随机等待时间，单位为秒，介于min_seconds和max_seconds之间
    """
    # 确保最小值小于等于最大值
    if min_seconds > max_seconds:
      min_seconds, max_seconds = max_seconds, min_seconds
    
    # 生成指定范围内的随机浮点数
    return random.uniform(min_seconds, max_seconds)

  @classmethod
  def get_today(cls):
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d')

  @classmethod
  def get_time(cls):
    now = datetime.datetime.now()
    return now.strftime('%H:%M:%S')

  @classmethod
  def get_now(cls):
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

  @classmethod
  def get_timestamp(cls):
    now = datetime.datetime.now()
    return int(now.timestamp() * 1000)

  @classmethod
  def count_down(cls,payload={}):
    '''
    @description : count down
    @param {int} payload.duration  : duration seconds
    @param {int} payload.interval  : interval seconds
    @param {str} payload.title  : title
    @param {bool} payload.printable  : print in the console
    '''

    duration = int(payload.get('duration',10))
    interval = int(payload.get('interval',1))
    title = payload.get('title','coutdown')
    printable = payload.get('printable',True)

    if not duration:
      return

    if interval <=0:
      interval =1
    
    if printable: 
      BluesConsole.wait('%s : %s' % (title,duration-cls.spend))

    time.sleep(interval) 
    cls.spend+=interval
    if cls.spend < duration:
      cls.count_down(payload)
    else:
      cls.spend=0

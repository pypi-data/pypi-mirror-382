import sys,os,re
from PIL import Image

from blues_lib.type.chain.AllMatchHandler import AllMatchHandler

class Formatter(AllMatchHandler):
  # format the images' size and pad the thumb

  def resolve(self)->None:
    entity = self._request.get('entity')
    config = self._request.get('config')
    self._first_image_para = {}
    self._thumb_image = ''
    self._format_body_images(entity,config)
    self._format_thumb(entity,config)
    self._pad_body_image(entity)
    self._raise()
    
  def _raise(self):
    if not self._thumb_image:
      raise Exception('no available image found')
    
  def _pad_body_image(self,entity:dict)->None:
    if entity.get('mat_paras') and not self._first_image_para and self._thumb_image:
      entity['mat_paras'].append({
        'type':'image',
        'value':self._thumb_image,
      })
    
  def _format_thumb(self,entity:dict,config:dict)->None:
    thumb = entity.get('mat_thumb')
    if not thumb or self._is_ad_image(thumb):
      entity['mat_thumb'] = self._first_image_para.get('value')
    else:
      entity['mat_thumb'] = self._resize(thumb,config)
      
    self._thumb_image = entity['mat_thumb']

  def _format_body_images(self,entity:dict,config:dict)->None:
    max_image_count:int = int(config.get('max_image_count',-1))
    paras = entity.get('mat_paras')
    if not paras:
      return 

    new_paras = []
    image_count = 0
    for para in paras:
      # skip the text para
      if para['type'] != 'image':
        new_paras.append(para)
        continue
      
      old_image = para['value']
      if self._is_ad_image(old_image):
        continue

      # skip the image if max_image_count is reached
      if max_image_count!=-1 and image_count>=max_image_count:
        continue

      if new_image:= self._resize(old_image,config):
        new_paras.append({**para,'value':new_image})
        image_count+=1
        if not self._first_image_para:
          self._first_image_para = para
    
    entity['mat_paras'] = new_paras
      
  def _is_ad_image(self, local_image: str, max_w_h_ratio: int = 3, max_h_w_ratio: int = 3) -> bool:
    """
    通过图片的长宽比判断是否为典型的广告图
    
    参数:
        local_image: 本地图片路径
        max_w_h_ratio: 最大宽高比阈值，默认3
        max_h_w_ratio: 最大高宽比阈值，默认3
        
    返回:
        bool: 如果长宽比超过阈值则返回True（认为是广告图），否则返回False
    """
    try:
      # 打开图片并获取尺寸
      with Image.open(local_image) as img:
        width, height = img.size
        
        # 避免除以零错误
        if width == 0 or height == 0:
          return False
        
        # 计算宽高比和高宽比
        width_height_ratio = width / height  # 宽/高
        height_width_ratio = height / width  # 高/宽
        
        # 判断是否超过阈值
        if width_height_ratio > max_w_h_ratio or height_width_ratio > max_h_w_ratio:
          self._logger.info(f"图片 {local_image} 长宽比异常，宽高比: {width_height_ratio:.2f}, 高宽比: {height_width_ratio:.2f}")
          return True
        return False
        
    except FileNotFoundError:
      self._logger.error(f"错误: 找不到图片文件 {local_image}")
      return False
    except Exception as e:
      self._logger.error(f"分析图片时发生错误: {str(e)}")
      return False

  def _resize(self, local_image: str, config: dict = {}) -> str:
    """
    检查并按比例调整本地图片尺寸使其符合给定范围，统一保存为PNG格式
    参数:
        local_image: 本地图片路径
        config: 包含尺寸范围配置的字典
    返回:
        str: 处理后的图片路径
    """
    if not local_image:
      return ''

    # 从配置中获取尺寸范围，设置默认值
    max_image_width = config.get('max_image_width') or 1000
    min_image_width = config.get('min_image_width') or 500
    max_image_height = config.get('max_image_height') or 1000
    min_image_height = config.get('min_image_height') or 500
    
    # 验证配置的有效性
    if min_image_width > max_image_width:
      min_image_width = max_image_width
    if min_image_height > max_image_height:
      min_image_height = max_image_height
    
    try:
      # 打开图片
      with Image.open(local_image) as img:
        # 获取当前图片尺寸
        current_width, current_height = img.size
        
        # 计算原始宽高比
        if current_height == 0:
          return local_image  # 避免除以零错误
        original_ratio = current_width / current_height
        
        new_width, new_height = current_width, current_height
        need_resize = False
        
        # 检查是否需要调整尺寸（按比例）
        # 情况1: 宽度超出最大值
        if current_width > max_image_width:
          new_width = max_image_width
          new_height = int(new_width / original_ratio)
          need_resize = True
        
        # 情况2: 高度超出最大值（在情况1调整后可能出现）
        if new_height > max_image_height:
          new_height = max_image_height
          new_width = int(new_height * original_ratio)
          need_resize = True
        
        # 情况3: 宽度小于最小值
        if current_width < min_image_width:
          new_width = min_image_width
          new_height = int(new_width / original_ratio)
          need_resize = True
        
        # 情况4: 高度小于最小值（在情况3调整后可能出现）
        if new_height < min_image_height:
          new_height = min_image_height
          new_width = int(new_height * original_ratio)
          need_resize = True
        
        # 处理特殊情况：如果一个边达到最小值后另一个边超过最大值，允许这种情况
        # 不需要额外处理，前面的逻辑已经允许这种情况发生
        
        # 无论是否需要调整尺寸，都处理格式
        original_format = img.format.upper() if img.format else ''
        is_png = original_format == 'PNG'
        
        # 处理图片尺寸（如果需要）
        if need_resize:
          processed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
          processed_img = img.copy()
        
        # 处理图片格式（确保为PNG）
        if not is_png:
          # 构建新的文件名（替换原扩展名）
          base, _ = os.path.splitext(local_image)
          new_path = f"{base}.png"
          
          # 保存为PNG格式
          processed_img.save(new_path, format='PNG')
          
          # 删除原文件
          os.remove(local_image)
          
          # 更新路径为新路径
          local_image = new_path
        else:
          # 如果已是PNG且尺寸需要调整，直接覆盖
          if need_resize:
            processed_img.save(local_image, format='PNG')
        
        return local_image
        
    except FileNotFoundError:
      self._logger.error(f"错误: 找不到图片文件 {local_image}")
      return ''
    except Exception as e:
      self._logger.error(f"处理图片时发生错误: {str(e)}")
      return ''
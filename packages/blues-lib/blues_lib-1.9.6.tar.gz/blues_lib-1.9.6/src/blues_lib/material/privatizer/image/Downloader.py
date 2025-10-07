from urllib.parse import urlparse
from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.material.file.MatFile import MatFile
from blues_lib.util.BluesAlgorithm import BluesAlgorithm
from blues_lib.util.BluesURL import BluesURL

class Downloader(AllMatchHandler):
  # download the images to the local

  def resolve(self)->None:
    entity = self._request.get('entity')
    self._set_thumbnail(entity)
    self._set_body_images(entity)

  def _is_http_url(self,url: str) -> bool:
    try:
      result = urlparse(url)
      # 检查 scheme 是否为 http 或 https，并且 netloc（域名）不为空
      return result.scheme in ('http', 'https') and bool(result.netloc)
    except ValueError:
      return False
    
  def _set_thumbnail(self,entity)->bool:
      # convert online image to local image，缩略图可能为空
      if url := entity.get('mat_thumb'):
        entity['mat_thumb'] = self._download(url)

  def _set_body_images(self,entity:dict)->bool:
    paras = entity.get('mat_paras')
    if not paras:
      return True # don't need to set body images

    new_paras:list[dict] = []
    for para in paras:

      # append unimage para 
      if para['type'] != 'image':
        new_paras.append(para)
        continue
      
      online_url = para['value']

      if local_file := self._download(online_url):
        new_paras.append({**para,'value':local_file})

    entity['mat_paras'] = new_paras
    return True
    
  def _download(self,url:str)->str:
    if not url:
      self._logger.warning(f'[{self.__class__.__name__}] Skip a empty url')
      return ''

    if not self._is_http_url(url):
      self._logger.warning(f'[{self.__class__.__name__}] Skip a not http url - {url}')
      return url

    entity = self._request.get('entity')
    dft_id = BluesAlgorithm.md5(entity['mat_title'])
    
    # 有限使用页面url中域名作为命名空间
    site_url = entity.get('mat_url') or url
    dft_site = BluesURL.get_main_domain(site_url) 

    site = entity.get('mat_site') or dft_site
    id = entity.get('mat_id') or dft_id
    stdout = MatFile.get_download_image(site,id,url)
    if stdout.code!=200:
      self._logger.error(f'[{self.__class__.__name__}] {stdout.message} - {stdout.data}')
      return ''
    return stdout.data

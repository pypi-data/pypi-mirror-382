import re
import re
from bs4 import BeautifulSoup, Comment
import tiktoken

class HtmlExtractor:
  
  def extract(self,html:str, includes:list[str]=[], excludes:list[str]=[])->dict[str,str|int]:
    """
    提取html的body有效内容并移除非必要属性
    这是唯一暴露的公共方法
    
    params:
     - html: 要提取的html字符串
     - includes: 可选的CSS选择器列表，用于在body之后进一步过滤内容，支持多个选择器
     - excludes: 可选的CSS选择器列表，用于排除指定的元素，在includes计算后立即执行，支持多个选择器
    
    returns: dict
     - html: 解析后的html
     - char_size： 解析后的html长度
     - token_size： 解析后的html token长度
    """
    if not html or not isinstance(html, str):
      return {"html": "", "char_size": 0, "token_size": 0}
    
    # 串行调用其他方法
    html = self._body(html, includes, excludes)
    html = self._shake(html)
    html = self._minify(html)
    
    # 计算字符长度
    char_size = len(html)
    
    # 计算token数量
    token_size = self._count_tokens(html)
    
    return {
      "html": html,
      "char_size": char_size,
      "token_size": token_size
    }
  
  def _count_tokens(self, text: str) -> int:
    """
    计算文本的token数量
    使用tiktoken库进行计算
    """
    try:
      # 使用cl100k_base编码（GPT-4、GPT-3.5-Turbo等使用的编码）
      encoding = tiktoken.get_encoding("cl100k_base")
      tokens = encoding.encode(text)
      return len(tokens)
    except Exception as e:
      # 如果出现异常，返回字符长度作为备选
      return len(text)
  
  def _filter_by_css_selectors(self, soup, css_selectors:list[str])->BeautifulSoup:
    """
    [Protected] 根据CSS选择器列表过滤HTML内容
    
    params:
     - soup: BeautifulSoup对象
     - css_selectors: CSS选择器列表
    
    returns:
     - 过滤后的BeautifulSoup对象
    """
    if not css_selectors:
      return soup
    
    try:
      # 创建一个新的BeautifulSoup对象，用于存储所有选中的元素
      new_soup = BeautifulSoup('<div></div>', 'html.parser')
      container = new_soup.div
      
      # 遍历所有选择器
      for selector in css_selectors:
        if selector:
          selected_elements = soup.select(selector)
          for element in selected_elements:
            # 克隆元素以避免修改原始文档
            container.append(element)
      
      # 如果有选中的元素，返回新的soup对象
      if len(container.contents) > 0:
        return new_soup
    except Exception as e:
      # 如果CSS选择器无效或其他错误，忽略该操作，返回原始soup对象
      pass
    
    return soup
  
  def _exclude_by_css_selectors(self, soup, css_selectors:list[str])->BeautifulSoup:
    """
    [Protected] 根据CSS选择器列表排除HTML内容
    
    params:
     - soup: BeautifulSoup对象
     - css_selectors: CSS选择器列表
    
    returns:
     - 排除指定元素后的BeautifulSoup对象
    """
    if not css_selectors:
      return soup
    
    try:
      # 遍历所有要排除的选择器
      for selector in css_selectors:
        if selector:
          # 查找所有匹配的元素并移除
          for element in soup.select(selector):
            element.decompose()
    except Exception as e:
      # 如果CSS选择器无效或其他错误，忽略该操作，返回原始soup对象
      pass
    
    return soup
    
  def _body(self,html:str, includes:list[str]=[], excludes:list[str]=[])->str:
    """
    [Protected] 提取html的body内容
    - 提取body标签内容
    - 如果提供了includes选择器列表，先使用这些选择器过滤内容
    - 如果提供了excludes选择器列表，在includes过滤后立即执行排除操作
    - 移除指定的不需要的标签：style、script、iframe、frame、canvas、svg
    - 移除所有注释
    """
    if not html or not isinstance(html, str):
      return ""
      
    # 解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取body内容，如果没有body则使用整个文档
    body = soup.body
    if body:
      soup = BeautifulSoup(str(body), 'html.parser')
    
    # 先根据CSS选择器列表过滤内容
    if includes:
      soup = self._filter_by_css_selectors(soup, includes)
    
    # 然后立即执行排除操作
    if excludes:
      soup = self._exclude_by_css_selectors(soup, excludes)
    
    # 定义需要移除的标签列表，方便统一管理和修改
    tags_to_remove = ['style', 'script', 'iframe', 'frame', 'canvas', 'svg', 'footer', 'aside']
    
    # 统一移除所有指定的标签
    for tag_name in tags_to_remove:
      for tag in soup(tag_name):
        tag.decompose()
    
    # 移除所有注释
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
      comment.extract()
    
    # 空白字符的处理将在_minify方法中进行
    return str(soup)
    
  def _shake(self,html:str)->str:
    """
    [Protected] 移除非必要属性，减少总字符数量
    - 移除所有标签内的非必要属性，例如 style class id 等
    - 保留某些必须的属性，例如 href src alt 等
    - 移除样式类标签 strong、b、i，但保留标签内的文本内容
    - 移除base64类型的img标签（src属性以data:image/开头）
    """
    if not html or not isinstance(html, str):
      return ""
      
    # 定义要保留的属性
    keep_attributes = {'href', 'src', 'alt', 'title'}
    
    # 解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除样式类标签 strong、b、i，但保留标签内的文本内容
    style_tags = ['strong', 'b', 'i']
    for tag_name in style_tags:
      for tag in soup.find_all(tag_name):
        tag.unwrap()  # 移除标签但保留内容
    
    # 移除base64类型的img标签
    for img in soup.find_all('img'):
      src = img.get('src', '')
      if src.lower().startswith('data:image/'):
        img.decompose()  # 完全移除该img标签
    
    # 遍历所有标签
    for tag in soup.find_all(True):
      # 创建一个新的字典，只保留必要的属性
      new_attrs = {}
      for attr, value in tag.attrs.items():
        if attr.lower() in keep_attributes:
          new_attrs[attr] = value
      
      # 替换属性
      tag.attrs = new_attrs
    
    # 返回清理后的HTML
    return str(soup)
    
  def _minify(self, html: str) -> str:
    """
    [Protected] 最小化HTML内容
    - 移除所有不必要的空白
    - 移除所有注释
    - 压缩标签间的空白
    """
    if not html or not isinstance(html, str):
      return ""
    
    # 移除注释
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # 压缩空白字符
    html = re.sub(r'\s+', ' ', html)
    # 移除标签间的空白
    html = re.sub(r'>\s+<', '><', html)
    # 移除首尾空白
    html = html.strip()
    
    return html
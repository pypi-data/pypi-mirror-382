from blues_lib.sele.script.javascript.JavaScript import JavaScript
from blues_lib.sele.script.shell.Shell import Shell

class Script():

  def __init__(self,driver):
    self.javascript = JavaScript(driver)
    self.shell = Shell()

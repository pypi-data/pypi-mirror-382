from blues_lib.namespace.NSEnum import NSEnum
from blues_lib.namespace.EnumNS import EnumNS

class CommandName(EnumNS):
  
  class Exception(NSEnum):
    UNSET = "command.exception.unset"
    ABORT = "command.exception.abort"
    IGNORE = "command.exception.ignore" # ignore the exception
    SKIP = "command.exception.skip" # ignore and skip to do some next command
    
  class Control(NSEnum):
    BLOCKER = "command.control.blocker"
    RETRYER = "command.control.retryer"
    PRINTER = "command.control.printer"
    
  class Type(NSEnum):
    GETTER = "command.type.getter" # just read the output
    SETTER = "command.type.setter" # set the output
    ACTION = "command.type.action" # just exec, don't update the output
    
  class Flow(NSEnum):
    ENGINE = "command.flow.engine"
    QUEUE = "command.flow.queue"
    WHILE = "command.flow.while"

  class IO(NSEnum):
    INPUT = "command.io.input"
    OUTPUT = "command.io.output"
    PREV = "command.io.prev" # 上一个flow节点的output
    PARENT = "command.io.parent" # 父flow的outout
    
  class Browser(NSEnum):
    CREATOR = "command.browser.creator"
    
  class Crawler(NSEnum):
    BASE = "command.crawler.base"
    LOOP = "command.crawler.loop"
    DEPTH = "command.crawler.depth"
    ENGINE = "command.crawler.engine"
  
  # login crawler
  class Loginer(NSEnum):
    ACTOR = "command.loginer.actor"
    CHECKER = "command.loginer.checker"
    
  # material crawler
  class Material(NSEnum):
    SINKER = "command.material.sinker"
    QUERIER = "command.material.querier"

  class Notifier(NSEnum):
    EMAIL = "command.notifier.email"
  
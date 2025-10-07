import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.executor.Command import Command
from blues_lib.namespace.CommandName import CommandName

# control
from blues_lib.command.control.Blocker import Blocker
from blues_lib.command.control.Retryer import Retryer
from blues_lib.command.control.Printer import Printer

# browser
from blues_lib.command.browser.Creator import Creator

# crawler
from blues_lib.command.crawler.Engine import Engine

# material
from blues_lib.command.material.Querier import Querier
from blues_lib.command.material.Sinker import Sinker

# notifier
from blues_lib.command.notifier.Email import Email

# --- flow command ---
# flow
from blues_lib.command.flow.Engine import Engine as FlowEngine

class CommandFactory(Factory):

  _COMMANDS:dict[str,Command] = {
    
    # control
    Blocker.NAME:Blocker,
    Retryer.NAME:Retryer,
    Printer.NAME:Printer,
    
    # browser
    Creator.NAME:Creator,
    
    # crawler
    Engine.NAME:Engine,
    
    # material
    Querier.NAME:Querier,
    Sinker.NAME:Sinker,
    
    # notifier
    Email.NAME:Email,

    # flow command
    FlowEngine.NAME:FlowEngine,
  }
  
  def __init__(self,context:dict,input:dict,id:str='') -> None:
    self._context = context
    self._input = input
    self._id = id
    
  def create(self,name:CommandName)->Command | None:
    # overide
    cmd = self._COMMANDS.get(name)
    return cmd(self._context,self._input,self._id) if cmd else None


import sys,os,re

from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.command.hook.mapping.AbsMapping import AbsMapping

class PostMapping(AbsMapping):

  POSITION = CrawlerName.Field.POST

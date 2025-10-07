import sys,os,re

from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.command.hook.mapping.AbsMapping import AbsMapping

class PrevMapping(AbsMapping):

  POSITION = CrawlerName.Field.PREV
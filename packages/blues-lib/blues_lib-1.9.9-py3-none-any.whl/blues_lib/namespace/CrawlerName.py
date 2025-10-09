from blues_lib.namespace.NSEnum import NSEnum
from blues_lib.namespace.EnumNS import EnumNS

class CrawlerName(EnumNS):
  # it's a filed level namespace

  # crawler engine
  class Engine(NSEnum):
    URL = "URL"
    FOR = "FOR"
    PAGE = "PAGE"
    NEXT_PAGE = "NEXT_PAGE"
    LOOP = "LOOP"
    MAT_LOOP = "MAT_LOOP"
    DEPTH = "DEPTH"
    HTML = "HTML"

  # static fields 
  class Field(NSEnum):
    PREV = "prev" # {dict} the prev node's config
    MAPPING = "mapping" # {dict} the mapping config

    POST = "post" # {dict} the post node's config
    PROCESSOR = "processor" # {dict} the processor config

    SUMMARY = "summary" # {dict} the info about the crawler
    # field in SUMMARY
    TYPE = "type" # {str} the type of crawler
    COUNT = "count" # {int} the count of crawler
    QUIT = "quit" # {bool} is quit the browser after crawled
    URLS = "urls" # {list[str]} the urls to crawl
    PAGES = "pages" # {list[dict]} the input list contains url and bizdata
    ENTITIES = "entities" # {list[dict]} the input list contains url field
    FOR_COUNT = "for_count" # {int} the loop count of for crawler
    LOOP_INTERVAL = "loop_interval" # {int} the interval of for crawler
    PAGE_SELECTOR = "page_selector" # {str} the selector to find the next page
    CURR_PAGE_SELECTOR = "curr_page_selector" # {str} the selector to find the current page
    MAX_PAGE_NO = "max_page_no" # {int} the max page number to crawl

    HEAD_CRAWL = "head_crawl" # {dict} the head crawler config
    FOOT_CRAWL = "foot_crawl" # {dict} the foot crawler config
    PAGE_CRAWL = "page_crawl" # {dict} the crawler meta config
    CHILD = "child" # {dict} the crawler meta config
    CHILDREN = "children" # {dict} the crawler meta config

    CRAWLER = "crawler" # {dict} the bhv executor's config
    CRAWLERS = "crawlers" # {list[dict]} the bhv executor's config
    BODY_CRAWL_META = "body_crawl_meta" # {dict} the crawler meta config

    # field in CRAWLER
    SETUP = "setup" # {dict} the setup config
    DATA = "data" # {dict} the attr to save the crawled data dict
    TEARDOWN = "teardown" # {dict} the teardown config

    # field in SETUP
    URL = "url" # {str} the url to crawl
    BEFORE_CRAWLED = "before_crawled" # {dict} the config to run before crawled
    AFTER_CRAWLED = "after_crawled" # {dict} the config to run after crawled
    BEFORE_EACH_CRAWLED = "before_each_crawled" # {dict} the config to run before each crawled
    AFTER_EACH_CRAWLED = "after_each_crawled" # {dict} the config to run after each crawled


    # field in DATA
    LOGGEDIN = "loggedin" # {bool} is logged
    CKFILE = "ckfile" # {str} is local file to save the cookie file
    
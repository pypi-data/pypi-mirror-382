from xproject.xadb import ADB
from xproject.xaliyun_oss import AliyunOSS
from xproject.xdataclasses.xaccount_dataclass import AccountDataclass
from xproject.xdbs.xmongo_db import MongoDB
from xproject.xdbs.xmysql_db import MysqlDB
from xproject.xdbs.xredis_db import RedisDB
from xproject.xfrida import Frida
from xproject.xhandler import Handler
from xproject.xlogger import get_logger, logger
from xproject.xspider.xenums.xdata_status_enum import DataStatusEnum
from xproject.xspider.xitems.xfield import Field
from xproject.xspider.xitems.xitem import Item
from xproject.xspider.xmodels.xmodel import Model
from xproject.xspider.xmodels.xsqlalchemy_model import SqlalchemyModel
from xproject.xtask import Task
from xproject.xwechat_ocr import WechatOCR

from . import scripts
from . import xadb
from . import xaliyun_oss
from . import xasyncio_priority_queue
from . import xbase64
from . import xbytes
from . import xcall
from . import xcommand
from . import xcookies
from . import xdata
from . import xdataclasses
from . import xdatetime
from . import xdbs
from . import xexceptions
from . import xfile
from . import xfrida
from . import xhandler
from . import xheaders
from . import xhtml
from . import xhttp
from . import ximage
from . import ximporter
from . import xjavascript
from . import xjson
from . import xlist
from . import xlogger
from . import xmath
from . import xmixins
from . import xnetwork
from . import xnotifier
from . import xpandas
from . import xrender
from . import xreverse
from . import xsignal
from . import xspider
from . import xsql
from . import xstring
from . import xtask
from . import xtypes
from . import xurl
from . import xvalidators
from . import xwechat_ocr

__all__ = [
    "ADB",
    "AccountDataclass",
    "AliyunOSS",
    "DataStatusEnum",
    "Field",
    "Frida",
    "Handler",
    "Item",
    "Model",
    "MongoDB",
    "MysqlDB",
    "RedisDB",
    "SqlalchemyModel",
    "Task",
    "WechatOCR",
    "get_logger",
    "logger",

    "scripts",
    "xadb",
    "xaliyun_oss",
    "xasyncio_priority_queue",
    "xbase64",
    "xbytes",
    "xcall",
    "xcommand",
    "xcookies",
    "xdata",
    "xdataclasses",
    "xdatetime",
    "xdbs",
    "xexceptions",
    "xfile",
    "xfrida",
    "xhandler",
    "xheaders",
    "xhtml",
    "xhttp",
    "ximage",
    "ximporter",
    "xjavascript",
    "xjson",
    "xlist",
    "xlogger",
    "xmath",
    "xmixins",
    "xnetwork",
    "xnotifier",
    "xpandas",
    "xrender",
    "xreverse",
    "xsignal",
    "xspider",
    "xsql",
    "xstring",
    "xtask",
    "xtypes",
    "xurl",
    "xvalidators",
    "xwechat_ocr",
]

import os

_assets_dir_name = "assets"  # noqa
ASSETS_DIR_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), _assets_dir_name)


def get_file_assets_dir_path(file_path: str, create_new_dir_path: bool = False) -> str:
    rel_path = os.path.relpath(os.path.abspath(file_path), start=ASSETS_DIR_PATH)
    new_dir_path = os.path.join(ASSETS_DIR_PATH, os.path.splitext(rel_path[3:])[0])  # 3 => ..\
    if create_new_dir_path:
        os.makedirs(new_dir_path, exist_ok=True)
    return new_dir_path


__all__ += ["get_file_assets_dir_path"]  # noqa

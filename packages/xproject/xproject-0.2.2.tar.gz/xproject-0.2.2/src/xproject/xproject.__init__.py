from xproject.xdataclasses.xaccount_dataclass import AccountDataclass

from xproject.xdbs.xmongo_db import MongoDB
from xproject.xdbs.xmysql_db import MysqlDB
from xproject.xdbs.xredis_db import RedisDB

from xproject.xspider.xitems.xfield import Field
from xproject.xspider.xitems.xitem import Item
from xproject.xspider.xmodels.xmodel import Model
from xproject.xspider.xmodels.xsqlalchemy_model import SqlalchemyModel
from xproject.xspider.xenums.xdata_status_enum import DataStatusEnum

from xproject.xhandler import Handler
from xproject.xtask import Task

from xproject.xlogger import get_logger, logger

from xproject.xaliyun_oss import AliyunOSS
from xproject.xfrida import Frida
from xproject.xadb import ADB
from xproject.xwechat_ocr import WechatOCR

# script
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
# script

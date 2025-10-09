# import os
import time
import calendar
from datetime import datetime

from ut_cli.kwargs import Kwargs
from ut_log.log import Log

from typing import Any
TyAny = Any
TyDateTime = datetime
TyTimeStamp = int
TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyPath = str

TnAny = None | Any
TnArr = None | TyArr
TnDic = None | TyDic
TnTimeStamp = None | TyTimeStamp
TnDateTime = None | TyDateTime
TnPath = None | str
TnStr = None | str


class Com:
    """
    Communication Class
    """
    cmd: TnStr = None
    sw_init: bool = False

    com_pac: TnStr = None
    nms_pac: TnStr = None
    app_pac: TnStr = None
    com_pac_path: TnPath = None
    nms_pac_path: TnPath = None
    app_pac_path: TnPath = None
    tenant: TnStr = None

    ts: TnTimeStamp
    d_timer: TyDic = {}

    Log: Any = None
    cfg: TnDic = None
    App: Any = None
    # Exit: Any = None

    @classmethod
    def init(cls, kwargs: TyDic):
        # def init(cls, cls_app, kwargs: TyDic):
        """
        initialise static variables of Com class
        """
        if cls.sw_init:
            return
        cls.sw_init = True
        cls.cmd = kwargs.get('cmd')
        cls.com_pac = kwargs.get('com_pac')
        cls.nms_pac = kwargs.get('nms_pac')
        cls.app_pac = kwargs.get('app_pac')
        cls.com_pac_path = kwargs.get('com_pac_path')
        cls.nms_pac_path = kwargs.get('nms_pac_path')
        cls.app_pac_path = kwargs.get('app_pac_path')
        cls.tenant = kwargs.get('tenant')
        cls.ts = calendar.timegm(time.gmtime())
        cls.Log = Log.sh(kwargs)
        # cls.Cfg = Cfg.sh(cls, **kwargs)
        # cls.App = App.sh(cls, **kwargs)
        # cls.Exit = Exit.sh(**kwargs)

    @classmethod
    def sh_kwargs(cls, cls_app, sys_argv) -> TyDic:
        """
        show keyword arguments
        """
        _kwargs: TyDic = Kwargs.sh(cls, cls_app, sys_argv)
        cls.init(_kwargs)
        return _kwargs

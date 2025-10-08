import importlib

from ut_dic.dic import Dic
from ut_cli.aoeq import AoEq
from ut_cli.doeq import DoEq

from typing import Any
TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyPath = str
TyTup = tuple[Any, Any]

TnDic = None | TyDic
TnTup = tuple[None | Any, None | Any]


class Kwargs:
    """
    Keyword arguments processor
    """
    @staticmethod
    def sh_t_parms_task(cls_app, d_eq: TyDic) -> TyTup:
        if hasattr(cls_app, 'd_cmd2pac'):
            _cmd = Dic.locate(d_eq, 'cmd')
            _pac = Dic.locate(cls_app.d_cmd2pac, _cmd[0])
        else:
            _pac = cls_app.__module__.split(".")[0]

        _parms_name = f"{_pac}.parms"
        _task_name = f"{_pac}.task"
        _parms = importlib.import_module(_parms_name)
        _task = importlib.import_module(_task_name)
        _t_parms_task: TyTup = (_parms.Parms, _task.Task)
        return _t_parms_task

    @classmethod
    def sh(cls, cls_com, cls_app, sys_argv: TyArr) -> TyDic:
        """
        show keyword arguments
        """
        _args = sys_argv[1:]
        _d_eq: TyDic = AoEq.sh_d_eq(_args)
        _cls_parms, _cls_task = cls.sh_t_parms_task(cls_app, _d_eq)
        if _cls_parms is not None:
            _d_parms = _cls_parms.d_parms
        else:
            _d_parms = None

        _kwargs: TyDic = DoEq.verify(_d_eq, _d_parms)
        _sh_prof = _kwargs.get('sh_prof')
        if callable(_sh_prof):
            _kwargs['sh_prof'] = _sh_prof()
        _kwargs['com'] = cls_com
        _kwargs['cls_app'] = cls_app
        _kwargs['cls_parms'] = _cls_parms
        _kwargs['cls_task'] = _cls_task

        # Get the module path of the class cls_com
        # _com_mod = sys.modules[cls_com.__module__]
        # _com_pac_path = _com_mod.__file__

        # Get the module path of the class cls_com
        # _app_mod = sys.modules[app_com.__module__]
        # _app_pac_path = _app_mod.__file__

        _com_pac = cls_com.__module__.split(".")[0]
        _com_pac_path: TyPath = str(importlib.resources.files(_com_pac))

        _nms_pac = cls_app.__module__.split(".")[0]
        _nms_pac_path: TyPath = str(importlib.resources.files(_nms_pac))

        _app_pac = _cls_parms.__module__.split(".")[0]
        _app_pac_path: TyPath = str(importlib.resources.files(_app_pac))

        _kwargs['com_pac'] = _com_pac
        _kwargs['com_pac_path'] = _com_pac_path
        _kwargs['nms_pac'] = _nms_pac
        _kwargs['nms_pac_path'] = _nms_pac_path
        _kwargs['app_pac'] = _app_pac
        _kwargs['app_pac_path'] = _app_pac_path

        return _kwargs

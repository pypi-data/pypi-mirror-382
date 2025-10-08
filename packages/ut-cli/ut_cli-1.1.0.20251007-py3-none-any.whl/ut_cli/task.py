from typing import Any

TyDic = dict[Any, Any]


class Task:
    """
    Task processor
    """
    @classmethod
    def do(cls, kwargs: TyDic) -> None:
        """
        Execute do method of Task class
        """
        _cls_task = kwargs.get('cls_task')
        if _cls_task is None:
            _msg = "Task class 'cls_task' is not defined in kwargs={kwargs}"
            raise Exception(_msg)
        _cls_task.do(kwargs)

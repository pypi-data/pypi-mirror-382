from heros import LocalHERO, LocalDatasourceHERO, PolledLocalDatasourceHERO
from .helper import get_class_by_name, log, extend_none_allowed_list

import asyncio
from abc import abstractmethod
from typing import Callable


class Factory:
    @classmethod
    def _build(cls, classname: str, arg_dict: dict, name: str, realm="heros", session_manager=None, tags:list|None=None):
        log.debug(f"building object of class {classname}")

        # if mixin classes are defined, we have to generate a modified class with the mixins
        tmp_classname = f"{classname}_HERO"
        log.debug(f"adding LocalHERO mixin to {classname} -> {tmp_classname}")

        target_class = type(
            tmp_classname,
            (
                get_class_by_name(classname),
                cls._mixin_class,
            ),
            {},
        )

        # we need to replace the constructor to call the constructor of all super classes
        target_class.__init__ = cls._get_init_replacement(classname, name, realm, session_manager,tags)

        return target_class(**arg_dict)

    @classmethod
    @abstractmethod
    def _get_init_replacement(cls, classname:str, name:str, realm:str, session_manager, tags:list|None) -> Callable:
        return


class HEROFactory(Factory):
    _mixin_class = LocalHERO

    @classmethod
    def build(cls, classname: str, arg_dict: dict, name: str, realm="heros", session_manager=None, tags:list|None = None):
        return cls._build(classname, arg_dict, name, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(cls, classname:str, name:str, realm:str, session_manager, tags:list|None) -> Callable:
        def _init_replacement(self, *args, _realm=realm, _session_manager=session_manager, _tags:list|None=None, **kwargs):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(self, name, realm = _realm, session_manager = _session_manager, tags = _tags)

        return _init_replacement


class DatasourceHEROFactory(HEROFactory):
    _mixin_class = LocalDatasourceHERO

    @classmethod
    def build(
            cls, classname: str, arg_dict: dict, name: str, observables: dict = {}, realm="heros", session_manager=None, tags:list|None=None
    ):
        cls._observables = observables
        return cls._build(classname, arg_dict, name, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(cls, classname:str, name:str, realm:str, session_manager, tags:list|None) -> Callable:
        def _init_replacement(self, *args, _realm=realm, _session_manager=session_manager, _tags:list|None=None, **kwargs):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(
                self, name, realm=_realm, session_manager=_session_manager, tags=_tags, observables=cls._observables
            )

        return _init_replacement


class PolledDatasourceHEROFactory(Factory):
    _mixin_class = PolledLocalDatasourceHERO

    @classmethod
    def build(
        cls,
        classname: str,
        arg_dict: dict,
        name: str,
        loop: asyncio.AbstractEventLoop,
        interval: float,
        observables: dict = {},
        realm="heros",
        session_manager=None,
        tags: list | None = None,
    ):
        cls._loop = loop
        cls._interval = interval
        cls._observables = observables
        return cls._build(classname, arg_dict, name, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(cls, classname:str, name:str, realm:str, session_manager, tags:list|None) -> Callable:
        def _init_replacement(self, *args, _realm=realm, _session_manager=session_manager,_tags:list|None=None, **kwargs):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(
                self,
                name,
                realm=_realm,
                loop=cls._loop,
                interval=cls._interval,
                session_manager=_session_manager,
                observables=cls._observables,
                tags = _tags,
            )

        return _init_replacement

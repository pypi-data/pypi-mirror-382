from enum import Enum, EnumMeta
from typing import Any, Dict

__all__ = ['_dict', '_Enum']


class _dict(dict):

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setattr__(self, name, value):
        super(_dict, self).__setattr__(name, value)
        super(_dict, self).__setitem__(name, value)
    
    def update(self, e: Dict = None, **f):
        dic = e or dict()
        dic.update(f)
        for key in dic:
            assert hasattr(self, key), f'unregistered key {key}'
            setattr(self, key, dic[key])

    def to_dict(self) -> Dict:
        """Convert object to ordinary dict."""
        def _iterative_dictify(__dict: Dict):
            _norm_dict = dict()
            for key, val in __dict.items():
                _key = str(key) if isinstance(key, _Enum) else key
                if isinstance(val, (_dict, dict)):
                    _norm_dict[_key] = _iterative_dictify(val)
                elif isinstance(val, list):
                    _norm_dict[_key] = [_iterative_dictify(v) if isinstance(v, _dict) else v for v in val]
                else:
                    _norm_dict[_key] = str(val) if isinstance(val, _Enum) else val
            return _norm_dict
        return _iterative_dictify(self)

    __setitem__ = __setattr__


class _EnumMeta(EnumMeta):

    def __getitem__(cls, name: str):
        if name not in cls._member_map_:
            return cls._value2member_map_.get(name)
        return cls._member_map_[name]

    def __contains__(cls, member: Enum):
        if isinstance(member, str):
            return member in cls._member_map_
        return isinstance(member, cls) and member._name_ in cls._member_map_


class _Enum(Enum, metaclass=_EnumMeta):

    def __repr__(self):
        return f'{self.name}-{self.value}'

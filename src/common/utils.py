"""Utility module.

Commonly used functions and classes are here.
"""

import textwrap
from hashlib import md5
from pprint import pprint
from datetime import datetime
from collections.abc import Iterable
from abc import ABCMeta, abstractmethod


vars_ = lambda obj: {k: v for k, v in vars(obj).items() if not k.startswith("__")}
str2dt = lambda s, format="%Y-%m-%d": datetime.datetime.strptime(s, format)
dt2str = lambda dt, format="%Y-%m-%d": dt.strftime(format)


def get_hash_id(*seeds) -> str:
    """Get hash ID from seeds"""
    seed = "-".join([str(s) for s in seeds])
    return md5(seed.encode()).hexdigest()


def dedent(s: str) -> str:
    """Dedent string."""
    return textwrap.dedent(s).strip()


def is_iterable(obj, allow_str: bool = False) -> bool:
    """Check if object is iterable."""
    result = isinstance(obj, Iterable) and not isinstance(obj, (bytes, bytearray))
    return result if allow_str else result and not isinstance(obj, str)


def pretty_print(
    title: str, content, use_pprint: bool = False, n_newlines: int = 1
) -> str:
    """Pretty print title and content."""
    title_with_sep = pretty_title(title)
    print(title_with_sep)

    if isinstance(content, str):
        if len(content) > 80:
            pprint(content) if use_pprint else print(content)
        else:
            print(content)
    else:
        pprint(content) if use_pprint else print(content)
    print(n_newlines * "\n", end="")


def pretty_title(title: str) -> str:
    """Pretty repr title and content."""
    padded = " " + title + " "
    sep_len = (80 - len(padded)) // 2
    sep = "=" * sep_len
    second_sep = sep + "=" if len(padded) % 2 else sep
    title_with_sep = f"{sep}{padded}{second_sep}"
    return title_with_sep


##################################################
# Singleton
##################################################
class SingletonBase(metaclass=ABCMeta):
    """Singleton base class.

    Example:
        class LLMManager(SingletonBase):
            @classmethod
            def _generate_instance_key(cls, model_name: str, provider: str) -> tuple:
                return (model_name, provider)

            def _init_once(self, model_name: str, provider: str) -> None:
                self.model_name = model_name
                self.provider = provider
    """

    _init = set()
    _instances = {}

    def __new__(cls, *args, **kwargs):
        instance_key = cls._generate_instance_key(*args, **kwargs)
        if instance_key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[instance_key] = instance
            instance._init_once(*args, **kwargs)
            cls._init.add(instance_key)
        return cls._instances[instance_key]

    @classmethod
    @abstractmethod
    def _generate_instance_key(cls, *args, **kwargs) -> tuple: ...

    @abstractmethod
    def _init_once(self, *args, **kwargs): ...

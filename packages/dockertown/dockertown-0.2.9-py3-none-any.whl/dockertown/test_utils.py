import random
import string
from contextlib import contextmanager
from pathlib import Path
from typing import List

from . import client_config
from .utils import PROJECT_ROOT


def random_name() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


@contextmanager
def set_cache_validity_period(x: float):
    old = client_config.CACHE_VALIDITY_PERIOD
    client_config.CACHE_VALIDITY_PERIOD = x
    yield
    client_config.CACHE_VALIDITY_PERIOD = old


def get_all_jsons(object_types: str) -> List[Path]:
    jsons_directory = PROJECT_ROOT / "tests/dockertown/components/jsons" / object_types
    return sorted(list(jsons_directory.iterdir()), key=lambda x: int(x.stem))

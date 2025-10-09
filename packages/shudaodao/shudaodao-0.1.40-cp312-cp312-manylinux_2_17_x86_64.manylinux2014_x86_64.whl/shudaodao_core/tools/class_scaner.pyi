from ..logger.logging_ import logging as logging
from typing import Any, Callable

class ClassScanner:
    @classmethod
    def find_classes(cls, package_name: str, base_class: type = ..., predicate: Callable[[type], bool] | None = None) -> dict[str, type]: ...
    @classmethod
    def find_classes_instances(cls, package_name: str, base_class: type = ..., predicate: Callable[[Any], bool] | None = None) -> dict[str, Any]: ...

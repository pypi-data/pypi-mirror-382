from ..enum.label_enum import LabelEnum as LabelEnum
from ..enum.resolve_enum import resolve_enum_field as resolve_enum_field

class EnumService:
    @classmethod
    def resolve_field(cls, data: dict, field_name: str, enum_cls: type[LabelEnum]) -> None: ...

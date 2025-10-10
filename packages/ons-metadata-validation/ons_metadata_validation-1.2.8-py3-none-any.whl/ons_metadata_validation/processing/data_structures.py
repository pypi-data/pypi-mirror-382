import attrs
import pandas as pd
from attrs.validators import ge, instance_of, optional


@attrs.define
class Fail:
    fail_type: str = attrs.field(validator=instance_of(str))
    tab: str = attrs.field(validator=instance_of(str))
    name: str = attrs.field(validator=instance_of(str))
    value: str = attrs.field(validator=optional(instance_of((int, float, str))))
    reason: str = attrs.field(validator=instance_of(str))
    cell_ref: str = attrs.field(default="", validator=instance_of(str))  # type: ignore


@attrs.define
class TabDetails:
    label_row: int = attrs.field(validator=[instance_of(int), ge(0)])
    data_row: int = attrs.field(validator=[instance_of(int), ge(0)])


@attrs.define
class DataDetails:
    path: str = attrs.field(validator=[instance_of(str)])
    md5: str = attrs.field(validator=[instance_of(str)])
    n_rows: int = attrs.field(validator=[instance_of(int)])
    schema: pd.DataFrame = attrs.field(validator=[instance_of(pd.DataFrame)])
    size: int = attrs.field(validator=[instance_of(int)], converter=int)

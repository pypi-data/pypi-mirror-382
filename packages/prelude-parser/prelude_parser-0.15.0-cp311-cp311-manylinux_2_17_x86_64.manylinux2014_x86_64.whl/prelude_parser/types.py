from datetime import date, datetime

FieldInfo = str | int | float | date | datetime | None
FlatFormInfo = list[dict[str, FieldInfo]]

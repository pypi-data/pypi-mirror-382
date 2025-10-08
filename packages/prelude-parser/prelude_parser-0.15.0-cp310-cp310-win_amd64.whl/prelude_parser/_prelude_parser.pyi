from __future__ import annotations

from datetime import datetime
from pathlib import Path

from prelude_parser.types import FlatFormInfo

__version__: str

class Value:
    by: str
    by_unique_id: str | None
    role: str
    when: datetime | None
    value: str

    def to_dict(self) -> dict: ...

class Reason:
    by: str
    by_unique_id: str | None
    role: str
    when: datetime | None
    value: str

    def to_dict(self) -> dict: ...

class Entry:
    entry_id: str
    reviewed_by: str | None
    reviewed_by_unique_id: str | None
    reviewed_by_when: datetime | None
    value: Value | None
    reason: Reason | None

    def to_dict(self) -> dict: ...

class Comment:
    comment_id: str
    value: Value | None

    def to_dict(self) -> dict: ...

class LockState:
    locked: bool
    user: str | None
    user_unique_id: str | None
    date_time_changed: datetime | None

class Field:
    name: str
    field_type: str
    data_type: str | None
    error_code: str
    when_created: datetime | None
    keep_history: bool
    lock_state: LockState | None
    entries: list[Entry] | None
    comments: list[Comment] | None

    def to_dict(self) -> dict: ...

class Category:
    name: str
    category_type: str
    highest_index: int
    fields: list[Field] | None

    def to_dict(self) -> dict: ...

class State:
    value: str
    signer: str
    signer_unique_id: str
    date_signed: datetime | None

    def to_dict(self) -> dict: ...

class Form:
    name: str
    last_modified: datetime | None
    who_last_modified_name: str | None
    who_last_modified_role: str | None
    when_created: int
    has_errors: bool
    has_warnings: bool
    locked: bool
    user: str | None
    date_time_changed: datetime | None
    form_title: str
    form_index: int
    form_group: str | None
    form_state: str
    lock_state: LockState | None
    states: list[State] | None
    categories: list[Category] | None

    def to_dict(self) -> dict: ...

class Patient:
    patient_id: str
    unique_id: str
    when_created: datetime | None
    creator: str
    site_name: str
    site_unique_id: str
    last_language: str | None
    number_of_forms: int
    forms: list[Form] | None

    def to_dict(self) -> dict: ...

class Site:
    name: str
    unique_id: str
    number_of_patients: int
    count_of_randomized_patients: int
    when_created: datetime | None
    creator: str
    number_of_forms: int
    forms: list[Form] | None

    def to_dict(self) -> dict: ...

class User:
    unique_id: str
    last_language: str | None
    creator: str
    number_of_forms: int
    forms: list[Form] | None

    def to_dict(self) -> dict: ...

class SiteNative:
    sites: list[Site]

    def to_dict(self) -> dict: ...
    def to_json(self) -> str: ...

class SubjectNative:
    patients: list[Patient]

    def to_dict(self) -> dict: ...
    def to_json(self) -> str: ...

class UserNative:
    users: list[User]

    def to_dict(self) -> dict: ...
    def to_json(self) -> str: ...

def _parse_flat_file_to_dict(
    xml_file: str | Path, *, short_names: bool = False
) -> dict[str, FlatFormInfo]: ...
def _parse_flat_file_to_pandas_dict(
    xml_file: str | Path, *, short_names: bool = False
) -> dict[str, FlatFormInfo]: ...
def parse_site_native_file(xml_file: str | Path) -> SiteNative: ...
def parse_site_native_string(xml_str: str) -> SiteNative: ...
def parse_subject_native_file(xml_file: str | Path) -> SubjectNative: ...
def parse_subject_native_string(xml_str: str) -> SubjectNative: ...
def parse_user_native_file(xml_file: str | Path) -> UserNative: ...
def parse_user_native_string(xml_str: str) -> UserNative: ...

class FileNotFoundError(Exception):
    pass

class InvalidFileTypeError(Exception):
    pass

class ParsingError(Exception):
    pass

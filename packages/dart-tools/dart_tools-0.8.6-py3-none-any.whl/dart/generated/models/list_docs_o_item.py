from enum import Enum


class ListDocsOItem(str, Enum):
    CREATED_AT = "created_at"
    FOLDER_ORDER = "folder__order"
    ORDER = "order"
    TITLE = "title"
    UPDATED_AT = "updated_at"
    VALUE_0 = "-created_at"
    VALUE_1 = "-folder__order"
    VALUE_2 = "-order"
    VALUE_3 = "-title"
    VALUE_4 = "-updated_at"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class ResponseEncoding(Enum):
    Bytes = "bytes"
    Iterator = "iterator"
    Json = "json"
    Text = "text"

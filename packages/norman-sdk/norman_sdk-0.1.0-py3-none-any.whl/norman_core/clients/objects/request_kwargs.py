from io import BufferedReader
from typing import TypedDict, Any, Union, Iterator, AsyncIterator

from aiofiles.threadpool.binary import AsyncBufferedReader

FileStream = Union[BufferedReader, AsyncBufferedReader, bytes]

class RequestKwargs(TypedDict, total=False):
    content: Union[bytes, str]
    data: Union[dict[str, Any], bytes, str]
    files: dict[str, tuple[str, FileStream, str]]
    json: Any
    params: dict[str, Any]
    stream: Union[Iterator[bytes], AsyncIterator[bytes]]

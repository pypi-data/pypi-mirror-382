import datetime
import json
from typing import Any
from uuid import UUID


class RequestClientJSONEncoder(json.JSONEncoder):
    """JSON encoder that supports UUID serialization

    Support Nan -> None if required - https://stackoverflow.com/a/71389334
    """

    def default(self, o: Any) -> Any:
        """Override JSONEncoder.default to support uuid serialization"""
        if isinstance(
            o,
            (
                datetime.datetime,
                datetime.date,
                datetime.time,
                UUID,
            ),
        ):
            return str(o)
        return super().default(o)

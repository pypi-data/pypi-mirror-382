from datetime import datetime
from typing import Any

import pytz


def human_readable_time(time: Any) -> datetime:
    if isinstance(time, datetime):
        return time
    return datetime.fromtimestamp(float(time), tz=pytz.timezone('Asia/Kolkata'))

async def async_api_handler(first_method: Any, first_method_data: Any, result_of_first_method, second_method: Any, second_method_data: Any):
    result = await first_method(first_method_data)
    if result == result_of_first_method:
        await second_method(second_method_data)

from __future__ import annotations

import calendar
from datetime import datetime, timezone
from enum import IntEnum
import pytz
from pytz import timezone
from typing import Optional, Final, Union

naive = datetime.utcfromtimestamp(None)

print(f"Type: {type(naive)}, val: {naive}")
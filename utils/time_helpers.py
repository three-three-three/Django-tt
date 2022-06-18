from datetime import datetime
import pytz


# 改成utc时区

def utc_now():
    return datetime.now().replace(tzinfo=pytz.utc)

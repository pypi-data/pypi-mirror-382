import math
from datetime import datetime


def human_readable_size(size_bytes):
    if size_bytes == 0:
        return '0B'
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s} {size_names[i]}'

def human_readable_date(dt):
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return f'{int(seconds)} seconds ago'
    elif seconds < 3600:
        return f'{int(seconds // 60)} minutes ago'
    elif seconds < 86400:
        return f'{int(seconds // 3600)} hours ago'
    return dt.strftime('%Y-%m-%d %H:%M:%S')[1]
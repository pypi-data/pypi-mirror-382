import re
import unicodedata


def slugify(text, sep=''):
    """
    >>> slugify('Foo & Bar !', sep='_')
    'Foo_Bar'
    >>> slugify('device_id', sep='_')
    'device_id'
    """
    value = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', sep, value)
    return re.sub(r'[-_\s]+', sep, value).strip(sep)

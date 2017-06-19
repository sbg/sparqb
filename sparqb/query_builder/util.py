__author__ = 'Adam Stanojevic <adam.stanojevic@sbgenomics.com>'
__date__ = '10 March 2016'
__copyright__ = 'Copyright (c) 2016 Seven Bridges Genomics'


def is_valid_short(uri):
    import re
    regex_short = re.compile(
            r'^[A-Z0-9_]*:[A-Z0-9_]+$', re.IGNORECASE)
    return uri is not None and (regex_short.fullmatch(uri) is not None)


def is_valid_url(url):
    import re
    regex_url = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+|\S+#?\S+)$', re.IGNORECASE)

    return url is not None and (regex_url.fullmatch(url) is not None)


def is_valid_uri(uri):
    return uri is not None and (is_valid_short(uri) or is_valid_url(uri))

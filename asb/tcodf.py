"""Bits for interacting with the forums."""

import urllib.parse

def parse_tcodf_url(link):
    """Parse a TCoDf URL, and make sure it's actually a TCoDf URL."""

    parsed_link = urllib.parse.urlparse(link)

    if not parsed_link.scheme:
        # Be lenient about missing schemes
        link = 'http://{}'.format(link)
        parsed_link = urllib.parse.urlparse(link)

    if parsed_link.netloc not in ['forums.dragonflycave.com',
      'tcodforums.eeveeshq.com']:
        raise ValueError('Not a TCoDf link')

    return parsed_link

def post_id(link):
    """Parse a post link and return the post ID."""

    link = parse_tcodf_url(link)
    query = urllib.parse.parse_qs(link.query)

    if link.path.startswith(('/showthread.php', '/showpost.php')):
        if 'p' not in query:
            raise ValueError('Missing post ID')
        elif len(query['p']) > 1:
            raise ValueEerror('Multiple post IDs????')

        [post_id] = query['p']
        return int(post_id)
    else:
        raise ValueError('Not a post link')

def post_link(post_id):
    """Return a post link."""

    return 'http://forums.dragonflycave.com/showpost.php?p={}'.format(post_id)

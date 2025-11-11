"""Bits for interacting with the forums."""

import logging
import json
import pathlib
import urllib.parse
import urllib.request

import pyramid.settings
import pyramid.threadlocal


_log = logging.getLogger(__name__)


def parse_tcodf_url(link):
    """Parse a TCoDf URL, and make sure it's actually a TCoDf URL."""

    parsed_link = urllib.parse.urlparse(link)

    if not parsed_link.scheme:
        # Be lenient about missing schemes
        link = 'https://{}'.format(link)
        parsed_link = urllib.parse.urlparse(link)

    if parsed_link.netloc != 'forums.dragonflycave.com':
        raise ValueError('Not a TCoDf link')

    return parsed_link


def post_id(link):
    """Parse a post link and return the post ID."""

    link = parse_tcodf_url(link)
    path = pathlib.PurePath(link.path)

    if link.fragment.startswith('post-'):
        if not path.match('/threads/*'):
            raise ValueError("Doesn't seem to be a TCoDf post link")
        post_bit = link.fragment
    else:
        if not path.match('/threads/*/post-*'):
            raise ValueError("Doesn't seem to be a TCoDf post link")
        post_bit = path.parts[3]

    post_id = post_bit.partition('-')[2]

    try:
        post_id = int(post_id)
    except ValueError as e:
        raise ValueError('Could not parse post ID number') from e

    return post_id


def post_link(post_id):
    """Return a post link."""

    # Not the canonical URL, but will redirect just fine
    return 'https://forums.dragonflycave.com/posts/{}'.format(post_id)


def thread_id(link):
    """Parse a post or thread link and return the thread ID."""

    link = parse_tcodf_url(link)
    path = pathlib.PurePath(link.path)

    # Accept thread link or post link
    if not path.match('/threads/*') or path.match('/threads/*/*'):
        raise ValueError("Doesn't seem to be a TCoDf thread link")

    thread_id = path.parts[2].rpartition('.')[2]

    try:
        thread_id = int(thread_id)
    except ValueError as e:
        raise ValueError('Could not parse thread ID number') from e

    return thread_id


def thread_link(thread_id):
    """Return a thread link."""

    # Thread title slug not needed; will redirect just fine
    return 'https://forums.dragonflycave.com/threads/{}'.format(thread_id)


def user_id(link):
    """Given a link to a user's forum profile, parse and return the user ID."""

    link = parse_tcodf_url(link)
    path = pathlib.PurePath(link.path)

    if not path.match('/members/*'):
        raise ValueError(
            'Not a valid forum profile link; should start with '
            'https://forums.dragonflycave.com/members/'
        )

    # Accept `name.12345` or just `12345` (hence rpartition)
    user_id = path.parts[2].rpartition('.')[2]

    try:
        user_id = int(user_id)
    except ValueError as e:
        raise ValueError('Could not parse user ID number') from e

    return user_id


def user_forum_link(tcodf_id):
    """Return a link to a user's forum profile."""

    # Username slug not needed; will redirect just fine
    return 'https://forums.dragonflycave.com/members/{}'.format(tcodf_id)


def user_info(tcodf_id):
    """Given a TCoDf user ID, retreive their profile via the API and return a
    dict containing just the info the ASBdb uses.
    """

    try:
        return _user_info(tcodf_id)
    except ValueError as e:
        # Let wtforms handle this
        raise e
    except Exception as e:
        _log.exception(e)
        raise ValueError('Unexpected error retrieving forum profile.')


def _user_info(tcodf_id):
    """Do the actual work for the above user_info function."""

    # XXX It would be nice to pass the request in rather than resorting to
    # get_current_request.  (The original vBulletin-era version of this
    # function didn't need the request and refactoring it to pass it in *now*
    # proved more effort than anticipated.)
    request = pyramid.threadlocal.get_current_request()

    if pyramid.settings.asbool(
        request.registry.settings.get('tcodf.test_mode')
    ):
        # Return dummy info for test mode assuming the forum agrees with what
        # we already have.  n.b. this assumes that the requested user is only
        # ever the current ASBdb user, which is true at the time of writing.
        return {
            'username': request.user.name,
            'profile_link': urllib.parse.urlparse(
                request.resource_url(request.user)
            )
        }

    api_key = request.registry.settings.get('tcodf.api_key')

    if not api_key:
        raise ValueError(
            "XenForo API key not set.  If you're seeing this message on the "
            'actual live ASBdb, tell Trinket to fix this.'
        )

    try:
        response = urllib.request.urlopen(urllib.request.Request(
            'https://forums.dragonflycave.com/api/users/{}'.format(tcodf_id),
            headers={'XF-Api-Key': api_key}
        )).read()
    except urllib.request.URLError as e:
        _log.exception(e)
        response = json.loads(e.fp.read())
        error_msg = response['errors'][0]['message']
        raise ValueError(f'The forums returned an error message: {error_msg}')

    response = json.loads(response)

    return {
        'username': response['user']['username'],
        'profile_link': urllib.parse.urlparse(
            response['user']['custom_fields'].get('asb_profile_link')
        )
    }

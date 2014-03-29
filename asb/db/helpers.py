import re
import unicodedata

def identifier(name, id=None):
    """Reduce a name to a URL-friendly yet human-readable identifier."""

    # Step one: strip out diacritics
    # XXX This won't simplify e.g. œ to oe
    identifier = ''.join(char for char in unicodedata.normalize('NFKD', name)
        if not unicodedata.combining(char))

    # Step two: convert to a bunch of alphanumeric words separated by hyphens
    identifier = identifier.lower()
    identifier = identifier.replace("'", '')
    identifier = identifier.replace('♀', '-f')
    identifier = identifier.replace('♂', '-m')
    identifier = re.sub('[^a-z0-9]+', '-', identifier)
    identifier = identifier.strip('-')

    # Step three: tack on the ID if provided
    if identifier and id is not None:
        identifier = '{0}-{1}'.format(id, identifier)
    elif id is not None:
        identifier = str(id)
    elif not identifier:
        # Hopefully-avoidable step four: oh god help we still have nothing
        raise ValueError('Name {0!r} reduces to empty identifier'.format(name))

    return identifier

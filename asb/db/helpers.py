import re
import unicodedata

# A handful of literal roman numerals, for use in roman_numeral below
roman_literals = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I')
]

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

def roman_numeral(n):
    """Return a number as a roman numeral."""

    result = []

    for number, numeral in roman_literals:
        numeral_count = n // number
        result.append(numeral * numeral_count)
        n -= number * numeral_count

    return ''.join(result)

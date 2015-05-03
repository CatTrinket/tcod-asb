"""ASB-specific Markdown customizations."""

import markdown
from pyramid.traversal import resource_path
import sqlalchemy as sqla

import asb.db as db

class NoneMarkdown(markdown.Markdown):
    """A Markdown class that will accept None and produce an empty string.

    This is useful because if a move, ability, or item has not been given an
    effect yet, its summary and description will both be None.
    """

    def convert(self, source):
        if source is None:
            return ''
        else:
            return super().convert(source)

class PokedexLinkExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('ability_link', ability_link, '>link')
        md.inlinePatterns.add('move_link', move_link, '>link')
        md.inlinePatterns.add('item_link', item_link, '>link')
        md.inlinePatterns.add('species_link', species_link, '>link')
        md.inlinePatterns.add('type_link', type_link, '>link')

class PokedexLink(markdown.inlinepatterns.Pattern):
    """A pattern to turn {tablename:thingname} into a link.

    For example, {ability:Serene Grace} will turn into a link to Serene Grace's
    page.
    """

    def __init__(self, label, table):
        """Set which table to look stuff up in and build the matching pattern,
        then do regular setup.
        """

        self.table = table

        # {label:name} with some optional whitespace
        pattern = r'({{\s*{0}\s*:\s*(.+?)\s*}})'.format(label)

        super().__init__(pattern)

    def fetch_thing(self, name):
        """Fetch the thing from the database, and return it with its name.

        The name is returned explicitly so that SpeciesLink can override this
        sqla.function and figure out whether to use the form name or species name
        for the link text.
        """

        thing = (
            db.DBSession.query(self.table)
            .filter(sqla.func.lower(self.table.name) == name.lower())
            .one()
        )

        return (thing, thing.name)

    def handleMatch(self, match):
        """Turn a pattern match into a Pokédex link."""

        name = match.group(3).strip()

        try:
            (thing, name) = self.fetch_thing(name)
        except sqla.orm.exc.NoResultFound:
            # Not a real thing; just leave the raw {label:name} alone
            return match.group(2)

        link = markdown.util.etree.Element('a')
        link.set('href', resource_path(thing))
        link.text = markdown.util.AtomicString(name)
        return link

class SpeciesLink(PokedexLink):
    def fetch_thing(self, name):
        """Try to find a Pokémon form with this name; if there isn't one, try
        to find a Pokémon species with this name.
        """

        name = name.lower()

        try:
            form = (
                db.DBSession.query(self.table)
                .filter(sqla.func.lower(self.table.full_name) == name)
                .one()
            )

            return (form, form.full_name)
        except sqla.orm.exc.NoResultFound:
            species = (
                db.DBSession.query(db.PokemonSpecies)
                .filter(sqla.func.lower(db.PokemonSpecies.name) == name)
                .one()
            )

            return (species.default_form, species.name)

def chomp(html):
    """Chomp the paragraph tags off a block of HTML.  This function is not very
    smart and will simply chop off the first three and last four characters.

    XXX There's probably some way to extend Markdown to do this more nicely
    """

    return html[3:-4]

ability_link = PokedexLink('ability', db.Ability)
item_link = PokedexLink('item', db.Item)
move_link = PokedexLink('move', db.Move)
species_link = SpeciesLink('species', db.PokemonForm)
type_link = PokedexLink('type', db.Type)

md = NoneMarkdown(extensions=[
    PokedexLinkExtension(),
    'markdown.extensions.nl2br'
])

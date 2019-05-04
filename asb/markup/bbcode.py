"""ASB-specific BBCode customizations."""

import re

import bbcode
import markupsafe

import asb.tcodf


# The main use case for this is just simple colors like "red" but I figure I
# may as well support the whole list, and including the full thing here is
# easier than installing a package just for this lol
css_colors = {
    'transparent', 'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
    'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet',
    'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral',
    'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
    'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki',
    'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred',
    'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray',
    'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
    'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite',
    'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod',
    'gray', 'green', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred',
    'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
    'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
    'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey',
    'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue',
    'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow',
    'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine',
    'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen',
    'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
    'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin',
    'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange',
    'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
    'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum',
    'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue',
    'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna',
    'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow',
    'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato',
    'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow',
    'yellowgreen'
}


class ASBBBCode(bbcode.Parser):
    """A BBCode parser that aims to mimic TCoDf's BBCode parsing."""

    def __init__(self, **kwargs):
        # Rely on white-space: pre-wrap; instead of inserting <br>s
        kwargs.setdefault('newline', '\n')

        # Don't use the default replacements ("---" to em dash, etc.)
        kwargs.setdefault('replace_cosmetic', False)

        # Don't use the default tags; a lot of them are handled differently
        kwargs.setdefault('install_defaults', False)

        super().__init__(**kwargs)
        self.add_formatters()

    def add_formatters(self):
        """Add all the formatters for the various tags."""

        self.add_simple_formatter('b', '<b>%(value)s</b>')
        self.add_simple_formatter('i', '<i>%(value)s</i>')
        self.add_simple_formatter('u', '<u>%(value)s</u>')
        self.add_simple_formatter('s', '<s>%(value)s</s>')

        for dir in ('left', 'right', 'center'):
            html = '<div style="text-align: {}">%(value)s</div>'.format(dir)
            self.add_simple_formatter(dir, html)

        self.add_simple_formatter(
            'noparse', '%(value)s', render_embedded=False)

        self.add_formatter('url', self._format_url)
        self.add_formatter('img', self._format_img, render_embedded=False)
        self.add_formatter('quote', self._format_quote,
                           swallow_trailing_newline=True)
        self.add_formatter('spoiler', self._format_spoiler)
        self.add_formatter('hide', self._format_hide,
                           swallow_trailing_newline=True)
        self.add_formatter('color', self._format_color)
        self.add_formatter('size', self._format_size)
        self.add_formatter('sprite', self._format_sprite,
                           render_embedded=False)
        self.add_formatter('list', self._format_list, strip=True,
                           swallow_trailing_newline=True)
        self.add_formatter('*', self._format_list_item, same_tag_closes=True)

    def format(self, *args, **kwargs):
        return markupsafe.Markup(super().format(*args, **kwargs))

    def _format_url(self, tag, contents, options, parent, context):
        """Handle a [url] tag.

        Examples:
        [url]https://example.com/[/url]
        [url=https://example.com/]Link text[/url]

        If the scheme is left out, default to https.  (Defaulting to http might
        work better but we'll cross that bridge when we come to it I guess?)
        """

        if 'url' in options:
            href = markupsafe.escape(options['url'].strip())            
        else:
            if contents.startswith('<a '):
                # [url]https://example.com[/url] has already been handled,
                # because it twigs as a plain URL pasted into the post body,
                # and those automatically get replaced
                return contents
            else:
                # [url]example.com[/url] still needs to be handled
                href = contents.strip()  # Already escaped

        if not href.startswith(('http://', 'https://')):
            href = 'https://{}'.format(href)

        return '<a href="{}">{}</a>'.format(href, contents)

    def _format_img(self, tag, contents, options, parent, context):
        """Handle an [img] tag.

        Examples:
        [img]https://example.com/image.png[/img]
        [img=https://example.com/image.png]Alt text[/img]
        """

        if 'img' in options:
            src = markupsafe.escape(options['img'].strip())
            alt = contents  # Already escaped
        else:
            src = contents.strip()  # Already escaped
            alt = '[BBCode image]'

        if not src.startswith(('http://', 'https://')):
            src = 'https://{}'.format(src)

        return '<img src="{}" alt="{}">'.format(src, alt)

    def _format_quote(self, tag, contents, options, parent, context):
        """Handle a [quote] tag.

        Examples:
        [quote]contents[/quote]
        [quote=name]contents[/quote]
        [quote=name;123]123 is a TCoDf post id in this example[/quote]
        """

        contents = _chomp(contents)
        html = []

        # Add header for [quote=name] or [quote=name;123]
        if 'quote' in options:
            html.append('<div class="bbcode-quote-header">Quote from <b>')

            match = re.fullmatch('(.+?)(;\d+)?', options['quote'])
            (name, post_id) = match.groups()

            if post_id is not None:
                post_id = int(post_id.lstrip(';'))
                html.append('<a href="{}">{}</a>'.format(
                    asb.tcodf.post_link(post_id),
                    markupsafe.escape(name)
                ))
            else:
                html.append(markupsafe.escape(name))

            html.append(':</b></div>')

        html.append('<blockquote>{}</blockquote>'.format(contents))

        return ''.join(html)

    def _format_spoiler(self, tag, contents, options, parent, context):
        """Handle a [spoiler] tag.

        Examples:
        [spoiler]hidden text[/spoiler]
        [spoiler=visible warning]hidden text[/spoiler]
        """

        if 'spoiler' in options:
            warning = '(SPOILER for {})'.format(
                markupsafe.escape(options['spoiler']))
        else:
            warning = '(SPOILER)'

        return '{} <span class="spoiler">{}</span>'.format(warning, contents)

    def _format_hide(self, tag, contents, options, parent, context):
        """Handle a [hide] tag.

        Examples:
        [hide]contents[/hide]
        [hide=summary]contents[/hide]
        """

        summary = options.get('hide', 'Hide/show')
        contents = _chomp(contents)

        return '<details><summary>{}</summary>{}</details>'.format(
            markupsafe.escape(summary), contents)

    def _format_color(self, tag, contents, options, parent, context):
        """Handle a [color] tag.

        Examples:
        [color=red]red[/color]
        [color=#FF0000]also red[/color]
        [color=#F00]also red[/color]
        [color=FF0000]allow missing #[/color]
        """

        if 'color' not in options:
            return contents

        color = options['color'].strip().lower()

        # Validate color
        if color not in css_colors:
            color = color.lstrip('#')
            hex_match = re.fullmatch('[0-9a-f]+', color)

            # Allow 3, 4, 6, or 8 hex digits, as CSS does
            # (either 1 or 2 digits per channel, and either RGB or RGBA)
            if hex_match is None or len(color) not in (3, 4, 6, 8):
                return contents

            color = '#{}'.format(color.upper())

        return '<span style="color: {}">{}</span>'.format(color, contents)

    def _format_size(self, tag, contents, options, parent, context):
        """Handle a [size] tag.

        Examples:
        [size=32]font-size: 32px[/size]
        [size=+1]font-size: 125%[/size]
        [size=-1]font-size: 80%[/size]
        """

        size = self._parse_size(options.get('size', ''))
        return '<span style="font-size: {}">{}</span>'.format(size, contents)

    def _parse_size(self, size):
        """Parse the size passed into _format_size."""

        # Relative size; 125% ** size up to +7
        match = re.fullmatch(r'\+(\d+)', size)
        if match is not None:
            size = min(int(match.group()), 7)
            return '{}%'.format(100 * 5 ** size // 4 ** size)

        # Negative relative size; 80% ** abs(size) down to -7
        match = re.fullmatch(r'-(\d+)', size)
        if match is not None:
            size = min(int(match(group)), 7)
            return '{}%'.format(100 * 4 ** size // 5 ** size)

        # Absolute size; interpret as pixels
        try:
            return '{}px'.format(min(int(size), 80))
        except ValueError:
            pass

        # Default
        return '100%'

    def _format_sprite(self, tag, contents, options, parent, context):
        """Handle a [sprite] tag.

        Examples:
        [sprite]meowstic[/sprite]
        [sprite=party]meowstic[/sprite]
        [sprite=party-shiny]meowstic-female[/sprite]
        [sprite=item]rare candy[/sprite]

        Anything other than "party", "party-shiny", or "item" will hotlink from
        TCoD.
        """

        sprite_set = options.get('sprite')
        name = contents.lower().strip().replace(' ', '-')

        if re.fullmatch('[a-z0-9-]+', name) is None:
            return contents
        elif sprite_set in ('party', 'party-shiny'):
            return self._format_sprite_party(name, sprite_set == 'party-shiny')
        elif sprite_set == 'item':
            url = '/static/images/items/{}.png'.format(name)
        else:
            url = ('https://www.dragonflycave.com/oldforums/images/vbsprites/'
                   '{}/{}.png'.format(sprite_set, name))

        return '<img src="{}" alt="{}">'.format(url, name)

    def _format_sprite_party(self, name, shiny):
        """Handle a Pokémon party icon.

        This returns a Pokémon icon span (see /static/icons.css).
        """

        male = False

        if not name.startswith('nidoran'):
            if name.endswith('-f'):
                name = name[:-2]
            elif name.endswith('-m'):
                name = name[:-2]
                male = True

        class_ = ['pokemon-icon', name]

        if shiny:
            class_.append('shiny')

        if male:
            class_.append('male')

        return '<span class="{}"></span>'.format(' '.join(class_))

    def _format_list(self, tag, contents, options, parent, context):
        """Handle a [list] tag.

        Example:
        [list]
            [*] 1
                [list]
                    [*] 1.1 (nested)
                    [*] 1.2
                [/list]
            [*] 2

                still part of 2
        [/list]

        This was the biggest problem I had with the default parser; it didn't
        support multi-line list items, and would just stick anything between
        list items directly into the <ul>, even though that's not allowed.
        """

        if not contents.startswith('<li>'):
            # If there's some junk at the beginning, just open a list item to
            # contain it.  It will automatically be closed by the start of the
            # next li (which is valid in HTML5).
            contents = '<li>{}'.format(contents)

        return '<ul>{}</ul>'.format(contents)

    def _format_list_item(self, tag, contents, options, parent, context):
        """Handle a [*] list item within a [list] tag."""

        if parent is None or parent.tag_name != 'list':
            return '[*]' + contents

        # Strip indentation, but otherwise keep extra spacing
        contents = '\n'.join(line.strip() for line in contents.splitlines())

        return '<li>{}</li>'.format(contents)

    def _find_closing_token(self, tag, tokens, position):
        """Find the corresponding closing token for an opening tag; handle [*]
        specially to support nested lists.
        """

        # Handle tags other than [*] as usual
        if tag.tag_name != '*':
            return super()._find_closing_token(tag, tokens, position)

        # For [*], look for the next [*] at the same level.  Skip over any
        # deeper tokens.
        length = len(tokens)

        while position < length:
            (token_type, tag_name, tag_opts, token_text) = tokens[position]

            if token_type == self.TOKEN_TAG_START:
                if tag_name == '*':
                    # Found it!
                    return (position, False)
                else:
                    # A nested tag is starting; skip to the end of it
                    (_, inner_tag) = self.recognized_tags[tag_name]
                    (position, consume) = self._find_closing_token(
                        inner_tag, tokens, position + 1)

                    if consume:
                        position += 1
            else:
                position += 1

        # If we run into the end of the list, then that's our closing position
        return (position, False)

def _chomp(contents):
    """Eat *one* leading/trailing newline and no more."""

    # This BBCode package changes all newlines to \r during processing, and
    # then back at the end; I don't know why.
    if contents.startswith('\r'):
        contents = contents[1:]

    if contents.endswith('\r'):
        contents = contents[:-1]

    return contents

parser = ASBBBCode()
render = parser.format

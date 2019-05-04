"""Markup stuff not specific to any format."""

import enum


class MarkupLanguage(enum.Enum):
    """An enum for all recognized markup formats."""

    bbcode = 'BBCode'
    markdown = 'Markdown'
    plain_text = 'Plain text'

    def __str__(self):
        """Stringify as e.g. 'plain_text' rather than
        'MarkupLanguage.plain_text'.

        This gets WTForms to round-trip properly.
        """

        return self.name

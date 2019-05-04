<%namespace name="helpers" file="/helpers/helpers.mako" />

<%!
    import asb.markup
    import asb.markup.markdown
    import asb.markup.bbcode
%>


<%def name="markup(text, format)">
    % if format is asb.markup.MarkupLanguage.plain_text:
        <div class="markup plain-text">${text}</div>
    % elif format is asb.markup.MarkupLanguage.markdown:
        <div class="markup markdown">${asb.markup.markdown.render(text)}</div>
    % elif format is asb.markup.MarkupLanguage.bbcode:
        <div class="markup bbcode">${asb.markup.bbcode.render(text)}</div>
    % endif
</%def>

<%def name="markup_editor(text_field, format_field)">
    ${helpers.form_error_list(format_field.errors)}
    <ul class="markup-format">
        % for option in format_field:
            <li><label>${option} ${option.label.text}</label></li>
        % endfor
    </ul>

    ${helpers.form_error_list(text_field.errors)}
    ${text_field(rows=10, maxlength=65535)}
</%def>

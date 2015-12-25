<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name="title">Trade - The Cave of Dragonflies ASB</%block>\

% if pending_trades:
    <h1>Gifts in progress</h1>

    <ul>
        % for lot in pending_trades:
            <li>
                <a href="${request.resource_path(lot.trade.__parent__,
                                                 lot.trade.__name__)}">
                    To ${lot.recipient.name}
                </a>
            </li>
        % endfor
    </ul>
% endif

<h1>Give a gift</h1>

<form action="/trade" method="POST">
${form.csrf_token}
${h.form_error_list(form.csrf_token.errors)}

<p><b>${form.recipient_name.label}</b></p>
${form.recipient_name}
${h.form_error_list(form.recipient_name.errors)}

<p><b>${form.contents.label}</b></p>
${form.contents(class_='option-list')}
${h.form_error_list(form.contents.errors)}

${form.submit}
</form>

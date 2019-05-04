<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name="title">Trade with ${trade_info['recipient_name']} - The Cave of Dragonflies ASB</%block>\
<%! from asb.markup.markdown import render as md %>

<p><a href="/trade?back=yes">← Back</a></p>

<h1>Trade with ${trade_info['recipient_name']}</h1>

<p>Anything you include will be taken from your account immediately, and
returned if the trade is turned down or cancelled.</p>

<form action="${request.path}" method="POST">
${form.csrf_token}
${h.form_error_list(form.csrf_token.errors)}

% if 'money' in trade_info['contents']:
<h1>Include money</h1>
<p><b>${form.money.label}:</b> $${form.money(size=2, maxlength=3)}</p>
${h.form_error_list(form.money.errors)}
<p>You have $${request.user.money}.</p>
% endif

% if 'items' in trade_info['contents']:
<h1>Include items</h1>
<table class="standard-table effect-table">
<col class="item-icon">
<col class="item">
<col class="stat">
<col class="stat stat-bag">
<col class="summary">

<thead>
    <tr>
        <th colspan="2">Item</th>
        <th><abbr title="Quantity to include">Qty</abbr></th>
        <th>Bag</th>
        <th>Summary</th>
    </tr>
</thead>

<tbody>
    % for (field, (item, quantity)) in zip(form.items, form.items.items):
    <tr>
        <td class="icon item-icon">
            <img src="/static/images/items/${item.identifier}.png" alt="">
        </td>
        <td class="focus-column">${h.link(item)}</td>
        <td class="input">${field(size=1, maxlength=2)}</td>
        <td class="stat">${quantity}</td>
        <td class="summary">${item.summary | md}</td>
    </tr>
    % endfor
</tbody>
</table>
% endif

% if 'pokemon' in trade_info['contents']:
<% tickies = iter(form.pokemon) %>
<%def name="ticky_cell(pokemon)">\
<td class="input ticky">${next(tickies)}</td>
</%def>
<%def name="ticky_col()"><col class="ticky"></%def>
<%def name="ticky_header()"><th></th></%def>

<h1>Include Pokémon</h1>
<p>Any items held by the Pokémon you select will be included as well.</p>

${t.pokemon_table(
    request.user.squad,
    request.user.pc,
    subheaders=['Active squad', 'PC'],
    skip_cols=['trainer'],
    extra_left_cols=[{
        'col': ticky_col,
        'th': ticky_header,
        'td': ticky_cell
    }]
)}
% endif

${form.next}
</form>

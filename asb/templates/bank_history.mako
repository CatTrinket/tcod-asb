<%inherit file='/base.mako'/>\
<%namespace name='t' file='/helpers/tables.mako'/>\
<%block name='title'>Bank - The Cave of Dragonflies ASB</%block>\

<p><a href="/bank">← Back to bank</a></p>

<h1>Transaction history</h1>
${t.transaction_table(transactions)}

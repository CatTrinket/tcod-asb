<%inherit file='/base.mako'/>\
<%block name='title'>The Cave of Dragonflies ASB</%block>\

<h1>${status}</h1>

% if message:
<p>Well, something went wrong.  Here's the message associated with the error,
possibly a generic default:</p>

<p>${message}</p>
% else:
<p>Well, something went wrong.</p>
% endif

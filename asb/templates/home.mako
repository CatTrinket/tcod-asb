<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>The Cave of Dragonflies ASB</%block>\

<%def name="bulletin_list(bulletin)">
% if bulletin:
<ul>
    % for message, link in bulletin:
    <li><a href="${link}">${message}</a>
    % endfor
</ul>
% else:
<p>${empty_bulletin_message()}</p>
% endif
</%def>

<p>ASB is back!  See
<a href="http://forums.dragonflycave.com/showthread.php?t=17397">the
announcement on the forums</a> for details.</p>

% if bulletin is not UNDEFINED:
<h1>Trainer bulletin</h1>

${bulletin_list(bulletin)}
% endif

% if mod_stuff is not UNDEFINED:
<h1>Mod bulletin</h1>

${bulletin_list(mod_stuff)}
% endif

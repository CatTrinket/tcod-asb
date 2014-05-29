<%inherit file='/base.mako'/>\
<%block name='title'>The Cave of Dragonflies ASB</%block>\

<p>HELLO.  Eventually there'll be some kind of actual landing page here.</p>

% if mod_stuff is not None:
<h1>Mod Bulletin</h1>

% if mod_stuff:
<ul>
    % for message, link in mod_stuff:
    <li><a href="${link}">${message}</a>
    % endfor
</ul>
% else:
<p>The mod bulletin is bare for the time being.  Someone has arranged all the
thumbtacks into a smiling cat face.</p>
% endif
% endif

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

% if bulletin is not UNDEFINED:
<h1>Trainer bulletin</h1>

${bulletin_list(bulletin)}
% endif

% if mod_stuff is not UNDEFINED:
<h1>Mod bulletin</h1>

${bulletin_list(mod_stuff)}
% endif

<h1 id="news">News</h1>
<p><a href="/news">All news →</a></p>
% if request.has_permission('news.post'):
<p><a href="/news/post">Post news →</a></p>
% endif
% for post in news:
${h.news_post(post)}
% endfor

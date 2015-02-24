<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>News archive - The Cave of Dragonflies ASB</%block>\

% if request.has_permission('news.post'):
<p><a href="/news/post">Post news →</a></p>
% endif

<h1>News archive</h1>
% for post in news:
${h.news_post(post)}
% endfor

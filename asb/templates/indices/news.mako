<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>News archive - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md, chomp %>

% if request.has_permission('news.post'):
<p><a href="/news/post">Post news →</a></p>
% endif

<h1>News archive</h1>
% for post in news:
<h2>${post.title | md.convert, chomp}</h2>
<p class="news-timestamp">
    Posted <b>${post.post_time.strftime('%Y %B %d, %H:%M.%S UTC')}</b>
    by <b>${h.link(post.poster)}</b>
</p>

${post.text | md.convert}
% endfor

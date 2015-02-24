<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%block name='title'>${post.title} - News - The Cave of Dragonflies ASB</%block>\

<p><a href="/news">← Back to news</a></p>

${h.news_post(post, h1=True)}

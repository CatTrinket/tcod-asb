<%def name="link(db_resource, text=None, **kwargs)">\
## resource_url will add a trailing slash unless we do it this way
<a href="${request.resource_url(db_resource.__parent__,
    db_resource.__name__, **kwargs)}">${text or db_resource.name}</a>\
</%def>

<%def name="num(n, invisible_plus=True)">\
% if n < 0:
−${n * -1}\
% elif n == 0 or invisible_plus:
${n}\
% else:
+${n}\
% endif
</%def>

<%def name="type_icon(type)">\
<span class="type type-${type.identifier}">\
<a href="${request.resource_url(type.__parent__, type.__name__)}">\
${type.name}</a></span>\
</%def>

<%def name="damage_class_icon(damage_class)">\
<span class="damage-class damage-class-${damage_class.identifier}">\
% if damage_class.identifier == 'non-damaging':
—\
% else:
${damage_class.name.capitalize()}\
% endif
</span>\
</%def>

<%def name="pokemon_icon(pokemon)">\
${pokemon_form_icon(pokemon.form, gender=pokemon.gender.identifier,
                    shiny=pokemon.is_shiny)}\
</%def>

<%def name="pokemon_form_icon(form, gender=None, shiny=False, alt='')">\
## alt is currently unused because I can't figure out how to make it work with
## this trick
<span class="pokemon-icon ${form.identifier}\
% if gender is not None:
 ${gender}\
% endif
% if shiny:
 shiny\
% endif
"></span>\
</%def>

<%def name="pokemon_sprite(pokemon)">\
${pokemon_form_sprite(pokemon.form, gender=pokemon.gender.identifier,
                      shiny=pokemon.is_shiny)}\
</%def>

<%def name="pokemon_form_sprite(form, gender=None, shiny=False, alt='')">\
<%
   if shiny:
       path = '/static/images/pokemon/shiny'
   else:
       path = '/static/images/pokemon'

   filename = '{}/{}.png'.format(path, form.identifier)

   if gender is not None:
       from pkg_resources import resource_exists

       alt_filename = '{}/{}-{}.png'.format(path, form.identifier, gender)

       if resource_exists('asb', alt_filename):
           filename = alt_filename
%>\
<div class="portrait">
    <img src="${filename}" alt="${alt}">
</div>
</%def>

<%def name="gender_symbol(gender)">\
<span class="gender-symbol-${gender.identifier}">\
% if gender.identifier == 'female':
♀\
% elif gender.identifier == 'male':
♂\
% elif gender.identifier == 'genderless':
—\
% endif
</span>\
</%def>

<%def name="form_error_list(*error_lists)">
<% errors = [error for list in error_lists for error in list] %>
% if errors:
<ul class="form-error">
    % for error in errors:
    <li>${error}</li>
    % endfor
</ul>
% endif
</%def>

<%def name="appeal(move)">\
% if move.appeal == -1:
+??\
% elif move.appeal is not None:
+${move.appeal}\
% endif
% if move.bonus_appeal == -1:
 (+??)\
% elif move.bonus_appeal is not None:
 (+${move.bonus_appeal})\
% endif
</%def>

<%def name="jam(move)">\
% if move.jam == -1:
−??\
% elif move.jam is not None:
−${move.jam}\
% endif
% if move.bonus_jam == -1:
 (−??)\
% elif move.bonus_jam is not None:
 (−${move.bonus_jam})\
% endif
</%def>

<%def name="news_post(post=None, h1=False, preview=False, **post_info)">
<%
    from asb.markdown import md

    if post is not None:
        post_info.setdefault('title', post.title)
        post_info.setdefault('post_time', post.post_time)
        post_info.setdefault('poster', post.poster)
        post_info.setdefault('text', post.text)
%>
% if h1:
<h1>${post_info['title']}</h1>
% elif post is None or preview:
<h2>${post_info['title']}</h2>
% else:
<h2>${link(post, text=post_info['title'])}</h2>
% endif

<p class="news-timestamp">
    Posted <b>${post_info['post_time'].strftime('%Y %B %d, %H:%M.%S UTC')}</b>
    by <b>${link(post_info['poster'])}</b>
    % if not preview and request.has_permission('news.edit', post):
    (<a href="${request.resource_url(post, 'edit')}">Edit</a>)
    % endif
</p>

${post_info['text'] | md.convert, n}
</%def>

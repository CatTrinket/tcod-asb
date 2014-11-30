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
<span class="type type-${type.identifier}">${type.name}</span>\
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

<%def name="pokemon_form_icon(form, gender=None, alt='')">\
<%
    if gender is not None and form.identifier in ['unfezant', 'frillish',
      'jellicent', 'pyroar']:
        # Meowstic's genders are forms, so that's already in the identifier
        filename = '{}-{}.png'.format(form.identifier, gender)
    else:
        filename = '{}.png'.format(form.identifier)

    if alt is None:
        alt = form.name
%>\
<img src="/static/images/pokemon-icons/${filename}" alt="${alt}">\
</%def>

<%def name="pokemon_form_sprite(form, gender=None, alt='')">\
<%
   filename = '/static/images/pokemon/{}.png'.format(form.identifier)
   if gender is not None:
       from pkg_resources import resource_exists

       alt_filename = '/static/images/pokemon/{}-{}.png'.format(
           form.identifier, gender)

       if resource_exists('asb', alt_filename):
           filename = alt_filename
%>\
<img class="portrait" src="${filename}" alt="${alt}">
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

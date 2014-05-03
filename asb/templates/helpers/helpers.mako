<%def name="link(db_resource, text=None, **kwargs)">\
## resource_url will add a trailing slash unless we do it this way
<a href="${request.resource_url(db_resource.__parent__,
    db_resource.__name__, **kwargs)}">${text or db_resource.name}</a>\
</%def>

<%def name="num(n, invisible_plus=True)">\
% if n < 0:
−${n * -1 | n, str}\
% elif n == 0 or invisible_plus:
${n | n, str}\
% else:
+${n | n, str}\
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

<%def name="pokemon_form_icon(form, gender=None)">\
<%
    if gender is not None and form.identifier in ['unfezant', 'frillish',
      'jellicent', 'pyroar']:
        # Meowstic's genders are forms, so that's already in the identifier
        filename = '{}-{}.png'.format(form.identifier, gender)
    else:
        filename = '{}.png'.format(form.identifier)
%>\
<img src="/static/images/pokemon-icons/${filename}" alt="">\
</%def>

<%def name="pokemon_form_sprite(form, gender=None)">\
<%
   filename = '/static/images/pokemon/{}.png'.format(form.identifier)
   if gender is not None:
       from pkg_resources import resource_exists

       alt_filename = '/static/images/pokemon/{}-{}.png'.format(
           form.identifier, gender)

       if resource_exists('asb', alt_filename):
           filename = alt_filename
%>\
<img src="${filename}" alt="">\
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

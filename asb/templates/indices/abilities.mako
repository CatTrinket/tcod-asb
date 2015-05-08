<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Abilities - The Cave of Dragonflies ASB</%block>\

<% from asb.markdown import md, chomp %>

% for ability in abilities:
<p><strong>${h.link(ability)}:</strong> \
${ability.description | md.convert, chomp}</p>
% endfor

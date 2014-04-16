<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers.mako"/>\
<%block name='title'>Abilities - The Cave of Dragonflies ASB</%block>\

% for ability in abilities:
<p><strong>${h.link(ability)}:</strong> ${ability.description}</p>
% endfor

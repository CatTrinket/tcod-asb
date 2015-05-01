<%inherit file='/base.mako'/>\
<%namespace name='h' file='/helpers/helpers.mako'/>\
<%namespace name='sig' file='/sig_stuff/helpers.mako'/>\
<%block name='title'>Signature moves awaiting approval - The Cave of Dragonflies ASB</%block>\

<h1>Signature moves awaiting approval</h1>

% for move in moves:
${sig.display_move_mod(move, show_pokemon=True)}
% endfor

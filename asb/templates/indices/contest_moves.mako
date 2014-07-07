<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%block name='title'>Moves - The Cave of Dragonflies ASB</%block>\

<%def name="move_list(moves)">\
<%
    moves = list(moves)
    last_move = len(moves) - 1
%>\
% if len(moves) == 1:
${h.link(moves[0])}\
% elif len(moves) == 2:
${h.link(moves[0])} and ${h.link(moves[1])}\
% else:
% for n, move in enumerate(moves):
% if n == 0:
${h.link(move)}\
% elif n == last_move:
, and ${h.link(move)}\
% else:
, ${h.link(move)}\
% endif
% endfor
% endif
</%def>

<h1>Contest type listings</h1>

<p>Contest types can be divided across these supercategories:</p>

<ul>
    <li>Appeal moves, which focus on simply boosting the user's score;</li>
    <li>Support moves, which provide the user miscellaneous bonuses;</li>
    <li>Jam moves, which may detract from an opponent's score or disrupt their advantages;</li>
    <li>Nervousness moves, which interact with the nervousness mechanic;</li>
    <li>Timing moves, which affect the order in which the Pokémon take action;</li>
    <li>Other moves.</li>
</ul>

% for supercategory in supercategories:
<h1>${supercategory.name} moves</h1>

% for category in supercategory.categories:
    <p><b>${category.name}:</b> ${category.description}
    
    % if category.identifier == 'pure-points':
        </p>

        <p>Pure Points moves, broken down by score, include: \
    
        % for ((appeal, jam), moves) in pure_points_moves:
        <p>+${appeal}${'/−{}'.format(jam) if jam  else ''}: ${move_list(moves)}.</p>
        % endfor
    % else:
        ${category.name} moves include: ${move_list(category.moves)}.</p>
    % endif
% endfor
% endfor

<%inherit file='/base.mako'/>\
<%namespace name="h" file="/helpers/helpers.mako"/>\
<%namespace name="t" file="/helpers/tables.mako"/>\
<%block name='title'>${battle.name} - Battles - The Cave of Dragonflies ASB</%block>\

<h1>Approve ${battle.name}</h1>

<dl>
    <dt>Thread link</dt>
    <dd><a href="${battle.link}">Here</a></dt>

    <dt>Who won?</dt>
    <dd>${outcome}</dd>

    <dt>How did it end?</dt>
    <dd>${length}.</dd>
</dl>

<h1>Pokémon</h1>

<table>
<thead>
    <tr>
        <th colspan="2">Pokémon</th>
        <th>KOs</th>
        <th>XP</th>
        <th>:3</th>
        <th></th>
    </tr>
</thead>

% for team in battle.teams:
% for trainer in team.trainers:
<tbody>
    <tr class="subheader-row">
        <td colspan="7">${trainer.name}</td>
    </tr>

    % for pokemon in trainer.pokemon:
    % if pokemon.participated:
    <tr>
        <td class="icon pokemon-icon">
            ${h.pokemon_icon(pokemon)}
        </td>

        <td class="focus-column">
            % if pokemon.pokemon:
            ${h.link(pokemon.pokemon, text=pokemon.name)}
            % else:
            ${pokemon.name}
            % endif
        </td>

        <td class="stat">${pokemon.kos}</td>
        <td class="stat">+${pokemon.experience_gained}</td>
        <td class="stat">+${pokemon.happiness_gained}</td>

        % if pokemon.item is not None and pokemon.item.identifier in ['lucky-egg', 'soothe-bell']:
        <td class="icon"><img src="/static/images/items/${pokemon.item.identifier}.png"></td>
        % else:
        <td></td>
        % endif
    </tr>
    % endif
    % endfor
</tbody>
% endfor
% endfor
</table>

<h1>Approve</h1>
<form action="${request.path}" method="POST">
<p>If something's wrong here, tell Zhorken (there isn't an interface for
actually fixing mistakes here yet).  Otherwise:</p>

${h.form_error_list(*form.errors.values())}
${form.csrf_token}
${form.approve}
</form>

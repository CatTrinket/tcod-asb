-- Insert moves that Pokémon should get from alternate forms/pre-evolutions.

-- 2014-11-29

begin;

-- Propagate moves up evolution lines
with recursive prevos (evo_id, prevo_id) as (
    select id, evolves_from_species_id from pokemon_species ps

    union all

    select prevos.evo_id, ps.evolves_from_species_id from prevos
    join pokemon_species ps on prevos.prevo_id=ps.id
),

prevo_forms (evo_id, prevo_id) as (
    select pf.id, pf_pre.id
    from pokemon_forms pf
    join prevos p on pf.species_id = p.evo_id
    join pokemon_forms pf_pre on p.prevo_id = pf_pre.species_id
    where pf.form_order = pf_pre.form_order or (
        pf_pre.form_order = 1 and pf.form_order not in (
            select form_order from pokemon_forms pf_pre_2
            where p.prevo_id = pf_pre_2.species_id
        )
    )
)

insert into pokemon_form_moves
select pfm.pokemon_form_id, pfm_pre.move_id
from pokemon_form_moves pfm
join pokemon_forms pf on pfm.pokemon_form_id=pf.id
join prevo_forms pre_f on pf.id = pre_f.evo_id
join pokemon_forms pf_pre on pre_f.prevo_id = pf_pre.id
join pokemon_form_moves pfm_pre on pf_pre.id=pfm_pre.pokemon_form_id
except select * from pokemon_form_moves;

-- Propagate moves between forms
insert into pokemon_form_moves
select pfa.pokemon_form_id, pfa2.move_id
from pokemon_form_moves pfa
join pokemon_forms pf on pfa.pokemon_form_id=pf.id
join pokemon_forms pf2 on pf.species_id=pf2.species_id
join pokemon_form_moves pfa2 on pf2.id=pfa2.pokemon_form_id
where pf.species_id not in (
    select id from pokemon_species
    where identifier in ('rotom', 'kyurem') or not can_switch_forms
)
except select * from pokemon_form_moves;

commit;

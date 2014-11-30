-- Insert duplicate abilities as needed so that each entire family has
-- abilities in all the same slots.

-- 2014-11-27

with existing as (
    select pokemon_form_id, slot
    from pokemon_form_abilities
),

family_existing as (
    select distinct ps.pokemon_family_id, pfa.slot
    from pokemon_form_abilities pfa
    join pokemon_forms pf on pfa.pokemon_form_id=pf.id
    join pokemon_species ps on pf.species_id=ps.id
),

missing_slots as (
    select pf.id, fe.slot
    from pokemon_forms pf
    join pokemon_species ps on pf.species_id=ps.id
    join family_existing fe on ps.pokemon_family_id=fe.pokemon_family_id
    
    except
    
    select pf.id, e.slot
    from pokemon_forms pf
    join existing e on pf.id=e.pokemon_form_id
)

insert into pokemon_form_abilities
select ms.id, ms.slot, a1.ability_id, ms.slot=3
from missing_slots ms
join pokemon_form_abilities a1 on ms.id=a1.pokemon_form_id and a1.slot=1;

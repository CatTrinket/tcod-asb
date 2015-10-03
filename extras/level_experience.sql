-- HELLO HAVE A PAIR OF GIANT SQL QUERIES THAT WILL PRESUMABLY ONLY WORK IN
-- POSTGRES.  As usual.

-- Set experience requirements.  This requires you to have temporarily created
-- a level column on pokemon_species first.

create function exp(level integer, stage integer, length integer,
                    buyable boolean, unova boolean)
returns integer
as $$
    select case when not unova then
        case when (stage, length) = (2, 2) then
            case when buyable then 2
            when level is null then 3
            when level between 15 and 35 then 3
            when level between 36 and 40 then 4
            when level = 48 then 5
            end
        when (stage, length) = (2, 3) then
            case when buyable and level between 7 and 9 then 1
            when buyable and level = 20 then 2
            when level between 14 and 18 then 2
            when level between 19 and 28 then 3
            when level between 30 and 42 then 4
            end
        when (stage, length) = (3, 3) then
            case when buyable then 2
            when level between 18 and 40 then 6
            when level between 42 and 45 then 7
            when level between 46 and 55 then 8
            when level is null then 6
            end
        end
    when unova then
        case when (stage, length) = (2, 2) then
            case when level between 20 and 43 then 3
            when level between 50 and 54 then 4
            when level = 59 then 5
            end
        when (stage, length) = (2, 3) then
            case when buyable then 2
            when level between 16 and 22 then 2
            when level between 25 and 35 then 3
            when level between 38 and 50 then 4
            end
        when (stage, length) = (3, 3) then
            case when level between 30 and 41 then 6
            when level between 47 and 49 then 7
            when level = 64 then 8
            end
        end
    end;
$$
language sql;

begin;

with recursive stages (id, family, stage) as (
    select id, pokemon_family_id, 1
    from pokemon_species
    where evolves_from_species_id is null

    union all

    select ps.id, ps.pokemon_family_id, s.stage + 1
    from pokemon_species as ps
    join stages as s on ps.evolves_from_species_id = s.id
),

family_lengths (family_id, length) as (
    select family, max(stage)
    from stages
    group by family
),

changes (id, exp) as (
    select ps.id, exp(ps.level, s.stage, fl.length,
                      pse.buyable_price is not null, ps.id between 494 and 649)
    from pokemon_species ps
    join stages s on ps.id = s.id
    join family_lengths fl on ps.pokemon_family_id = fl.family_id
    join pokemon_species_evolution pse on ps.id = pse.evolved_species_id
    where pse.item_id is null and pse.happiness is null
)

update pokemon_species_evolution
set experience = (select exp from changes where id=evolved_species_id)
where evolved_species_id in (select id from changes)
returning evolved_species_id, experience;

-- I ran a query to find cases like Slowbro and Glalie; the only other thing
-- is Gardevoir which is only 3 exp past Kirlia anyway.  I didn't run a query
-- for level babies but there are barely any of those and the rest are already
-- 3 exp.
update pokemon_species_evolution set experience = 3
where evolved_species_id in (
    select id from pokemon_species
    where identifier in ('slowbro', 'glalie', 'electabuzz', 'magmar')
);

commit;

drop function exp(integer, integer, integer, boolean, boolean);

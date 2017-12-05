-- Prevent clashes mid-update
update pokemon_forms set "order" = id + 10000;

-- HERE WE GO
with orders (id, "order") as (
    select pf.id, rank() over (order by ps.order, pf.form_order)
    from pokemon_forms pf
    join pokemon_species ps on pf.species_id = ps.id
)

update pokemon_forms set "order" = (
    select "order" from orders where pokemon_forms.id = orders.id
);

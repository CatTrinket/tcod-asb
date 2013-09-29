<!DOCTYPE html>
<html>
<head>
    <title><%block name='title'>The ASB thing</%block></title>
</head>
<body>
<ul>
  <li>
    <a href="/pokemon">Pokémon</a>
    <ul>
      <li><a href="/pokemon/species">Species list</a></li>
    </ul>
  </li>

  <li>
    <a href="/trainers">Trainers</a>
  </li>
</ul>
${next.body()}\
</body>
</html>

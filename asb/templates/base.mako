<!DOCTYPE html>
<html>
<head>
    <title><%block name='title'>The Cave of Dragonflies ASB</%block></title>
    <link rel="stylesheet" href="/static/asb.css">
</head>
<body>
<section id="header">
<div id="menu">
<ul>
  <li>
    Your Account
    <ul>
      <li>Do things</li>
      <li>idk</li>
    </ul>
  </li>

  <li>
    ASB Marketplace
    <ul>
      <li>Buy stuff</li>
    </ul>
  </li>

  <li>
    Dex
    <ul>
      <li>
        <a href="/pokemon">Pokémon</a>
        <ul>
          <li><a href="/pokemon/species">Species list</a></li>
        </ul>
      </li>
    
      <li><a href="/trainers">Trainers</a></li>
      <li>Items</li>
      <li>Moves?  Abilities?</li>
    </ul>
  </li>
</ul>
</div>
</section>

<section id="body">
${next.body()}\
</section>
</body>
</html>

Players will need to have attributes attached to their character (the Mobile field of the Player struct in game.thrift). 

# Attributes

- strength - relates to how much a character can carry, how strong they are
- luck - is used when luck might come into play, like random drop chances
- constitution - how long and strong can the character sprint, or carry items, or apply strength to a problem
- dexterity - weapon handling, engineering operations with fine equipment, complex tasks
- arcana - relating to discovery, item information being shown, revealing contextual secrets, better blueprint studying
- operations - affects general operations like repair, scanning, equipment use, ship weapons, mining, refining

We will need to add these to AttributeType enum. Each of these values can only be a double. Add a comment to each entry to explain what it's for.

We will need to update the python code that references attributes, that loads and saves them for a Player/Mobile. These attributes can also appear on Items, in which case they would normally affect the owner's attributes in an
additive sense.

We will also need to update the testing code that applies to mobiles and players if applicable.

We will need to update the seed_players.py script so that when we create a player, and a mobile,
that we also generate these attributes for the mobile with random values, and assert that we can
also read them back.
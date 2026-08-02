# MTG Game Simulator

Includes custom deck inputs, custom gameplay logic, and custom success criteria.

## Caveats and Assumptions

- This is intended to simulate "goldfishing" and therefore does not take into account the possibility of interactions from other players such as counter spells or STAX.


## How to import your own decklist

Save your decklist under `/decks/<your_deck>.json`.

Format:

```json
[

    {
        "name": "Grim Monolith"
    },
    ...
    {
        "name": "Zirda, the Dawnwaker",
        "is_commander": true
    }
]

```

## The Game base class

The `Game` base class is intended for reusable logic that is not specific to a specific deck. It already contains general logic for phases and common game actions.


## How to write your own custom module

Create a custom class in `/custom`. The class should inherit the base `game.Game` class which defines general gameplay. 

Your custom class should override function such as `first_main_phase` to include logic regarding what you would do given the cards in your hand.

See `custom/_template.py` as an example.

Keep gameplay logic simple and don't be afraid to make assumtions that would be true most of the time. For example, assumming you will always shock in shock lands.



## Unit Tests

Add unit tests for key logic. For example, if there is logic to play a card in `first_main_phase` if in hand, write a test that starts with the given card in hand and asserts that it is no longer in hand after resolving `first_main_phase`. See examples in test_game.py


## How to use

Assuming Python is installed and requirements.txt...

From root, run 

`python run.py -f EDH -d ./decks/<your_deck>.json -i <n_iterations> -t <n_turns> -g <custom_gameplay_module> -m <max_mulligans>`

For example, `python run.py -d ./decks/zirda.json -i 10000 -t 2 -g custom.zirda.ZirdaGame -m 2` 

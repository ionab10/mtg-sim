# MTG Game Simulator

Includes custom deck inputs, custom gameplay logic, and custom success criteria.

## Caveats and Assumptions

- This is intended to simulate "goldfishing" and therefore does not take into account the possibility of interactions from other players such as counter spells or STAX.


## How to use

From root, run `python run.py -d ./decks/<your_deck>.json -i <n_iterations> -t <n_turns> -g <custom_gameplay_module>`


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


## How to write your own custom module

Create a custom class in `/custom`. The class should inherit the base `game.Game` class which defines general gameplay. 

Your custom class should override function such as `first_main_phase` to include logic regarding what you would do given the cards in your hand.

import argparse
from html import parser
import importlib
import json
import logging

from game import Card, Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_logger = logging.getLogger("game_state_logger")
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('./mtgsim.log', mode='a')
file_logger.addHandler(file_handler)


def load_deck_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def resolve_game_class(gameplay_logic: str):
    if not gameplay_logic:
        return Game

    # Backward-compat short aliases (optional)
    aliases = {
        "ZirdaGame": "custom.zirda.ZirdaGame",
    }

    target = aliases.get(gameplay_logic, gameplay_logic)

    # If user passed only a class name, assume custom.<lowercase_without_game>
    if "." not in target:
        module_name = f"custom.{target.replace('Game', '').lower()}"
        target = f"{module_name}.{target}"

    module_path, class_name = target.rsplit(".", 1)
    module = importlib.import_module(module_path)
    game_cls = getattr(module, class_name)
    return game_cls


def simulate(deck_data, iterations=1, turns=0, gameplay_logic=None):

    library = [
        Card(c["name"], c.get("card_types", []))
        for c in deck_data if not c.get("is_commander", False)
    ]
    commanders = [Card(c["name"], c.get("card_types", [])) for c in deck_data if c.get("is_commander", False)]

    game_cls = resolve_game_class(gameplay_logic)

    successes = 0
    
    for _ in range(iterations):
        game = game_cls(library.copy(), commanders.copy())

        # Shuffle the library
        game.shuffle()

        # Draw 7 cards
        for _ in range(7):  
            game.draw()
        logger.debug("Hand after drawing 7 cards: \n%s", "\n".join(str(card) for card in game.hand))

        # Handle pregame actions (like Gemstone Caverns)
        game.pregame()

        # Take turns
        for _ in range(turns):
            game.start_turn()
            logger.debug("Begin turn %d", game.turn_number)
            
            game.untap()
            game.draw()
            game.first_main_phase()

            is_success = game.check_success()
            if is_success:
                successes += 1
                logger.debug("Success on turn %d", game.turn_number)
                file_logger.debug("Hand: %s", ", ".join(card.name for card in game.hand))
                file_logger.debug("Battlefield: %s", ", ".join(card.name for card in game.battlefield))
                break

            game.end_step()

    logger.info("Simulation complete. Successes: %d out of %d iterations (%.2f%%)", successes, iterations, (successes / iterations * 100) if iterations > 0 else 0)

def main():
    parser = argparse.ArgumentParser(
        description="Simulates a MTG game"
    )


    parser.add_argument("-d", "--deck", type=str, help="Path to the deck input file")
    parser.add_argument("-i", "--iter", type=int, default=1, help="Number of games to simulate.")
    parser.add_argument("-t", "--turns", type=int, default=1, help="Number of turns to simulate. Exits early if success criteria is met.")
    parser.add_argument(
        "-g", "--gameplay",
        type=str,
        help="Game class or import path, e.g. ZirdaGame or custom.zirda.ZirdaGame. If not provided, defaults to the base Game class."
    )

    args = parser.parse_args()

    logger.info("Processing file: %s, Iterations set to: %d, simulating %d turns", args.deck, args.iter, args.turns)
    logger.info("Custom gameplay logic: %s", args.gameplay)

    deck_data = load_deck_from_json(args.deck)

    simulate(deck_data, args.iter, args.turns, args.gameplay)

if __name__ == "__main__":
    main()
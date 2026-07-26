import argparse
import json
import logging

from game import Card, Game


logging.basicConfig(
    level=logging.INFO,
    # filename='./mtgsim.log', filemode='a',
)
logger = logging.getLogger(__name__)


def load_deck_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def simulate(deck_data, iterations=1, turns=0, gameplay_logic=None):

    library = [Card(c["name"], c.get("is_land", False)) for c in deck_data if not c.get("is_commander", False)]
    commanders = [Card(c["name"]) for c in deck_data if c.get("is_commander", False)]

    successes = 0

    for _ in range(iterations):
        if gameplay_logic == "zirda":
            from custom.zirda import ZirdaGame
            game = ZirdaGame(library.copy(), commanders.copy())
        else:
            game = Game(library.copy(), commanders.copy())

        game.shuffle()

        for _ in range(7):  # Draw 7 cards
            game.draw()


        logger.debug("Hand after drawing 7 cards: \n%s", "\n".join(str(card) for card in game.hand))

        # Gemstone Caverns Pregame
        for card in game.hand:
            if card.name == "Gemstone Caverns" and game.seat_number != 1:
                game.hand.remove(card)
                game.battlefield.append(card)
                card.counters["luck"] += 1  # Add a luck counter to Gemstone Caverns

        for _ in range(turns):
            game.untap()
            game.draw()
            game.first_main_phase()

        available_mana = game.count_available_mana()
        logger.debug("Available mana: %s", available_mana)
        if available_mana["coloured"] >= 2 and available_mana["C"] >= 2:
            successes += 1

    logger.info("Simulation complete. Successes: %d out of %d iterations (%.2f%%)", successes, iterations, (successes / iterations * 100) if iterations > 0 else 0)

def main():
    parser = argparse.ArgumentParser(
        description="Simulates a MTG game"
    )


    parser.add_argument("-d", "--deck", type=str, help="Path to the deck input file")
    parser.add_argument("-i", "--iter", type=int, default=1, help="Number of iterations")
    parser.add_argument("-t", "--turns", type=int, default=1, help="Number of turns to simulate")
    parser.add_argument("-g", "--gameplay", type=str, help="Custom gameplay logic (optional)")

    args = parser.parse_args()

    logger.info("Processing file: %s, Iterations set to: %d, simulating %d turns", args.deck, args.iter, args.turns)
    logger.info("Custom gameplay logic: %s", args.gameplay)

    deck_data = load_deck_from_json(args.deck)

    simulate(deck_data, args.iter, args.turns, args.gameplay)

if __name__ == "__main__":
    main()
from random import randint, shuffle

class Card:

    def __init__(self, name, is_land=False):
        self.name = name
        self.is_tapped = False
        self.is_land = is_land
        self.counters = {
            "charge": 0,
            "lore": 0,
            "loyalty": 0,
            "luck": 0,
        }

    def tap(self):
        self.is_tapped = True

    def untap(self):
        self.is_tapped = False

    def __repr__(self):
        return f"[{self.name}] {'tapped' if self.is_tapped else 'untapped'}"


class Game:
    def __init__(self, library, format, commanders=[]):
        self.library = library
        self.hand = []
        self.graveyard = []
        self.command_zone = commanders
        self.mana_pool = {
            "W": 0,
            "U": 0,
            "B": 0,
            "R": 0,
            "G": 0,
            "C": 0
        }
        self.battlefield = []
        if format == "EDH":
            self.life_total = 40
            self.seat_number = randint(1, 4)  # Random seat number for EDH format
        else:
            self.life_total = 20
            self.seat_number = randint(1, 2)  # Random seat number for other formats

    def shuffle(self):
        """Shuffle the library of cards."""
        shuffle(self.library)

    def draw(self):
        """Draw a card from the library."""
        if self.library:
            card = self.library.pop()
            self.hand.append(card)
            return card
        else:
            raise ValueError("No more cards in the library to draw.")

    def sacrifice(self, card):
        """Sacrifice a card from the battlefield."""
        if card in self.battlefield:
            self.battlefield.remove(card)
            self.graveyard.append(card)
        else:
            raise ValueError(f"{card.name} is not on the battlefield.")

    def tutor(self, target_cards, to_battlefield=False):
        """Tutor a card from the library to the hand or battlefield."""

        for target_card in target_cards:
            for card in self.library:
                if card.name == target_card:
                    self.library.remove(card)
                    if to_battlefield:
                        self.battlefield.append(card)
                    else:
                        self.hand.append(card)
                    return card
        return None  # If no target card was found

    def first_main_phase(self):
        """Simulate the first main phase of the game."""
        # Play a land if available
        self.play_land()
        
        self.play_mox()
    
    def count_available_mana(self):
        """Count the available mana in the mana pool."""
        available_mana = self.mana_pool.copy()
        available_mana["WUBRG"] = 0

        for card in self.battlefield:
            if not card.is_tapped and card.is_land:
                # Assuming each land can produce one mana of its color
                # This is a simplification; actual MTG rules are more complex
                if card.name == "Plains":
                    available_mana["W"] += 1
                elif card.name == "Island":
                    available_mana["U"] += 1
                elif card.name == "Swamp":
                    available_mana["B"] += 1
                elif card.name == "Mountain":
                    available_mana["R"] += 1
                elif card.name == "Forest":
                    available_mana["G"] += 1
                else:
                    available_mana["C"] += 1

            elif not card.is_tapped and card.name in ["Lotus Petal", "Mox Diamond"]:
                available_mana["WUBRG"] += 1

        for card in self.hand:
            if card.name == "Simian Spirit Guide":
                available_mana["R"] += 1

        return available_mana

    def untap(self):
        """Untap all cards on the battlefield."""
        for card in self.battlefield:
            if card.name == "Mana Vault" and card.is_tapped:
                self.life_total -= 1

            # Skip cards that should not be untapped
            if card.name in [
                "Basalt Monolith",
                "Grim Monolith",
                "Mana Vault",
            ]:
                continue  
            card.untap()


    ## Special Cards

    def play_land(self):
        for card in self.hand:
            if card.is_land:
                self.hand.remove(card)
                self.battlefield.append(card)
                return card

    def play_mox(self):
        for card in self.hand:
            if card.name in [
                "Lotus Petal",
                "Mox Opal",
                "Mox Amber",
                "Mox Ruby",
                "Mox Sapphire",
                "Mox Jet",
                "Mox Pearl",
                "Mox Emerald",
            ]:
                self.hand.remove(card)
                self.battlefield.append(card)


            if card.name == "Mox Diamond" and any(c.is_land for c in self.hand):
                self.hand.remove(card)
                self.battlefield.append(card)
                for c in self.hand:
                    if c.is_land:
                        self.hand.remove(c)
                        self.graveyard.append(c)
                        break  # discard only one land

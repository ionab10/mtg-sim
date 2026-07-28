import json
from random import randint, shuffle

class Card:

    def __init__(self, name, card_types=[]):
        self.name = name
        self.is_tapped = False
        self.card_types = card_types
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

    def is_artifact(self):
        return "Artifact" in self.card_types
    
    def is_land(self):
        return "Land" in self.card_types

    def __repr__(self):
        return f"[{self.name}] {'tapped' if self.is_tapped else 'untapped'}"


class Game:
    def __init__(self, library, format, commanders=[]):
        self.library = library
        self.hand = []
        self.graveyard = []
        self.exile = []
        self.command_zone = commanders
        self.mana_pool = {
            "W": 0,
            "U": 0,
            "B": 0,
            "R": 0,
            "G": 0,
            "C": 0,
        }
        self.battlefield = []
        if format == "EDH":
            self.life_total = 40
            self.seat_number = randint(1, 4)  # Random seat number for EDH format
        else:
            self.life_total = 20
            self.seat_number = randint(1, 2)  # Random seat number for other formats
        self.turn_number = 0

        self.LANDS = json.load(open("static/lands.json", "r"))
        self.LAND_ORDER = []

        # Cards that should not be pitched to exile for effects such as Chrome Mox or Gemstone Caverns
        self.DO_NOT_PITCH = []
    
    @staticmethod
    def _get_available_mana(available_mana, pip=None):
        """Get the total mana available to satisfy a pip"""

        total = 0
        for col, n in available_mana.items():
            if pip is None or pip in col:
                total += n

        return total
    
    ## Game Actions

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
        
    def pitch(self, require_nonland=False, require_nonartifact=False, exclude=[]):
        """Pitch a card from the hand to exile.

        e.g. for Chrome Mox, Gemstone Caverns, etc
        
        """
        for card in self.hand:

            if card.name in exclude:
                continue

            if require_nonland and card.is_land():
                continue

            if require_nonartifact and card.is_artifact():
                continue

            self.hand.remove(card)
            self.exile.append(card)
            return card
        raise ValueError("No valid cards to pitch.")
        
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
        
    ### Phases

    def pregame(self):
        """Handle pregame actions."""

        # Gemstone Caverns
        self.pregame_gemstone_caverns()

    def start_turn(self):
        self.turn_number += 1
        
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

    def first_main_phase(self):
        """Simulate the first main phase of the game."""
        # Play a land if available
        self.play_land()
        
        self.play_mox()


    def end_step(self):
        """Handle end step actions."""
        # reset mana pool
        for c in self.mana_pool:
            self.mana_pool[c] = 0

    def opponent_turn(self):
        # this is where you might simulate Rhystic Study or Esper Sentinel draws
        pass
        

    ## Helper Functions

    def count_available_mana(self):
        """Count the available mana in the mana pool."""
        available_mana = self.mana_pool.copy()
        available_mana.update({
            "CWUBRG": 0,
            "WUBRG": 0,
            "WU": 0,
            "WB": 0,
            "WR": 0,
            "WG": 0,
            "UB": 0,
            "UR": 0,
            "UG": 0,
            "BR": 0,
            "BG": 0,
            "RG": 0,
        })


        for card in self.battlefield:

            ## LANDS and mana rocks
            if not card.is_tapped:
                if card.name == "Gemstone Caverns":
                    if card.counters.get("luck", 0) > 0:
                        available_mana["WUBRG"] += 1
                    else:
                        available_mana["C"] += 1

                elif card.is_land():
                    for land_info in self.LANDS:
                        if card.name == land_info["name"]:
                            for color in land_info["produces"]:
                                available_mana[color] += 1

                elif card.name in ["Chrome Mox", "Lotus Petal", "Mox Diamond"]:
                    available_mana["WUBRG"] += 1

                elif card.name in ["Sol Ring"]:
                    available_mana["C"] += 2

                elif card.name in ["Mana Vault", "Grim Monolith", "Basalt Monolith"]:
                    available_mana["C"] += 3

        # Other instant mana

        for card in self.hand:
            
            if card.name == "Simian Spirit Guide":
                available_mana["R"] += 1

        ## Rituals
        
        # Rite of Flame costs R, and would net one extra R
        if self._get_available_mana(available_mana, "R") >= 1:
            if any(card.name == "Rite of Flame" for card in self.hand):
                available_mana["R"] += 1

        # Pyretic Ritual costs 1R, and would net one extra R
        if self._get_available_mana(available_mana, "R") >= 1 and self._get_available_mana(available_mana) >= 2:
            if any(card.name == "Pyretic Ritual" for card in self.hand):
                available_mana["R"] += 1

        # Seething Song costs 2R, and would net 2 extra R
        if self._get_available_mana(available_mana, "R") >= 1 and self._get_available_mana(available_mana) >= 3:
            if any(card.name == "Seething Song" for card in self.hand):
                available_mana["R"] += 2

        # todo: Jeska's Will

        return available_mana


    ## Special Cards

    def play_land(self):
        self.hand.sort(key=lambda c: self.LAND_ORDER.index(c.name) if c.name in self.LAND_ORDER else len(self.LAND_ORDER))
        for card in self.hand:
            self.hand.remove(card)
            self.battlefield.append(card)
            for land_info in self.LANDS:
                if card.name == land_info["name"]:
                    if land_info["enters_tapped"]:
                        card.tap()

            # check for City of Traitors and sacrifice it because you played another land
            for c in self.battlefield:
                if c.name == "City of Traitors":
                    self.sacrifice(c)

            return card
        

    def play_mox(self, do_not_imprint=[]):
        """
        do_not_imprint: list of card names that should not be imprinted on Chrome Mox
        """

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

            elif card.name == "Mox Diamond" and any(c.is_land() for c in self.hand):
                self.hand.remove(card)
                self.battlefield.append(card)
                for c in self.hand:
                    if c.is_land():
                        self.hand.remove(c)
                        self.graveyard.append(c)
                        break  # discard only one land

            # chrome mox
            elif card.name == "Chrome Mox" and any((not c.is_land() and not c.is_artifact()) for c in self.hand):
                
                try:
                    self.pitch(
                        require_nonland=True,
                        require_nonartifact=True,
                        exclude=do_not_imprint + self.DO_NOT_PITCH
                    )

                    self.hand.remove(card)
                    self.battlefield.append(card)
                except ValueError:
                    # No valid cards to imprint, skip playing Chrome Mox
                    continue

            # todo: Lion's Eye Diamond

    def pregame_gemstone_caverns(self, exclude=[]):
        if self.seat_number == 1:
            return  # Gemstone Caverns can only be played if you are not the first player
        
        for card in self.hand:
            if card.name == "Gemstone Caverns":

                try:
                    self.pitch(exclude=["Gemstone Caverns"] + exclude + self.DO_NOT_PITCH)
                    self.hand.remove(card)
                    self.battlefield.append(card)
                    card.counters["luck"] += 1  # Add a luck counter to Gemstone Caverns
                    return

                except ValueError:
                    # No valid cards to pitch, skip playing Gemstone Caverns
                    continue

    # Check if the game state meets the success criteria
    def check_success(self):
        """Check if the game state meets the success criteria."""
        return False  # Default implementation, override in subclasses
import warnings

from game import Game


class ZirdaGame(Game):

    LAND_ORDER = [
        # 3 mana
        "Mishra's Workshop",

        # 2 mana
        "Ancient Tomb",
        "City of Traitors",

        # coloured mana
        "Battlefield Forge",
        "Cavern of Souls",
        "City of Brass",
        "Command Tower",
        "Fogwell's Gym",
        "Mana Confluence",
        "Plateau",
        "Sacred Foundry",
        "Spectator Seating",
        "Sunbaked Canyon",

        # tapped coloured mana,
        "Elegant Parlor",
        "Remote Farm",
    ]

    def __init__(self, library, commanders=[]):
        super().__init__(library, "EDH", commanders)

    def play_land(self):
        for land in self.LAND_ORDER:
            for card in self.hand:
                if card.name == land:
                    self.hand.remove(card)
                    self.battlefield.append(card)
                    return card
        for card in self.hand:
            if card.is_land:
                self.hand.remove(card)
                self.battlefield.append(card)
                return card

    # override
    def first_main_phase(self):

        # play land
        self.play_land()

        # fetch lands    
        for card in self.battlefield:
            if card.name in [
                "Arid Mesa",
                "Flooded Strand",
                "Marsh Flats",
                "Windswept Heath",
            ]:
                card.tap()
                self.life_total -= 1
                self.sacrifice(card)
                tutored = self.tutor(["Plateau", "Sacred Foundry", "Elegant Parlor"], to_battlefield=True)
                if not tutored:
                    warnings.warn(f"Failed to tutor a land for {card.name}.")

        self.play_mox()

        # todo: play mana rocks
        # self.play_mana_rocks()

        # todo: tutor
        # self.tutor()
                    

    # override
    def count_available_mana(self):
        """Count the available mana in the mana pool."""
        available_mana =  {
            "coloured": 0,
            "C": 0,
        }

        for col, count in self.mana_pool.items():
            if col == "C":
                available_mana["C"] += count
            else:
                available_mana["coloured"] += count

        for card in self.battlefield:
            if not card.is_tapped and card.name == "Gemstone Caverns":
                if card.counters.get("luck", 0) > 0:
                    available_mana["coloured"] += 1
                else:
                    available_mana["C"] += 1

            if not card.is_tapped and card.name in [
                "Battlefield Forge",
                "Cavern of Souls",
                "City of Brass",
                "Command Tower",
                "Elegant Parlor",
                "Fogwell's Gym",
                "Mana Confluence",
                "Plateau",
                "Remote Farm",
                "Sacred Foundry",
                "Spectator Seating",
                "Sunbaked Canyon",
            ]:
                available_mana["coloured"] += 1

            elif not card.is_tapped and card.name in [
                "Abstergo Entertainment",
                "Emergence Zone",
                "Inventors' Fair",
                "Talon Gates of Madara",
                "Treasure Vault",
                "Urza's Saga",
            ]:
                available_mana["C"] += 1

            elif not card.is_tapped and card.name in [
                "Ancient Tomb",
                "City of Traitors",
            ]:
                available_mana["C"] += 2

            elif not card.is_tapped and card.name in [
                "Mishra's Workshop",
            ]:
                available_mana["C"] += 3

            elif not card.is_tapped and card.name in ["Lotus Petal", "Mox Diamond"]:
                available_mana["coloured"] += 1

        for card in self.hand:
            if card.name == "Simian Spirit Guide":
                available_mana["coloured"] += 1

            # todo: rituals

        return available_mana


    # override
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

            # todo: chrome mox


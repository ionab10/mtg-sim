import warnings

from game import Game


class ZirdaGame(Game):

    LAND_ORDER = [
        # 3 mana
        "Mishra's Workshop",

        # 2 mana
        "Ancient Tomb",
        "City of Traitors",

        # fetch lands
        "Arid Mesa",
        "Flooded Strand",
        "Marsh Flats",
        "Windswept Heath",

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

    INFINITE_MANA_WINCONS = [
        {"name": "Walking Ballista"},
        {"name": "Staff of Domination"},
        {"name": "Diviner's Wand"},
        {"name": "Kozilek's Command"},
        {"name": "Thran Spider"},
        {"name": "Cogwork Assembler"},
        {"name": "Apple of Eden, Isu Relic"},
        {"name": "Staff of Compleation"},
        {"name": "Goblin Cannon"},
        {"name": "Dino DNA"},
        {"name": "Chrome Dome"},

        # these are debatable because it assumes another player has a wincon that you can copy
        # {"name": "Mirage Mirror"},  
        # {"name": "Avarice Totem"},

        # wincons that require coloured mana
        {"name": "Water Tribe Rallier", "cost": ["1", "W"]},
        {"name": "Godo, Bandit Warlord", "cost": ["5", "R"]},
        {"name": "Zuko, Exiled Prince", "cost": ["3", "R"]},
        {"name": "Ranger Captain of Eos", "cost": ["1", "W", "W"]},
        {"name": "Imperial Recruiter", "cost": ["2", "R"]},
        {"name": "Recruiter of the Guard", "cost": ["2", "W"]}
    ]

    def __init__(self, library, commanders=[]):
        super().__init__(library, "EDH", commanders)

        self.mana_pool["artifact"] = 0  # Track generic mana for artifacts


    # override
    def pregame_gemstone_caverns(self):
        """Handle pregame actions."""

        # Gemstone Caverns
        for card in self.hand:
            if card.name == "Gemstone Caverns" and self.seat_number != 1:
                self.hand.remove(card)
                self.battlefield.append(card)
                card.counters["luck"] += 1  # Add a luck counter to Gemstone Caverns

                # must exile a card from hand to play Gemstone Caverns
                for c in self.hand:
                    if c.name in ["Grim Monolith", "Basalt Monolith"] or c.name in [wincon["name"] for wincon in self.INFINITE_MANA_WINCONS]:
                        continue  # Skip these cards
                    self.hand.remove(c)
                    self.exile.append(c)
                    break  # Exile only one card


    # override
    def play_land(self):
        for land in self.LAND_ORDER:
            for card in self.hand:
                if card.name == land:
                    self.hand.remove(card)
                    self.battlefield.append(card)
                    return card
        for card in self.hand:
            if card.is_land():
                self.hand.remove(card)
                self.battlefield.append(card)
                return card
            

    def pay_one_generic(self, for_artifact=False):

        # if is for artifact, pay from artifact mana pool first
        
        if for_artifact:
            # check mana pool
            if self.mana_pool["artifact"] > 0:
                self.mana_pool["artifact"] -= 1
                return
        
            for card in self.battlefield:
                if card.name == "Mishra's Workshop" and not card.is_tapped:
                    card.tap()
                    self.mana_pool["artifact"] += 3
                    self.mana_pool["artifact"] -= 1
                    return

        # pay from colourless mana pool first
        if self.mana_pool["C"] > 0:
            self.mana_pool["C"] -= 1
            return
        
        # then use Sol Ring if available
        for card in self.battlefield:
            if card.name == "Sol Ring" and not card.is_tapped:
                card.tap()
                self.mana_pool["C"] += 2
                self.mana_pool["C"] -= 1  # Pay 1 generic
                return

        # then pay from coloured mana pool if available
        for c in self.mana_pool:
            if self.mana_pool[c] > 0:
                self.mana_pool[c] -= 1
                return


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
                self.shuffle()

        self.play_mox()

        
        if self.check_success():
            return  # Stop if success criteria is met

        # Play mana rocks

        for card in self.hand:
            if card.name in [
                "Sol Ring",
                "Mana Vault",
            ]:
                self.hand.remove(card)
                self.pay_one_generic(for_artifact=True)  # Pay 1 generic mana to play the artifact
                self.battlefield.append(card)


        if self.check_success():
            return  # Stop if success criteria is met

        # todo: play tutors
            

    def check_success(self):
        """Check if the game state meets the success criteria."""
        available_mana = self.count_available_mana()
        coloured = 0
        colourless = 0
    
        for col, count in available_mana.items():
            if col == "C":
                colourless += count
            else:
                coloured += count

        if coloured >= 2 and coloured + colourless >= 4:
            return True
        return False
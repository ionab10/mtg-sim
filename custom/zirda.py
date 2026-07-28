from game import Game


class ZirdaGame(Game):

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

    @staticmethod
    def _land_sort(x):
        # calculate land order based on
        # 1. enters untapped
        # 2. multiple mana
        # 3. fetch lands
        # 4. coloured mana
        # 5. colourless mana
        return (
            x["enters_tapped"],
            -max(len(x["produces"]), 1),
            -(1 if x.get("is_fetch", False) else 0),
            -(len(x["produces"][0].strip("C")) if x["produces"] else 0),
            x["name"]
        )

    def __init__(self, library, commanders=[]):
        super().__init__(library, "EDH", commanders)

        self.mana_pool["artifact"] = 0  # Track generic mana for artifacts
        self.LAND_ORDER = [land["name"] for land in sorted(self.LANDS, key=self._land_sort)]

        self.DO_NOT_PITCH = ["Grim Monolith", "Basalt Monolith"] #+ [wincon["name"] for wincon in self.INFINITE_MANA_WINCONS]

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
                tutored = self.tutor(["Plateau", "Sacred Foundry", "Elegant Parlor"], destination="battlefield")
                if not tutored:
                    print(f"Warning: Failed to tutor a land for {card.name}.")
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
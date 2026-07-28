from game import Game


class CustomGame(Game):

    # Add constants here such as card orders

    def __init__(self, library, commanders=[]):
        super().__init__(library, "EDH", commanders)

        # Overring DO_NOT_PITCH here for example:
        # self.DO_NOT_PITCH = ["Grim Monolith", "Basalt Monolith"]

    # override
    def first_main_phase(self):

        # play land
        self.play_land()

        self.play_mox()

        # Play mana rocks

        if self.check_success():
            return  # Stop if success criteria is met
            

    def check_success(self):
        """Check if the game state meets the success criteria."""
        return False  # Replace with actual success criteria
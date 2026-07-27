from custom.zirda import ZirdaGame
from game import Card


def make_card(name: str, card_types: list[str] = None) -> Card:
	return Card(name, card_types=card_types or [])


def make_game(*, hand=None, library=None, battlefield=None, mana_pool=None) -> ZirdaGame:
	game = ZirdaGame(library or [])
	game.hand = hand or []
	game.battlefield = battlefield or []
	if mana_pool is not None:
		game.mana_pool = mana_pool
	return game

def test_pregame_gemstone_caverns_does_not_pitch_monolith():
	gemstone = Card("Gemstone Caverns", card_types=["Land"])
	game = make_game(
		hand=[
			gemstone,
			make_card("Grim Monolith", card_types=["Artifact"]),
			make_card("Mountain", card_types=["Land"]),
			make_card("Mountain", card_types=["Land"]),
			make_card("Mountain", card_types=["Land"]),
			make_card("Mountain", card_types=["Land"]),
			make_card("Mountain", card_types=["Land"]),
		]
	)
	game.seat_number = 2

	game.pregame()

	assert gemstone in game.battlefield
	assert gemstone not in game.hand
	assert gemstone.counters["luck"] == 1
	assert len(game.hand) == 5
	assert any(card.name == "Grim Monolith" for card in game.hand)


def test_play_land_prefers_land_order_over_other_lands():
	game = make_game(
		hand=[
			make_card("Command Tower", card_types=["Land"]),
			make_card("Mishra's Workshop", card_types=["Land"]),
			make_card("Island", card_types=["Land"]),
		]
	)

	played = game.play_land()

	assert played is not None
	assert played.name == "Mishra's Workshop"
	assert any(card.name == "Mishra's Workshop" for card in game.battlefield)
	assert all(card.name != "Mishra's Workshop" for card in game.hand)


def test_land_order_matches_expected_priority_list():
	game = make_game()

	expected_order = [
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

			# WUBRG
			"Cavern of Souls",
            "City of Brass",
			"Command Tower",
			"Mana Confluence",

            # coloured mana
            "Battlefield Forge",
            "Plateau",
            "Sacred Foundry",
            "Spectator Seating",
            "Sunbaked Canyon",

			"Fogwell's Gym",

            # tapped coloured mana,
			"Remote Farm",
			
            "Elegant Parlor",
            
        ]


	actual_expected_lands_in_order = [
		land for land in game.LAND_ORDER if land in expected_order
	]
	print(actual_expected_lands_in_order)

	assert actual_expected_lands_in_order == expected_order


def test_first_main_phase_fetches_and_loses_life_with_arid_mesa():
	arid_mesa = make_card("Arid Mesa", card_types=["Land"])
	game = make_game(
		hand=[arid_mesa],
		library=[
			make_card("Plateau", card_types=["Land"]),
			make_card("Mountain", card_types=["Land"]),
		],
	)
	starting_life = game.life_total

	game.first_main_phase()

	assert game.life_total == starting_life - 1
	assert all(card.name != "Arid Mesa" for card in game.battlefield)
	assert any(card.name == "Arid Mesa" for card in game.graveyard)
	assert any(card.name == "Plateau" for card in game.battlefield)


def test_first_main_phase_uses_mishras_workshop_to_cast_sol_ring():
	game = make_game(
		hand=[
			make_card("Mishra's Workshop", card_types=["Land"]),
			make_card("Sol Ring", card_types=["Artifact"]),
		]
	)

	game.first_main_phase()

	workshop = next(card for card in game.battlefield if card.name == "Mishra's Workshop")

	assert any(card.name == "Sol Ring" for card in game.battlefield)
	assert workshop.is_tapped is True
	assert game.mana_pool["artifact"] == 2
	assert all(card.name not in {"Mishra's Workshop", "Sol Ring"} for card in game.hand)


def test_check_success_requires_at_least_two_coloured_and_two_colourless():
	game = make_game(
		mana_pool={"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0},
		battlefield=[
			make_card("Command Tower", card_types=["Land"]),
			make_card("Plateau", card_types=["Land"]),
			make_card("Ancient Tomb", card_types=["Land"]),
		],
	)

	assert game.check_success() is True


def test_check_success_fails_when_colourless_threshold_not_met():
	game = make_game(
		mana_pool={"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0},
		battlefield=[
			make_card("Command Tower", card_types=["Land"]),
			make_card("Plateau", card_types=["Land"]),
			make_card("Battlefield Forge", card_types=["Land"]),
		],
	)

	assert game.check_success() is False

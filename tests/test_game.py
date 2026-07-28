from game import Card, Game


def make_card(name: str, card_types: list[str] = None) -> Card:
	return Card(name, card_types=card_types or [])


def make_game(*, hand=None, library=None, battlefield=None, mana_pool=None) -> Game:
	game = Game(library or [], format="EDH")
	game.hand = hand or []
	game.battlefield = battlefield or []
	if mana_pool is not None:
		game.mana_pool = mana_pool
	return game


def test_pregame_gemstone_caverns_moves_to_battlefield_and_gets_luck_if_not_first_seat():
	gemstone = Card("Gemstone Caverns", card_types=["Land"])
	game = Game(library=[], format="EDH")
	game.hand = [
		gemstone,
		Card("Mountain", card_types=["Land"]),
		Card("Mountain", card_types=["Land"]),
		Card("Mountain", card_types=["Land"]),
		Card("Mountain", card_types=["Land"]),
		Card("Mountain", card_types=["Land"]),
		Card("Mountain", card_types=["Land"]),
	]
	game.seat_number = 2

	game.pregame()

	assert gemstone in game.battlefield
	assert gemstone not in game.hand
	assert gemstone.counters["luck"] == 1
	assert len(game.hand) == 5


def test_play_mox_diamond_requires_lands_to_discard_from_hand():
	mox_diamond = make_card("Mox Diamond")
	command_tower = make_card("Command Tower", card_types=["Land"])
	game = make_game(hand=[mox_diamond, command_tower])

	game.play_mox()

	assert any(card.name == "Mox Diamond" for card in game.battlefield)
	assert any(card.name == "Command Tower" for card in game.graveyard)
	assert all(card.name not in {"Mox Diamond", "Command Tower"} for card in game.hand)


def test_count_available_mana_includes_gemstone_luck_and_spirit_guide():
	gemstone_with_luck = make_card("Gemstone Caverns", card_types=["Land"])
	gemstone_with_luck.counters["luck"] = 1
	ancient_tomb = make_card("Ancient Tomb", card_types=["Land"])
	lotus_petal = make_card("Lotus Petal")
	spirit_guide = make_card("Simian Spirit Guide")

	game = make_game(
		hand=[spirit_guide],
		battlefield=[gemstone_with_luck, ancient_tomb, lotus_petal],
		mana_pool={"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 1},
	)

	available = game.count_available_mana()

	assert available["WUBRG"] == 2  # Gemstone + Lotus Petal
	assert available["R"] == 1  # Spirit Guide
	assert available["C"] == 3  # pool(1) + Ancient Tomb(2)


def test_tutor_to_top_of_library_places_card_as_next_draw():
	target = make_card("Pyretic Ritual")
	other = make_card("Mountain", card_types=["Land"])
	game = make_game(library=[target, other])

	tutored = game.tutor(["Pyretic Ritual"], destination="top_of_library")

	assert tutored is target
	assert game.library[-1] is target
	assert game.draw() is target

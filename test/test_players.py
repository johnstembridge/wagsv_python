import unittest

from back_end.players import Player, Players


class TestPlayers(unittest.TestCase):
    def test_make_player(self):
        player = Player(12)
        self.assertEqual(player.name, 'John Stembridge')

    def test_player_with_salutation(self):
        player = Player.normalise_name('Andrew Burn')
        self.assertEqual(player, 'Andy Burn')

    def test_get_current_members(self):
        x = Players().get_current_members()
        self.assertTrue(len(x) > 0)

    def test_name_to_id(self):
        x = Players().name_to_id('John Stembridge')
        self.assertEqual(x, 12)

    def test_name_to_id_multi(self):
        x = Players().name_to_id(['John Stembridge', 'Peter Berring'])
        self.assertEqual(x, [12, 2])

    def test_id_to_name(self):
        x = Players().id_to_name(12)
        self.assertEqual(x, 'John Stembridge')

    def test_id_to_name_multi(self):
        x = Players().id_to_name([12, 2])
        self.assertEqual(x, ['John Stembridge', 'Peter Berring'])


if __name__ == '__main__':
    unittest.main()

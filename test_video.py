import unittest
from video import Score, Rallies, Rally, Video
from unittest.mock import MagicMock, patch

class TestScore(unittest.TestCase):
    def test_init_score(self):
        score = Score()
        self.assertEqual(score.sets, [[0,0],[0,0],[0,0]], "Should be empty score")

    def test_get_current_set(self):
        score = Score([[0,0],[0,0],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 0, "Should be 0")
        self.assertEqual(set_, [0,0], "Should be [0,0]")

        score = Score([[15,6],[0,0],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 0, "Should be 0")
        self.assertEqual(set_, [15,6], "Should be [0,0]")

        score = Score([[25,26],[0,0],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 0, "Should be 0")
        self.assertEqual(set_, [25,26], "Should be [25,26]")

        score = Score([[30,29],[0,0],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 1, "Should be 1")
        self.assertEqual(set_, [0,0], "Should be [0,0]")

        score = Score([[18,21],[0,0],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 1, "Should be 1")
        self.assertEqual(set_, [0,0], "Should be [0,0]")

        score = Score([[18,21],[0,8],[0,0]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 1, "Should be 1")
        self.assertEqual(set_, [0,8], "Should be [0,8]")

        score = Score([[18,21],[21,19],[0,9]])
        index, set_ = score.get_current_set()
        self.assertEqual(index, 2, "Should be 2")
        self.assertEqual(set_, [0,9], "Should be [0,9]")

    def test_increment(self):
        score = Score([[0,0],[0,0],[0,0]])
        self.assertEqual(score.get_score(), [[0,0],[0,0],[0,0]], "Should be [[0,0],[0,0],[0,0]]")
        score.increment([1,0])
        self.assertEqual(score.get_score(), [[1,0],[0,0],[0,0]], "Should be [1,0]...")
        score.increment([3,21])
        self.assertEqual(score.get_score(), [[4, 21],[0,0],[0,0]], "Should be...")
        score.increment([1,2])
        self.assertEqual(score.get_score(), [[4, 21],[1,2],[0,0]], "Should be...")

class TestRally(unittest.TestCase):
    def test_increment(self):
        rally = Rally(0, 300, Score())
        rally.increment_score([0,9])
        self.assertEqual(rally.end_score.get_score(), [[0,9], [0,0], [0,0]])

class TestRallies(unittest.TestCase):
    def test_init(self):
        rallies = Rallies(300)
        # Test initial rally creation
        self.assertEqual(len(rallies.rallies), 1, "Should start with one rally")
        self.assertEqual(rallies.rallies[0].start_frame, 0, "Initial rally should start at frame 0")
        self.assertEqual(rallies.rallies[0].end_frame, 300, "Initial rally should end at total frames (300)")
        self.assertEqual(rallies.rallies[0].start_score.get_score(), [[0,0],[0,0],[0,0]], "Initial score should be all zeros")
    
    def test_get_rally_index(self):
        rallies = Rallies(300)
        rally = rallies.get_rally_index(0)
        # Test getting rally by index
        self.assertEqual(rally.start_frame, 0, "Should get rally with start frame 0")
        self.assertEqual(rally.end_frame, 300, "Should get rally with end frame 300")
    
    def test_get_rally(self):
        rallies = Rallies(300)
        rally = rallies.get_rally(100)
        # Test getting rally by frame number
        self.assertIsNotNone(rally, "Rally should be found for frame 100")
        self.assertEqual(rally.start_frame, 0, "Rally should start at frame 0")
        self.assertEqual(rally.end_frame, 300, "Rally should end at frame 300")
        
        rally = rallies.get_rally(400)
        # Test getting rally for out-of-bound frame number
        self.assertFalse(rally, "No rally should exist for frame 400")
    
    def test_get_rally_before_break(self):
        rallies = Rallies(200)
        rallies.append(300, 500)
        rallies.append(700, 900)
        
        index, rally = rallies.get_rally_before_break(600)
        # Test rally before break (frame between two rallies)
        self.assertEqual(index, 1, "Should return the index of the first rally before break")
        
        result = rallies.get_rally_before_break(400)
        # Test when no rally break is found
        self.assertFalse(result[0], "Should return False if no rally break is found")
    
    def test_append(self):
        rallies = Rallies(300)
        rallies.append(300, 600)
        self.assertEqual(len(rallies.rallies), 2, "There should be 2 rallies after append")
        self.assertEqual(rallies.rallies[1].start_frame, 300, "Second rally should start at frame 300")
        self.assertEqual(rallies.rallies[1].end_frame, 600, "Second rally should end at frame 600")
    
    def test_pop(self):
        rallies = Rallies(300)
        rallies.append(300, 600)
        rallies.pop(1)
        # Test popping rally
        self.assertEqual(len(rallies.rallies), 1, "There should be 1 rally after pop")
        self.assertEqual(rallies.rallies[0].start_frame, 0, "Remaining rally should start at frame 0")
        self.assertEqual(rallies.rallies[0].end_frame, 300, "Remaining rally should end at frame 300")





if __name__ == "__main__":
    unittest.main()
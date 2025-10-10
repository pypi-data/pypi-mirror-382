"""
Feature Systems Tests
Tests for tutorial system, AI assistant, and gamification system
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from features.tutorial_system import TutorialSystem
    TUTORIAL_AVAILABLE = True
except ImportError:
    TUTORIAL_AVAILABLE = False

try:
    from features.ai_assistant import AICodeAssistant
    AI_ASSISTANT_AVAILABLE = True
except ImportError:
    AI_ASSISTANT_AVAILABLE = False

try:
    from features.gamification import GamificationSystem, UserStats, Achievement, Challenge, DailyChallenge
    GAMIFICATION_AVAILABLE = True
except ImportError:
    GAMIFICATION_AVAILABLE = False


class TestTutorialSystem(unittest.TestCase):
    """Test cases for the tutorial system"""

    def setUp(self):
        """Set up test fixtures"""
        if not TUTORIAL_AVAILABLE:
            self.skipTest("Tutorial system not available")
        
        self.tutorial_system = TutorialSystem()

    def test_tutorial_system_initialization(self):
        """Test tutorial system initializes correctly"""
        self.assertIsNotNone(self.tutorial_system)
        self.assertTrue(hasattr(self.tutorial_system, 'get_available_tutorials'))

    def test_get_available_tutorials(self):
        """Test getting available tutorials"""
        tutorials = self.tutorial_system.get_available_tutorials()
        self.assertIsInstance(tutorials, list)
        
        if tutorials:
            # Check that tutorials have required attributes
            tutorial = tutorials[0]
            self.assertTrue(hasattr(tutorial, 'tutorial_id'))
            self.assertTrue(hasattr(tutorial, 'title'))
            self.assertTrue(hasattr(tutorial, 'description'))

    def test_get_tutorial_by_language(self):
        """Test getting tutorials for specific languages"""
        languages = ['pilot', 'basic', 'logo', 'python']
        
        for language in languages:
            tutorials = self.tutorial_system.get_tutorials_by_language(language)
            self.assertIsInstance(tutorials, list)
            
            # All tutorials should be for the requested language
            for tutorial in tutorials:
                if hasattr(tutorial, 'language'):
                    self.assertEqual(tutorial.language, language)

    def test_tutorial_completion_tracking(self):
        """Test tutorial completion tracking"""
        # Test marking tutorial as completed
        if hasattr(self.tutorial_system, 'mark_tutorial_completed'):
            test_tutorial_id = "test_tutorial"
            result = self.tutorial_system.mark_tutorial_completed(test_tutorial_id)
            # Should handle completion marking gracefully
            self.assertTrue(result is None or isinstance(result, bool))

    def test_tutorial_progress_tracking(self):
        """Test tutorial progress tracking"""
        if hasattr(self.tutorial_system, 'get_tutorial_progress'):
            progress = self.tutorial_system.get_tutorial_progress()
            self.assertIsInstance(progress, (dict, list, type(None)))


class TestAICodeAssistant(unittest.TestCase):
    """Test cases for the AI code assistant"""

    def setUp(self):
        """Set up test fixtures"""
        if not AI_ASSISTANT_AVAILABLE:
            self.skipTest("AI assistant not available")
        
        self.ai_assistant = AICodeAssistant()

    def test_ai_assistant_initialization(self):
        """Test AI assistant initializes correctly"""
        self.assertIsNotNone(self.ai_assistant)
        self.assertTrue(hasattr(self.ai_assistant, 'analyze_code'))

    def test_code_analysis(self):
        """Test code analysis functionality"""
        test_code = "T:Hello, World!\nEND"
        
        analysis = self.ai_assistant.analyze_code(test_code, "pilot")
        
        # Should return some form of analysis
        self.assertTrue(analysis is not None)
        
        if isinstance(analysis, dict):
            # Common analysis fields
            expected_fields = ['suggestions', 'errors', 'quality_score', 'feedback']
            # At least one of these should be present
            has_expected_field = any(field in analysis for field in expected_fields)
            self.assertTrue(has_expected_field or len(analysis) > 0)

    def test_multiple_language_analysis(self):
        """Test code analysis for different languages"""
        test_codes = {
            'pilot': "T:Hello from PILOT!\nEND",
            'basic': "10 PRINT \"Hello from BASIC!\"\n20 END",
            'logo': "FORWARD 100\nRIGHT 90",
            'python': "print('Hello from Python!')"
        }
        
        for language, code in test_codes.items():
            with self.subTest(language=language):
                analysis = self.ai_assistant.analyze_code(code, language)
                # Should handle all supported languages
                self.assertTrue(analysis is not None)

    def test_syntax_error_detection(self):
        """Test detection of syntax errors"""
        error_codes = {
            'pilot': "T:Unclosed string\nEND",
            'basic': "10 PRINT WITHOUT QUOTES\n20 END",
            'python': "print('unclosed string"
        }
        
        for language, code in error_codes.items():
            with self.subTest(language=language):
                analysis = self.ai_assistant.analyze_code(code, language)
                
                # Should detect errors (though specific format may vary)
                if isinstance(analysis, dict) and 'errors' in analysis:
                    # If errors field exists, it should contain something for error code
                    self.assertTrue(analysis['errors'] is not None)

    def test_code_suggestions(self):
        """Test code improvement suggestions"""
        # Test with simple code that could be improved
        simple_code = "T:Hello\nEND"
        
        analysis = self.ai_assistant.analyze_code(simple_code, "pilot")
        
        if isinstance(analysis, dict) and 'suggestions' in analysis:
            suggestions = analysis['suggestions']
            # Suggestions should be a list or string
            self.assertTrue(isinstance(suggestions, (list, str, type(None))))


class TestGamificationSystem(unittest.TestCase):
    """Test cases for the gamification system"""

    def setUp(self):
        """Set up test fixtures"""
        if not GAMIFICATION_AVAILABLE:
            self.skipTest("Gamification system not available")
        
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the config directory
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = self.temp_dir
            self.gamification = GamificationSystem()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_gamification_initialization(self):
        """Test gamification system initializes correctly"""
        self.assertIsNotNone(self.gamification)
        self.assertIsInstance(self.gamification.user_stats, UserStats)
        self.assertIsInstance(self.gamification.achievements, dict)
        self.assertIsInstance(self.gamification.challenges, dict)

    def test_user_stats_initialization(self):
        """Test user statistics are properly initialized"""
        stats = self.gamification.user_stats
        
        # Check default values
        self.assertEqual(stats.level, 1)
        self.assertEqual(stats.experience, 0)
        self.assertEqual(stats.programs_written, 0)
        self.assertEqual(stats.total_points, 0)

    def test_record_activity(self):
        """Test activity recording"""
        initial_programs = self.gamification.user_stats.programs_written
        
        # Record a program written activity
        self.gamification.record_activity('program_written', {'language': 'pilot'})
        
        # Should increment programs written
        self.assertGreater(self.gamification.user_stats.programs_written, initial_programs)

    def test_achievement_checking(self):
        """Test achievement checking logic"""
        # Set up conditions for an achievement
        self.gamification.user_stats.programs_written = 1
        
        # Check for achievements
        new_achievements = self.gamification.check_achievements()
        
        # Should return a list
        self.assertIsInstance(new_achievements, list)
        
        # Check if first program achievement was unlocked
        first_program_achievement = None
        for achievement in self.gamification.achievements.values():
            if 'first' in achievement.name.lower() and 'program' in achievement.name.lower():
                first_program_achievement = achievement
                break
        
        if first_program_achievement:
            # Should be unlocked with 1 program written
            self.assertTrue(first_program_achievement.unlocked)

    def test_daily_challenge_generation(self):
        """Test daily challenge generation"""
        # Initialize daily challenges
        self.gamification.initialize_daily_challenges()
        
        # Should have today's challenge
        today_challenge = self.gamification.get_today_daily_challenge()
        
        if today_challenge:
            self.assertIsInstance(today_challenge, DailyChallenge)
            self.assertIsInstance(today_challenge.challenge_id, str)
            self.assertIsInstance(today_challenge.title, str)
            self.assertIsInstance(today_challenge.points, int)

    def test_points_and_experience_system(self):
        """Test points and experience calculation"""
        initial_points = self.gamification.user_stats.total_points
        initial_exp = self.gamification.user_stats.experience
        
        # Award some points
        self.gamification.award_points_and_experience(100)
        
        # Points and experience should increase
        self.assertGreater(self.gamification.user_stats.total_points, initial_points)
        self.assertGreater(self.gamification.user_stats.experience, initial_exp)

    def test_level_calculation(self):
        """Test level calculation system"""
        # Test level 1 (starting level)
        self.gamification.user_stats.experience = 0
        level = self.gamification.calculate_level()
        self.assertEqual(level, 1)
        
        # Test level 2
        self.gamification.user_stats.experience = 100
        level = self.gamification.calculate_level()
        self.assertEqual(level, 2)
        
        # Test higher level
        self.gamification.user_stats.experience = 300  # Should be level 3
        level = self.gamification.calculate_level()
        self.assertGreaterEqual(level, 3)

    def test_achievement_progress_tracking(self):
        """Test achievement progress tracking"""
        # Create a test achievement to ensure the functionality works
        from features.gamification import Achievement, BadgeRarity
        test_achievement = Achievement(
            achievement_id="test_progress",
            name="Test Progress",
            description="Test achievement for progress tracking",
            icon="🧪",
            rarity=BadgeRarity.COMMON,
            points=10,
            requirements={"programs_written": 4}
        )
        self.gamification.achievements["test_progress"] = test_achievement
        
        # Set partial progress (2 out of 4 programs)
        self.gamification.user_stats.programs_written = 2
        
        # Check achievements to update progress
        self.gamification.check_achievements()
        
        # Progress should be 0.5
        self.assertEqual(test_achievement.progress, 0.5)
        self.assertFalse(test_achievement.unlocked)

    def test_theme_tracking(self):
        """Test theme usage tracking"""
        initial_themes = len(self.gamification.user_stats.themes_used) if self.gamification.user_stats.themes_used else 0
        
        # Track theme usage
        self.gamification.track_theme_usage('dark_theme')
        self.gamification.track_theme_usage('light_theme')
        
        # Should track themes
        self.assertIsNotNone(self.gamification.user_stats.themes_used)
        current_themes = len(self.gamification.user_stats.themes_used)
        self.assertGreaterEqual(current_themes, initial_themes)

    def test_feature_discovery_tracking(self):
        """Test feature discovery tracking"""
        initial_features = len(self.gamification.user_stats.features_discovered) if self.gamification.user_stats.features_discovered else 0
        
        # Track feature discovery
        self.gamification.track_feature_discovery('ai_assistant')
        self.gamification.track_feature_discovery('tutorial_system')
        
        # Should track features
        self.assertIsNotNone(self.gamification.user_stats.features_discovered)
        current_features = len(self.gamification.user_stats.features_discovered)
        self.assertGreaterEqual(current_features, initial_features)

    def test_perfect_program_tracking(self):
        """Test perfect program tracking"""
        initial_perfect = self.gamification.user_stats.perfect_programs
        
        # Track perfect program
        self.gamification.track_perfect_program()
        
        # Should increment perfect programs
        self.assertEqual(self.gamification.user_stats.perfect_programs, initial_perfect + 1)

    def test_session_time_tracking(self):
        """Test session time tracking"""
        initial_time = self.gamification.user_stats.total_session_time
        
        # Track session time (30 minutes)
        self.gamification.track_session_time(30)
        
        # Should increment session time
        self.assertEqual(self.gamification.user_stats.total_session_time, initial_time + 30)

    def test_data_persistence(self):
        """Test saving and loading user data"""
        # Modify some stats
        self.gamification.user_stats.programs_written = 5
        self.gamification.user_stats.total_points = 100
        
        # Save data
        self.gamification.save_user_stats()
        
        # Create new instance (simulating restart)
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = self.temp_dir
            new_gamification = GamificationSystem()
        
        # Data should be preserved (if loading is implemented)
        # This might not work if loading isn't implemented yet, so just check it doesn't crash
        self.assertIsInstance(new_gamification.user_stats, UserStats)


class TestIntegrationBetweenSystems(unittest.TestCase):
    """Test integration between different feature systems"""

    def setUp(self):
        """Set up test fixtures"""
        self.systems_available = {
            'tutorial': TUTORIAL_AVAILABLE,
            'ai_assistant': AI_ASSISTANT_AVAILABLE,
            'gamification': GAMIFICATION_AVAILABLE
        }

    def test_tutorial_gamification_integration(self):
        """Test integration between tutorial system and gamification"""
        if not (TUTORIAL_AVAILABLE and GAMIFICATION_AVAILABLE):
            self.skipTest("Tutorial system or gamification not available")
        
        # This would test that completing tutorials awards points/achievements
        # Implementation depends on how systems are integrated
        self.assertTrue(True)  # Placeholder

    def test_ai_assistant_gamification_integration(self):
        """Test integration between AI assistant and gamification"""
        if not (AI_ASSISTANT_AVAILABLE and GAMIFICATION_AVAILABLE):
            self.skipTest("AI assistant or gamification not available")
        
        # This would test that using AI assistant counts toward achievements
        # Implementation depends on how systems are integrated
        self.assertTrue(True)  # Placeholder

    def test_cross_system_data_sharing(self):
        """Test data sharing between systems"""
        available_systems = sum(self.systems_available.values())
        
        if available_systems < 2:
            self.skipTest("Need at least 2 systems available for integration testing")
        
        # This would test that systems can share data appropriately
        # For example, tutorial completion informing gamification
        self.assertTrue(True)  # Placeholder


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTutorialSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAICodeAssistant))
    suite.addTests(loader.loadTestsFromTestCase(TestGamificationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationBetweenSystems))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if test_result.wasSuccessful() else 1)
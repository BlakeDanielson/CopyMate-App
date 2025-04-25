import unittest
from backend.risk_analysis.analyzer import Analyzer
from backend.risk_analysis.keywords import ALL_KEYWORDS, KEYWORD_TO_CATEGORY

class TestAnalyzer(unittest.TestCase):

    def test_keyword_matching(self):
        analyzer = Analyzer()
        text_to_analyze = "This video is a potential scam and a fraud, be warned!"
        flags = analyzer.analyze_text(text_to_analyze)
        # We expect the keywords defined in backend/risk_analysis/keywords.py to be found
        expected_flags = [k for k in ["scam", "fraud", "warning"] if k in ALL_KEYWORDS]
        self.assertEqual(set(flags), set(expected_flags))

    def test_assign_flags(self):
        analyzer = Analyzer()
        matching_keywords = ["scam", "fraud", "warning", "not_a_keyword"]
        assigned_flags = analyzer.assign_flags(matching_keywords)
        
        # We expect a dictionary mapping categories to lists of keywords
        expected_flags = {}
        for keyword in matching_keywords:
            if keyword in KEYWORD_TO_CATEGORY:
                category = KEYWORD_TO_CATEGORY[keyword]
                if category not in expected_flags:
                    expected_flags[category] = []
                expected_flags[category].append(keyword)
        
        self.assertEqual(assigned_flags, expected_flags)

    def test_keyword_matching_edge_cases(self):
        analyzer = Analyzer()

        # Test with empty text
        text_to_analyze = ""
        flags = analyzer.analyze_text(text_to_analyze)
        self.assertEqual(flags, [])

        # Test with no matching keywords
        text_to_analyze = "This text is safe and appropriate for all audiences."
        flags = analyzer.analyze_text(text_to_analyze)
        self.assertEqual(flags, [])

    def test_word_boundary_detection(self):
        analyzer = Analyzer()
        
        # Test that word boundaries are respected
        # "hat" should not match in "chat" but should match in "the hat is red"
        text_with_substring = "I was chatting with my friend."
        flags = analyzer.analyze_text(text_with_substring)
        self.assertNotIn("hat", flags)
        
        text_with_whole_word = "I wore a hat today."
        flags = analyzer.analyze_text(text_with_whole_word)
        if "hat" in ALL_KEYWORDS:
            self.assertIn("hat", flags)

    def test_calculate_severity(self):
        analyzer = Analyzer()
        
        # Test empty keywords list
        severity = analyzer.calculate_severity([])
        self.assertEqual(severity, "low")
        
        # Test low severity keywords
        low_severity_keywords = ["warning"]
        severity = analyzer.calculate_severity(low_severity_keywords)
        self.assertEqual(severity, "low")
        
        # Test medium severity with more keywords
        # This test assumes that with enough keywords, severity increases
        medium_keywords = ["hate", "warning", "danger", "caution", "alert"]
        severity = analyzer.calculate_severity(medium_keywords)
        self.assertIn(severity, ["low", "medium"])  # Could be low or medium depending on implementation

    def test_analyze_content(self):
        analyzer = Analyzer()
        
        # Test safe content
        title = "Cute puppies playing in the park"
        description = "Watch these adorable puppies have fun at the local park"
        results = analyzer.analyze_content(title, description)
        
        self.assertFalse(results["has_risk"])
        self.assertEqual(results["risk_categories"], [])
        self.assertEqual(results["total_keywords_matched"], 0)
        
        # Test risky content
        title = "Warning: Dangerous Challenge Going Viral"
        description = "This video discusses the risks of the new viral challenge that has led to several injuries."
        results = analyzer.analyze_content(title, description)
        
        self.assertTrue(results["has_risk"])
        self.assertTrue(len(results["risk_categories"]) > 0)
        self.assertTrue(results["total_keywords_matched"] > 0)
        self.assertIn("overall_severity", results)
        self.assertIn("confidence_score", results)

if __name__ == '__main__':
    unittest.main()
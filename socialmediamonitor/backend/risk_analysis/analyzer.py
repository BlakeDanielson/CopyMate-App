"""
Analysis Engine for content risk assessment.
This module provides functionality to analyze text content for potentially harmful keywords
and patterns, assigning risk categories and severity levels.
"""
import re
from typing import List, Dict, Set, Tuple, Optional, Union
import logging

from .keywords import (
    ALL_KEYWORDS,
    KEYWORD_TO_CATEGORY,
    get_keyword_severity,
    calculate_risk_score
)

# Configure logging
logger = logging.getLogger(__name__)

class Analyzer:
    """
    Analyzes text for the presence of keywords and assigns risk flags.
    Implements pattern matching logic to identify potentially harmful content.
    """
    
    def analyze_text(self, text: str) -> List[str]:
        """
        Checks if any of the internal keywords are present in the text.
        Uses word boundary detection to reduce false positives.
        
        Args:
            text: The text content to analyze
            
        Returns:
            List of matching keywords found in the text
        
        Raises:
            TypeError: If input text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")
        if not text:
            return []  # Return empty list for empty string

        found_keywords = []
        text_lower = text.lower()
        
        # First pass: simple substring matching for multi-word phrases
        for keyword in ALL_KEYWORDS:
            if len(keyword.split()) > 1:  # Multi-word phrase
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
        
        # Second pass: word boundary matching for single words to reduce false positives
        # For example, "hat" shouldn't match in "chat" but should match in "the hat is red"
        words = re.findall(r'\b\w+\b', text_lower)
        for keyword in ALL_KEYWORDS:
            if len(keyword.split()) == 1:  # Single word
                if keyword.lower() in words:
                    found_keywords.append(keyword)
        
        return found_keywords

    def assign_flags(self, matching_keywords: List[str]) -> Dict[str, List[str]]:
        """
        Assigns flags/categories based on matching keywords and the internal mapping.
        Groups keywords by their risk category.
        
        Args:
            matching_keywords: List of keywords found in the analyzed text
            
        Returns:
            Dictionary mapping risk categories to lists of matching keywords
        """
        assigned_flags = {}
        
        for keyword in matching_keywords:
            if keyword in KEYWORD_TO_CATEGORY:
                category = KEYWORD_TO_CATEGORY[keyword]
                if category not in assigned_flags:
                    assigned_flags[category] = []
                assigned_flags[category].append(keyword)
        
        return assigned_flags
    
    def calculate_severity(self, matching_keywords: List[str]) -> str:
        """
        Calculate the severity level based on matched keywords.
        
        Args:
            matching_keywords: List of keywords found in the analyzed text
            
        Returns:
            Severity level as string ('high', 'medium', or 'low')
        """
        if not matching_keywords:
            return "low"
            
        # Calculate risk score based on keyword severity
        risk_score = calculate_risk_score(matching_keywords)
        
        # Determine severity based on risk score
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def analyze_content(self, title: str, description: str) -> Dict[str, Dict]:
        """
        Comprehensive analysis of content (title and description).
        
        Args:
            title: Content title
            description: Content description
            
        Returns:
            Dictionary with analysis results including risk categories,
            matched keywords, severity, and confidence scores
        """
        # Combine title and description, giving more weight to title
        combined_text = f"{title} {title} {description}"
        
        # Find matching keywords
        matching_keywords = self.analyze_text(combined_text)
        
        # Group keywords by risk category
        categorized_keywords = self.assign_flags(matching_keywords)
        
        # Calculate overall severity
        overall_severity = self.calculate_severity(matching_keywords)
        
        # Calculate confidence score
        confidence_score = calculate_risk_score(matching_keywords)
        
        # Prepare results
        results = {
            "has_risk": len(matching_keywords) > 0,
            "risk_categories": list(categorized_keywords.keys()),
            "categorized_keywords": categorized_keywords,
            "overall_severity": overall_severity,
            "confidence_score": confidence_score,
            "total_keywords_matched": len(matching_keywords)
        }
        
        return results

if __name__ == '__main__':
    # Example usage
    analyzer = Analyzer()
    title = "Warning: Dangerous Challenge Going Viral"
    description = "This video discusses the risks of the new viral challenge that has led to several injuries."
    results = analyzer.analyze_content(title, description)
    print(f"Analysis results: {results}")
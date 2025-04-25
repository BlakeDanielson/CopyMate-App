"""Local dummy provider for AI image processing."""
import logging
import random
import time
from typing import Dict, Any, List

from backend.services.ai_processing.base import AIProviderBase
from backend.services.ai_processing.exceptions import ImageProcessingError

# Configure logger
logger = logging.getLogger(__name__)


class LocalDummyProvider(AIProviderBase):
    """
    A dummy AI provider implementation for local development and testing.
    
    This provider doesn't perform any actual AI processing but simulates it by:
    1. Adding a configurable delay to simulate processing time
    2. Returning randomized mock results
    
    It's useful for:
    - Local development without external AI service dependencies
    - Testing the AI processing flow without incurring costs
    - CI/CD pipelines where real AI processing isn't needed
    """
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0, failure_rate: float = 0.0):
        """
        Initialize the local dummy provider.
        
        Args:
            min_delay: Minimum processing delay in seconds
            max_delay: Maximum processing delay in seconds
            failure_rate: Probability of simulated failure (0.0 to 1.0)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.failure_rate = max(0.0, min(1.0, failure_rate))  # Clamp between 0 and 1
        
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image and return dummy results.
        
        Args:
            image_path: Path to the image file to process
            
        Returns:
            A dictionary containing the dummy processing results
            
        Raises:
            ImageProcessingError: If there's a simulated error processing the image
        """
        logger.info(f"LocalDummyProvider processing image at {image_path}")
        
        # Simulate processing delay
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
        
        # Randomly simulate failure based on failure_rate
        if random.random() < self.failure_rate:
            logger.info("LocalDummyProvider simulating a processing failure")
            raise ImageProcessingError(
                "Simulated processing failure", 
                provider_name=self.get_provider_name(),
                image_path=image_path
            )
        
        # Generate dummy results
        results = self._generate_dummy_results(image_path)
        logger.info(f"LocalDummyProvider finished processing in {delay:.2f}s")
        
        return results
    
    def get_provider_name(self) -> str:
        """
        Get the name of this AI provider.
        
        Returns:
            The provider's name as a string
        """
        return "local_dummy"
    
    def _generate_dummy_results(self, image_path: str) -> Dict[str, Any]:
        """
        Generate mock AI processing results.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with mock AI results
        """
        # Mock object detection
        objects = self._generate_random_objects()
        
        # Mock image tagging
        tags = self._generate_random_tags()
        
        # Mock text detection
        text = self._maybe_generate_text()
        
        # Mock sentiment analysis
        sentiment = random.choice(["positive", "neutral", "negative"])
        sentiment_score = random.uniform(0.0, 1.0)
        
        # Create the results dictionary
        results = {
            "provider": self.get_provider_name(),
            "processing_time_seconds": random.uniform(0.5, 2.5),
            "image_path": image_path,
            "objects_detected": objects,
            "tags": tags,
            "sentiment": {
                "label": sentiment,
                "score": sentiment_score
            },
            "moderation": {
                "safe": random.random() > 0.05,
                "categories": {
                    "violence": random.uniform(0.0, 0.1),
                    "adult": random.uniform(0.0, 0.1),
                    "sensitive": random.uniform(0.0, 0.1)
                }
            }
        }
        
        # Conditionally add text if it was generated
        if text:
            results["text_detected"] = text
            
        return results
    
    def _generate_random_objects(self) -> List[Dict[str, Any]]:
        """Generate a list of random detected objects."""
        possible_objects = [
            "person", "cat", "dog", "car", "bicycle", "house", "tree", 
            "book", "cup", "chair", "table", "phone", "flower"
        ]
        
        # Randomly select 0-5 objects
        objects_count = random.randint(0, 5)
        objects = []
        
        for _ in range(objects_count):
            obj = {
                "class": random.choice(possible_objects),
                "confidence": random.uniform(0.7, 0.99),
                "bounding_box": {
                    "x": random.uniform(0.0, 0.8),
                    "y": random.uniform(0.0, 0.8),
                    "width": random.uniform(0.1, 0.5),
                    "height": random.uniform(0.1, 0.5)
                }
            }
            objects.append(obj)
            
        return objects
    
    def _generate_random_tags(self) -> List[Dict[str, Any]]:
        """Generate a list of random image tags."""
        possible_tags = [
            "indoor", "outdoor", "nature", "urban", "portrait", "landscape",
            "daylight", "night", "colorful", "monochrome", "animal", "building",
            "water", "sky", "food", "technology", "artistic", "vintage"
        ]
        
        # Randomly select 3-7 tags
        tag_count = random.randint(3, 7)
        selected_tags = random.sample(possible_tags, min(tag_count, len(possible_tags)))
        
        # Create tag objects with confidence scores
        tags = []
        for tag in selected_tags:
            tags.append({
                "name": tag,
                "confidence": random.uniform(0.7, 0.99)
            })
            
        return tags
    
    def _maybe_generate_text(self) -> List[Dict[str, Any]]:
        """Randomly decide whether to generate text detection results."""
        # 30% chance of having text in the image
        if random.random() > 0.7:
            text_samples = [
                "Hello World", 
                "SALE 50% OFF", 
                "OPEN", 
                "STOP", 
                "EXIT",
                "Welcome",
                "123 Main St."
            ]
            
            text_count = random.randint(1, 3)
            texts = []
            
            for _ in range(text_count):
                text = {
                    "text": random.choice(text_samples),
                    "confidence": random.uniform(0.7, 0.99),
                    "position": {
                        "x": random.uniform(0.0, 0.8),
                        "y": random.uniform(0.0, 0.8),
                        "width": random.uniform(0.1, 0.5),
                        "height": random.uniform(0.05, 0.2)
                    }
                }
                texts.append(text)
                
            return texts
            
        return []
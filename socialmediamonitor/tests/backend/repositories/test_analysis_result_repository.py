import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session

from backend.repositories.analysis_result import AnalysisResultRepository
from backend.models.content import AnalysisResult, SubscribedChannel
from backend.models.user import LinkedAccount
from backend.models.base import RiskCategory


class TestAnalysisResultRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = AnalysisResultRepository()
        
        # Create mock analysis result
        self.mock_result = MagicMock(spec=AnalysisResult)
        self.mock_result.id = 1
        self.mock_result.channel_id = 101
        self.mock_result.video_id = 201
        self.mock_result.risk_category = RiskCategory.HATE_SPEECH
        self.mock_result.severity = "high"
        self.mock_result.flagged_text = "Test flagged text"
        self.mock_result.keywords_matched = ["test", "keywords"]
        self.mock_result.confidence_score = 0.85
        self.mock_result.marked_not_harmful = False
        self.mock_result.marked_not_harmful_at = None
        self.mock_result.marked_not_harmful_by = None
        self.mock_result.created_at = datetime.now()
    
    def test_get_results_by_channel(self):
        """Test getting analysis results for a specific channel"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        order_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_channel(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    def test_get_results_by_channel_include_marked_not_harmful(self):
        """Test getting analysis results for a channel including marked as not harmful"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        order_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_channel(self.db, 101, marked_not_harmful=True)
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        # Should not have additional filter for marked_not_harmful
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    def test_get_results_by_video(self):
        """Test getting analysis results for a specific video"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        order_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_video(self.db, 201)
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    def test_get_results_by_video_include_marked_not_harmful(self):
        """Test getting analysis results for a video including marked as not harmful"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        order_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_video(self.db, 201, marked_not_harmful=True)
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        # Should not have additional filter for marked_not_harmful
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    def test_get_results_by_category(self):
        """Test getting analysis results for a specific risk category"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_not_harmful_mock = filter_mock.filter.return_value
        order_mock = filter_not_harmful_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_category(
            self.db, RiskCategory.HATE_SPEECH, skip=0, limit=100
        )
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        filter_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    def test_get_results_by_category_include_marked_not_harmful(self):
        """Test getting results by category including marked as not harmful"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_result]
        
        # Act
        result = self.repo.get_results_by_category(
            self.db, RiskCategory.HATE_SPEECH, marked_not_harmful=True
        )
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.filter.assert_called_once()
        # Should not have additional filter for marked_not_harmful
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_result)
    
    @patch.object(AnalysisResultRepository, 'get')
    @patch.object(AnalysisResultRepository, 'update')
    def test_mark_as_not_harmful_existing(self, mock_update, mock_get):
        """Test marking an existing analysis result as not harmful"""
        # Arrange
        mock_get.return_value = self.mock_result
        mock_update.return_value = self.mock_result
        
        # Act
        result = self.repo.mark_as_not_harmful(self.db, 1, 301)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        mock_update.assert_called_once()
        # Check that update was called with correct parameters
        update_data = mock_update.call_args[1]['obj_in']
        self.assertTrue(update_data['marked_not_harmful'])
        self.assertIsNotNone(update_data['marked_not_harmful_at'])
        self.assertEqual(update_data['marked_not_harmful_by'], 301)
        self.assertEqual(result, self.mock_result)
    
    @patch.object(AnalysisResultRepository, 'get')
    @patch.object(AnalysisResultRepository, 'update')
    def test_mark_as_not_harmful_nonexistent(self, mock_update, mock_get):
        """Test marking a nonexistent analysis result as not harmful"""
        # Arrange
        mock_get.return_value = None
        
        # Act
        result = self.repo.mark_as_not_harmful(self.db, 999, 301)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        mock_update.assert_not_called()
        self.assertIsNone(result)
    
    def test_get_new_results_count(self):
        """Test getting count of new analysis results since a specific time"""
        # Arrange
        query_mock = self.db.query.return_value
        join1_mock = query_mock.join.return_value
        join2_mock = join1_mock.join.return_value
        filter_mock = join2_mock.filter.return_value
        filter_mock.count.return_value = 5
        since_date = datetime.now()
        
        # Act
        result = self.repo.get_new_results_count(self.db, 401, since_date)
        
        # Assert
        self.db.query.assert_called_once_with(AnalysisResult)
        query_mock.join.assert_called_once()
        join1_mock.join.assert_called_once()
        join2_mock.filter.assert_called_once()
        self.assertEqual(result, 5)
    
    def test_bulk_create_success(self):
        """Test bulk creation of analysis results - successful case"""
        # Arrange
        results_data = [
            {"channel_id": 101, "risk_category": RiskCategory.HATE_SPEECH},
            {"channel_id": 102, "risk_category": RiskCategory.EXPLICIT_CONTENT}
        ]
        
        # Act
        results = self.repo.bulk_create(self.db, results_data)
        
        # Assert
        self.assertEqual(len(results), 2)
        self.db.add.call_count = 2
        self.db.commit.assert_called_once()
        self.db.refresh.call_count = 2
    
    def test_bulk_create_exception(self):
        """Test bulk creation of analysis results with an exception"""
        # Arrange
        results_data = [
            {"channel_id": 101, "risk_category": RiskCategory.HATE_SPEECH},
            {"channel_id": 102, "risk_category": RiskCategory.EXPLICIT_CONTENT}
        ]
        self.db.add.side_effect = Exception("Database error")
        
        # Act/Assert
        with self.assertRaises(Exception):
            self.repo.bulk_create(self.db, results_data)
        
        self.db.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
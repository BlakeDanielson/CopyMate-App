import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from backend.repositories.child_profile import ChildProfileRepository
from backend.models.user import ChildProfile
from backend.models.content import Alert


class TestChildProfileRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = ChildProfileRepository()
        
        # Create mock child profile
        self.mock_profile = MagicMock(spec=ChildProfile)
        self.mock_profile.id = 1
        self.mock_profile.parent_id = 101
        self.mock_profile.name = "Test Child"
        self.mock_profile.age = 10
        self.mock_profile.avatar_url = "https://example.com/avatar.jpg"
        self.mock_profile.is_active = True
        
        # Create another mock child profile for the same parent
        self.mock_profile2 = MagicMock(spec=ChildProfile)
        self.mock_profile2.id = 2
        self.mock_profile2.parent_id = 101
        self.mock_profile2.name = "Test Child 2"
        self.mock_profile2.age = 12
        self.mock_profile2.is_active = True
        
        # Create a mock inactive child profile
        self.mock_inactive_profile = MagicMock(spec=ChildProfile)
        self.mock_inactive_profile.id = 3
        self.mock_inactive_profile.parent_id = 101
        self.mock_inactive_profile.name = "Inactive Child"
        self.mock_inactive_profile.is_active = False
    
    def test_get_profiles_by_parent_active_only(self):
        """Test getting active child profiles for a parent"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_active_mock = filter_mock.filter.return_value
        limit_mock = filter_active_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_profile, self.mock_profile2]
        
        # Act
        result = self.repo.get_profiles_by_parent(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(ChildProfile)
        query_mock.filter.assert_called_once()
        filter_mock.filter.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_profile, result)
        self.assertIn(self.mock_profile2, result)
    
    def test_get_profiles_by_parent_include_inactive(self):
        """Test getting all child profiles for a parent including inactive"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        limit_mock = filter_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [
            self.mock_profile, self.mock_profile2, self.mock_inactive_profile
        ]
        
        # Act
        result = self.repo.get_profiles_by_parent(self.db, 101, active_only=False)
        
        # Assert
        self.db.query.assert_called_once_with(ChildProfile)
        query_mock.filter.assert_called_once()
        # Should not filter by is_active
        self.assertEqual(len(result), 3)
        self.assertIn(self.mock_profile, result)
        self.assertIn(self.mock_profile2, result)
        self.assertIn(self.mock_inactive_profile, result)
    
    def test_get_profile_with_linked_accounts(self):
        """Test getting a child profile with linked accounts eager loaded"""
        # Arrange
        query_mock = self.db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.first.return_value = self.mock_profile
        
        # Act
        with patch('backend.repositories.child_profile.joinedload') as mock_joinedload:
            result = self.repo.get_profile_with_linked_accounts(self.db, 1)
        
        # Assert
        self.db.query.assert_called_once_with(ChildProfile)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.first.assert_called_once()
        self.assertEqual(result, self.mock_profile)
    
    @patch.object(ChildProfileRepository, 'get')
    @patch.object(ChildProfileRepository, 'update')
    def test_deactivate_profile_existing(self, mock_update, mock_get):
        """Test deactivating an existing child profile"""
        # Arrange
        mock_get.return_value = self.mock_profile
        mock_update.return_value = self.mock_inactive_profile
        
        # Act
        result = self.repo.deactivate_profile(self.db, 1)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        mock_update.assert_called_once_with(
            self.db, db_obj=self.mock_profile, obj_in={"is_active": False}
        )
        self.assertEqual(result, self.mock_inactive_profile)
    
    @patch.object(ChildProfileRepository, 'get')
    @patch.object(ChildProfileRepository, 'update')
    def test_deactivate_profile_nonexistent(self, mock_update, mock_get):
        """Test deactivating a nonexistent child profile"""
        # Arrange
        mock_get.return_value = None
        
        # Act
        result = self.repo.deactivate_profile(self.db, 999)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        mock_update.assert_not_called()
        self.assertIsNone(result)
    
    def test_get_profile_with_alerts_all(self):
        """Test getting a child profile with all alerts eager loaded"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        options_mock = filter_mock.options.return_value
        options_mock.first.return_value = self.mock_profile
        
        # Act
        with patch('backend.repositories.child_profile.joinedload') as mock_joinedload:
            result = self.repo.get_profile_with_alerts(self.db, 1)
        
        # Assert
        self.db.query.assert_called_once_with(ChildProfile)
        query_mock.filter.assert_called_once()
        filter_mock.options.assert_called_once()
        options_mock.first.assert_called_once()
        self.assertEqual(result, self.mock_profile)
    
    def test_get_profile_with_alerts_unread_only(self):
        """Test getting a child profile with only unread alerts eager loaded"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        options_mock = filter_mock.options.return_value
        options_mock.first.return_value = self.mock_profile
        
        # Act
        with patch('backend.repositories.child_profile.joinedload') as mock_joinedload:
            with patch('backend.repositories.child_profile.and_') as mock_and:
                result = self.repo.get_profile_with_alerts(self.db, 1, unread_only=True)
        
        # Assert
        self.db.query.assert_called_once_with(ChildProfile)
        query_mock.filter.assert_called_once()
        filter_mock.options.assert_called_once()
        options_mock.first.assert_called_once()
        self.assertEqual(result, self.mock_profile)


if __name__ == '__main__':
    unittest.main()
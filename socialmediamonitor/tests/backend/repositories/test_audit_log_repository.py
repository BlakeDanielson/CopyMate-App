import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.repositories.audit_log import AuditLogRepository
from backend.models.content import AuditLog
from backend.models.base import AuditActionType


class TestAuditLogRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = AuditLogRepository()
        
        # Create mock audit log
        self.mock_log = MagicMock(spec=AuditLog)
        self.mock_log.id = 1
        self.mock_log.parent_id = 101
        self.mock_log.action = AuditActionType.USER_LOGIN
        self.mock_log.resource_type = "user"
        self.mock_log.resource_id = 101
        self.mock_log.details = {"ip": "192.168.1.1"}
        self.mock_log.ip_address = "192.168.1.1"
        self.mock_log.user_agent = "Mozilla/5.0"
        self.mock_log.created_at = datetime.now()
        
        # Create another mock audit log
        self.mock_log2 = MagicMock(spec=AuditLog)
        self.mock_log2.id = 2
        self.mock_log2.parent_id = 101
        self.mock_log2.action = AuditActionType.PROFILE_CREATE
        self.mock_log2.resource_type = "child_profile"
        self.mock_log2.resource_id = 201
        self.mock_log2.created_at = datetime.now() - timedelta(days=1)
    
    @patch.object(AuditLogRepository, 'create')
    def test_log_action(self, mock_create):
        """Test logging an action"""
        # Arrange
        mock_create.return_value = self.mock_log
        action = AuditActionType.USER_LOGIN
        parent_id = 101
        details = {"ip": "192.168.1.1"}
        
        # Act
        result = self.repo.log_action(
            self.db,
            action=action,
            parent_id=parent_id,
            resource_type="user",
            resource_id=101,
            details=details,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Assert
        mock_create.assert_called_once()
        self.assertEqual(mock_create.call_args[1]['obj_in']['action'], action)
        self.assertEqual(mock_create.call_args[1]['obj_in']['parent_id'], parent_id)
        self.assertEqual(mock_create.call_args[1]['obj_in']['details'], details)
        self.assertEqual(result, self.mock_log)
    
    def test_get_logs_for_parent(self):
        """Test getting audit logs for a specific parent user"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log, self.mock_log2]
        
        # Act
        result = self.repo.get_logs_for_parent(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(AuditLog)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_log, result)
        self.assertIn(self.mock_log2, result)
    
    def test_get_logs_by_action(self):
        """Test getting audit logs for a specific action type"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log]
        
        # Act
        with patch('backend.repositories.audit_log.datetime') as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            result = self.repo.get_logs_by_action(
                self.db, AuditActionType.USER_LOGIN
            )
        
        # Assert
        self.db.query.assert_called_once_with(AuditLog)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_log)
    
    def test_get_logs_for_resource(self):
        """Test getting audit logs for a specific resource"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log2]
        
        # Act
        result = self.repo.get_logs_for_resource(
            self.db, "child_profile", 201
        )
        
        # Assert
        self.db.query.assert_called_once_with(AuditLog)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_log2)
    
    def test_get_error_logs(self):
        """Test getting system error logs"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log]
        
        # Act
        with patch('backend.repositories.audit_log.datetime') as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            result = self.repo.get_error_logs(self.db)
        
        # Assert
        self.db.query.assert_called_once_with(AuditLog)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_log)
    
    def test_list_with_date_filter_standard_filters(self):
        """Test listing logs with standard filters"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log]
        
        # Act
        result = self.repo.list_with_date_filter(
            self.db, parent_id=101, action=AuditActionType.USER_LOGIN
        )
        
        # Assert
        self.db.query.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_log)
    
    def test_list_with_date_filter_date_filters(self):
        """Test listing logs with date range filters"""
        # Arrange
        query_mock = self.db.query.return_value
        filter1_mock = query_mock.filter.return_value
        filter2_mock = filter1_mock.filter.return_value
        order_mock = filter2_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_log]
        
        # Some date for testing
        test_date = datetime(2025, 4, 1)
        
        # Act
        result = self.repo.list_with_date_filter(
            self.db,
            date_filters={
                "created_at__gte": test_date
            }
        )
        
        # Assert
        self.db.query.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_log)
    
    def test_count_by_action_type_no_filters(self):
        """Test counting logs by action type with no filters"""
        # Arrange
        query_mock = self.db.query.return_value
        group_mock = query_mock.group_by.return_value
        group_mock.all.return_value = [
            (AuditActionType.USER_LOGIN, 5),
            (AuditActionType.PROFILE_CREATE, 3)
        ]
        
        # Act
        result = self.repo.count_by_action_type(self.db)
        
        # Assert
        self.db.query.assert_called_once()
        query_mock.group_by.assert_called_once_with(AuditLog.action)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], AuditActionType.USER_LOGIN)
        self.assertEqual(result[0][1], 5)
        self.assertEqual(result[1][0], AuditActionType.PROFILE_CREATE)
        self.assertEqual(result[1][1], 3)
    
    def test_count_by_action_type_with_filters(self):
        """Test counting logs by action type with filters"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        group_mock = filter_mock.group_by.return_value
        group_mock.all.return_value = [
            (AuditActionType.USER_LOGIN, 5)
        ]
        
        # Act
        test_date = datetime(2025, 4, 1)
        result = self.repo.count_by_action_type(
            self.db, parent_id=101, start_date=test_date
        )
        
        # Assert
        self.db.query.assert_called_once()
        query_mock.filter.assert_called_once()
        filter_mock.group_by.assert_called_once_with(AuditLog.action)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], AuditActionType.USER_LOGIN)
        self.assertEqual(result[0][1], 5)
    
    def test_count_by_resource_type(self):
        """Test counting logs by resource type"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter2_mock = filter_mock.filter.return_value
        group_mock = filter2_mock.group_by.return_value
        group_mock.all.return_value = [
            ("child_profile", 3),
            ("linked_account", 2)
        ]
        
        # Act
        result = self.repo.count_by_resource_type(self.db)
        
        # Assert
        self.db.query.assert_called_once()
        filter2_mock.group_by.assert_called_once_with(AuditLog.resource_type)
        self.assertEqual(len(result), 2)
        self.assertEqual(result["child_profile"], 3)
        self.assertEqual(result["linked_account"], 2)
    
    def test_count_by_day(self):
        """Test counting logs by day"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        group_mock = filter_mock.group_by.return_value
        
        # Create mock date objects that will be returned by the database query
        date1 = MagicMock()
        date1.strftime.return_value = "2025-04-01"
        date2 = MagicMock()
        date2.strftime.return_value = "2025-04-02"
        
        group_mock.all.return_value = [
            (date1, 10),
            (date2, 5)
        ]
        
        # Act
        result = self.repo.count_by_day(
            self.db, parent_id=101
        )
        
        # Assert
        self.db.query.assert_called_once()
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result["2025-04-01"], 10)
        self.assertEqual(result["2025-04-02"], 5)
    
    def test_count_by_day_with_date_range(self):
        """Test counting logs by day with date range filters"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        group_mock = filter_mock.group_by.return_value
        
        # Create mock date objects that will be returned by the database query
        date1 = MagicMock()
        date1.strftime.return_value = "2025-04-01"
        
        group_mock.all.return_value = [
            (date1, 10)
        ]
        
        # Act
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 5)
        result = self.repo.count_by_day(
            self.db, 
            parent_id=101,
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        self.db.query.assert_called_once()
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result["2025-04-01"], 10)


if __name__ == '__main__':
    unittest.main()
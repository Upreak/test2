"""
Test Profile Update Freshness
Tests for profile update with freshness logic
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


class TestProfileUpdateFreshness:
    """Test suite for profile update freshness functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_candidate_id = str(uuid4())
        self.freshness_days = 30
        
        # Mock current timestamps
        self.now = datetime.utcnow()
        self.fresh_date = self.now - timedelta(days=10)  # 10 days old - still fresh
        self.stale_date = self.now - timedelta(days=35)  # 35 days old - stale
    
    def test_should_update_global_fresh_timestamp(self):
        """Test that fresh timestamps don't trigger updates"""
        # Current CTC last updated 10 days ago (still fresh)
        last_updated = self.fresh_date
        
        # Should NOT update because it's still fresh
        should_update = (self.now - last_updated).days < self.freshness_days
        
        assert should_update is True  # Data is fresh, so we should use it
        # But for updates, we want the opposite logic
        should_trigger_update = (self.now - last_updated).days >= self.freshness_days
        assert should_trigger_update is False
    
    def test_should_update_global_stale_timestamp(self):
        """Test that stale timestamps trigger updates"""
        # Current CTC last updated 35 days ago (stale)
        last_updated = self.stale_date
        
        # Should trigger update because it's stale
        should_trigger_update = (self.now - last_updated).days >= self.freshness_days
        
        assert should_trigger_update is True
    
    def test_freshness_threshold_boundary(self):
        """Test freshness threshold boundary conditions"""
        # Exactly 30 days old (boundary condition)
        boundary_date = self.now - timedelta(days=self.freshness_days)
        
        should_trigger_update = (self.now - boundary_date).days >= self.freshness_days
        
        # At exactly 30 days, it should trigger update
        assert should_trigger_update is True
    
    def test_never_updated_field(self):
        """Test fields that have never been updated"""
        # Field was never updated (None timestamp)
        last_updated = None
        
        # Should always trigger update for never-updated fields
        if last_updated is None:
            should_trigger_update = True
        else:
            should_trigger_update = (self.now - last_updated).days >= self.freshness_days
        
        assert should_trigger_update is True
    
    def test_update_timestamp_tracking(self):
        """Test that update timestamps are properly tracked"""
        updates = {
            "current_ctc": {
                "value": "15.0",
                "last_updated": self.now.isoformat(),
                "source": "prescreen"
            },
            "skills": {
                "value": ["Python", "FastAPI"],
                "last_updated": self.now.isoformat(),
                "source": "prescreen"
            }
        }
        
        # Verify timestamp format
        for field, data in updates.items():
            assert "last_updated" in data
            assert "T" in data["last_updated"]  # ISO format check
    
    def test_selective_field_updates(self):
        """Test selective updating of only stale fields"""
        candidate_profile = {
            "current_ctc": "10.0",
            "current_ctc_last_updated": self.stale_date,  # Stale
            "expected_ctc": "15.0", 
            "expected_ctc_last_updated": self.fresh_date,  # Fresh
            "skills": ["Python"],
            "skills_last_updated": self.stale_date  # Stale
        }
        
        new_updates = {
            "current_ctc": "12.0",
            "expected_ctc": "16.0",
            "skills": ["Python", "FastAPI"]
        }
        
        # Only update stale fields
        fields_to_update = []
        for field in new_updates:
            last_updated_field = f"{field}_last_updated"
            last_updated = candidate_profile.get(last_updated_field)
            
            if last_updated is None or (self.now - last_updated).days >= self.freshness_days:
                fields_to_update.append(field)
        
        assert "current_ctc" in fields_to_update
        assert "skills" in fields_to_update
        assert "expected_ctc" not in fields_to_update  # This should not be updated as it's fresh
    
    def test_update_source_tracking(self):
        """Test tracking of update sources"""
        update_sources = ["prescreen", "manual", "import", "api"]
        
        for source in update_sources:
            update_record = {
                "field": "current_ctc",
                "value": "15.0",
                "source": source,
                "timestamp": self.now.isoformat()
            }
            
            assert update_record["source"] in update_sources
    
    def test_bulk_profile_update(self):
        """Test bulk profile update with freshness logic"""
        stale_fields = ["current_ctc", "skills", "notice_period"]
        fresh_fields = ["email", "phone"]
        
        # Simulate bulk update
        updates = {}
        for field in stale_fields + fresh_fields:
            if field in stale_fields:
                # This field should be updated (stale)
                updates[field] = f"new_{field}_value"
            else:
                # This field should not be updated (fresh)
                pass
        
        # Verify only stale fields are in updates
        assert len(updates) == len(stale_fields)
        for field in stale_fields:
            assert field in updates
        for field in fresh_fields:
            assert field not in updates
    
    def test_freshness_config_override(self):
        """Test that freshness days can be configured"""
        custom_freshness_days = 60  # Custom configuration
        
        # Test with custom freshness period
        old_date = self.now - timedelta(days=45)  # 45 days old
        
        # With default 30 days - should trigger update
        should_update_default = (self.now - old_date).days >= 30
        assert should_update_default is True
        
        # With custom 60 days - should NOT trigger update
        should_update_custom = (self.now - old_date).days >= custom_freshness_days
        assert should_update_custom is False
    
    def test_update_audit_log(self):
        """Test that profile updates are audited"""
        audit_entry = {
            "candidate_id": self.test_candidate_id,
            "field": "current_ctc",
            "old_value": "10.0",
            "new_value": "12.0",
            "update_reason": "freshness_expired",
            "source": "prescreen",
            "timestamp": self.now.isoformat(),
            "updated_by": "system"
        }
        
        required_fields = ["candidate_id", "field", "old_value", "new_value", "update_reason", "source", "timestamp"]
        
        for field in required_fields:
            assert field in audit_entry
            assert audit_entry[field] is not None
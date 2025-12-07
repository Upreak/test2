"""
Chatbot Profile Update Service
Handle freshness logic and global profile updates
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from backend_app.chatbot.config import settings


class ProfileUpdateService:
    """Service for handling profile updates with freshness logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.freshness_days = settings.FRESHNESS_DAYS
    
    def should_update_global(
        self,
        field: str,
        candidate_profile: Dict[str, Any],
        freshness_days: Optional[int] = None
    ) -> bool:
        """
        Check if a field should be updated in global profile based on freshness
        
        Args:
            field: Field name to check
            candidate_profile: Current candidate profile
            freshness_days: Custom freshness threshold (uses default if None)
            
        Returns:
            True if should update, False otherwise
        """
        threshold_days = freshness_days or self.freshness_days
        
        # Get last updated timestamp for the field
        last_updated_field = f"{field}_last_updated"
        last_updated = candidate_profile.get(last_updated_field)
        
        if not last_updated:
            self.logger.debug(f"No last_updated found for {field}, allowing update")
            return True
        
        # Parse timestamp
        try:
            if isinstance(last_updated, str):
                last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                last_updated_dt = last_updated
            
            # Check if older than threshold
            time_diff = datetime.utcnow() - last_updated_dt.replace(tzinfo=None)
            should_update = time_diff.days > threshold_days
            
            self.logger.debug(
                f"Field {field}: last_updated={last_updated_dt}, "
                f"diff={time_diff.days} days, should_update={should_update}"
            )
            
            return should_update
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Error parsing last_updated for {field}: {e}")
            return True  # Default to update on error
    
    async def update_global_profile(
        self,
        candidate_id: str,
        updates: Dict[str, Any],
        source: str = "chatbot"
    ) -> Dict[str, Any]:
        """
        Update global candidate profile with new data
        
        Args:
            candidate_id: Candidate identifier
            updates: Dictionary of field updates
            source: Source of the update
            
        Returns:
            Update result
        """
        try:
            self.logger.info(f"Updating global profile for candidate {candidate_id}")
            
            # Prepare updates with timestamps
            timestamped_updates = {}
            current_time = datetime.utcnow()
            
            for field, value in updates.items():
                # Update the field value
                timestamped_updates[field] = value
                
                # Update the timestamp
                timestamp_field = f"{field}_last_updated"
                timestamped_updates[timestamp_field] = current_time
            
            # This would update the candidate profile in the database
            # For now, return success as placeholder
            result = {
                "candidate_id": candidate_id,
                "fields_updated": list(updates.keys()),
                "source": source,
                "updated_at": current_time.isoformat(),
                "success": True
            }
            
            self.logger.info(f"Successfully updated global profile for {candidate_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update global profile for {candidate_id}: {e}")
            return {
                "candidate_id": candidate_id,
                "error": str(e),
                "success": False
            }
    
    def get_freshness_status(
        self,
        candidate_profile: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get freshness status for specified fields
        
        Args:
            candidate_profile: Candidate profile data
            fields: List of fields to check (checks all if None)
            
        Returns:
            Dictionary of field freshness status
        """
        if fields is None:
            # Default fields to check
            fields = [
                "current_ctc", "expected_ctc", "notice_period",
                "current_location", "skills", "preferred_location",
                "total_experience"
            ]
        
        freshness_status = {}
        current_time = datetime.utcnow()
        
        for field in fields:
            last_updated_field = f"{field}_last_updated"
            last_updated = candidate_profile.get(last_updated_field)
            
            if not last_updated:
                status = {
                    "field": field,
                    "is_fresh": False,
                    "last_updated": None,
                    "days_old": None,
                    "should_update": True
                }
            else:
                try:
                    if isinstance(last_updated, str):
                        last_updated_dt = datetime.fromisoformat(
                            last_updated.replace('Z', '+00:00')
                        )
                    else:
                        last_updated_dt = last_updated
                    
                    days_old = (current_time - last_updated_dt.replace(tzinfo=None)).days
                    is_fresh = days_old <= self.freshness_days
                    should_update = not is_fresh
                    
                    status = {
                        "field": field,
                        "is_fresh": is_fresh,
                        "last_updated": last_updated,
                        "days_old": days_old,
                        "should_update": should_update
                    }
                except (ValueError, TypeError):
                    status = {
                        "field": field,
                        "is_fresh": False,
                        "last_updated": last_updated,
                        "days_old": None,
                        "should_update": True
                    }
            
            freshness_status[field] = status
        
        return freshness_status
    
    async def batch_update_profile(
        self,
        candidate_id: str,
        updates: Dict[str, Any],
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Batch update profile fields with freshness checking
        
        Args:
            candidate_id: Candidate identifier
            updates: Dictionary of field updates
            force_update: Whether to force update regardless of freshness
            
        Returns:
            Batch update result
        """
        try:
            self.logger.info(f"Batch updating profile for candidate {candidate_id}")
            
            # Get current profile (this would fetch from database)
            # For now, use empty profile
            current_profile = {}
            
            fields_to_update = {}
            
            for field, value in updates.items():
                if force_update or self.should_update_global(field, current_profile):
                    fields_to_update[field] = value
                else:
                    self.logger.debug(f"Skipping update for {field} - still fresh")
            
            if not fields_to_update:
                return {
                    "candidate_id": candidate_id,
                    "fields_updated": [],
                    "message": "No fields needed updating",
                    "success": True
                }
            
            # Update the profile
            update_result = await self.update_global_profile(
                candidate_id, fields_to_update, source="chatbot_batch"
            )
            
            return {
                "candidate_id": candidate_id,
                "fields_updated": list(fields_to_update.keys()),
                "update_result": update_result,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to batch update profile for {candidate_id}: {e}")
            return {
                "candidate_id": candidate_id,
                "error": str(e),
                "success": False
            }
    
    def get_freshness_threshold(self) -> int:
        """Get current freshness threshold in days"""
        return self.freshness_days
    
    def set_freshness_threshold(self, days: int) -> None:
        """
        Set freshness threshold
        
        Args:
            days: Number of days for freshness threshold
        """
        if days > 0:
            self.freshness_days = days
            self.logger.info(f"Set freshness threshold to {days} days")
        else:
            raise ValueError("Freshness threshold must be positive")


# Global profile update service instance
profile_update_service = ProfileUpdateService()
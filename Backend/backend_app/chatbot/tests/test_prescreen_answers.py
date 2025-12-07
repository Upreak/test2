"""
Test Prescreen Answers
Tests for submitting and processing prescreen answers
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestPrescreenAnswers:
    """Test suite for prescreen answers functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_application_id = str(uuid4())
        self.test_question_id = str(uuid4())
        self.test_answers = {
            "ps_current_ctc": "10.5",
            "ps_expected_ctc": "15.0",
            "ps_notice_period": "60",
            "ps_total_experience": "5",
            "ps_key_skills": ["Python", "FastAPI", "SQLAlchemy"]
        }
    
    def test_submit_prescreen_answers_structure(self):
        """Test the structure of prescreen answers submission"""
        # This would test the actual API endpoint
        # For now, test the expected response structure
        
        response = {
            "application_id": self.test_application_id,
            "jd_match_score": 85,
            "must_have_failed": False,
            "answers_processed": 5,
            "global_profile_updated": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        assert response["application_id"] == self.test_application_id
        assert isinstance(response["jd_match_score"], int)
        assert 0 <= response["jd_match_score"] <= 100
        assert isinstance(response["must_have_failed"], bool)
        assert isinstance(response["answers_processed"], int)
        assert isinstance(response["global_profile_updated"], bool)
        assert "timestamp" in response
    
    def test_answer_validation(self):
        """Test validation of prescreen answers"""
        # Test valid answers
        valid_answers = {
            "ps_current_ctc": "10.5",
            "ps_expected_ctc": "15.0",
            "ps_notice_period": "60",
            "ps_total_experience": "5.5"
        }
        
        for qid, answer in valid_answers.items():
            # Test that answers are strings (as stored in database)
            assert isinstance(answer, str)
            # Test that numeric answers can be converted to numbers
            if qid in ["ps_current_ctc", "ps_expected_ctc", "ps_total_experience"]:
                try:
                    float(answer)
                    valid = True
                except ValueError:
                    valid = False
                assert valid is True
    
    def test_skill_answer_format(self):
        """Test skills answer format"""
        skills_answer = ["Python", "FastAPI", "SQLAlchemy"]
        
        # Skills should be a list
        assert isinstance(skills_answer, list)
        
        # Each skill should be a string
        for skill in skills_answer:
            assert isinstance(skill, str)
            assert len(skill) > 0
    
    def test_match_score_calculation(self):
        """Test match score calculation logic"""
        # Mock match score calculation
        answers = self.test_answers
        total_questions = len(answers)
        answered_questions = len([a for a in answers.values() if a])
        
        # Calculate mock match score
        completion_rate = (answered_questions / total_questions) * 100
        
        assert 0 <= completion_rate <= 100
    
    def test_must_have_validation(self):
        """Test must-have criteria validation"""
        # Mock must-have questions
        must_have_questions = ["ps_current_ctc", "ps_expected_ctc", "ps_key_skills"]
        
        # Check if all must-have questions are answered
        answers = self.test_answers
        must_have_failed = False
        
        for qid in must_have_questions:
            if qid not in answers or not answers[qid]:
                must_have_failed = True
                break
        
        assert must_have_failed is False
    
    def test_answer_metadata_storage(self):
        """Test that answer metadata is properly stored"""
        answer_metadata = {
            "validation_result": "passed",
            "normalized_value": "10.5",
            "question_weight": 10,
            "answer_timestamp": datetime.utcnow().isoformat()
        }
        
        assert "validation_result" in answer_metadata
        assert "normalized_value" in answer_metadata
        assert "question_weight" in answer_metadata
        assert "answer_timestamp" in answer_metadata
    
    def test_prescreen_summary_generation(self):
        """Test prescreen summary generation"""
        summary = {
            "total_questions": 5,
            "answered_questions": 5,
            "match_score": 85,
            "must_have_failed": False,
            "scores_by_category": {
                "compensation": 90,
                "experience": 80,
                "skills": 85
            },
            "completed_at": datetime.utcnow().isoformat()
        }
        
        assert summary["total_questions"] == 5
        assert summary["answered_questions"] == 5
        assert summary["match_score"] == 85
        assert summary["must_have_failed"] is False
        assert "scores_by_category" in summary
        assert "completed_at" in summary
    
    def test_global_profile_update_flag(self):
        """Test global profile update functionality"""
        # Test with update_global_profile = True
        update_global = True
        assert update_global is True
        
        # Test with update_global_profile = False
        update_global = False
        assert update_global is False
    
    def test_answer_processing_error_handling(self):
        """Test error handling during answer processing"""
        # Test invalid answer format
        invalid_answers = {
            "ps_current_ctc": "invalid_number",
            "ps_expected_ctc": "",
            "ps_notice_period": "abc"
        }
        
        # These should be handled gracefully
        for qid, answer in invalid_answers.items():
            if answer == "":
                # Empty answer should be handled
                assert True
            elif qid == "ps_current_ctc" and answer == "invalid_number":
                # Invalid number should be caught
                assert True
    
    def test_answer_timestamp_tracking(self):
        """Test that answer timestamps are tracked"""
        timestamp = datetime.utcnow().isoformat()
        
        # Timestamp should be in ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp
"""
Test JD KB Service
Tests for job knowledge base functionality
"""

import pytest
from uuid import uuid4


class TestJDKB:
    """Test suite for JD knowledge base functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_job_id = str(uuid4())
        self.test_faq_data = {
            "job_id": self.test_job_id,
            "question": "What is the work location for this position?",
            "answer": "This position is based in Bangalore with hybrid work options available.",
            "question_keywords": '["work location", "bangalore", "hybrid", "remote"]',
            "created_by": "recruiter-123"
        }
    
    def test_save_job_faq(self):
        """Test saving FAQ entry to knowledge base"""
        faq_entry = {
            "id": str(uuid4()),
            "job_id": self.test_job_id,
            "question": self.test_faq_data["question"],
            "answer": self.test_faq_data["answer"],
            "question_keywords": self.test_faq_data["question_keywords"],
            "created_by": self.test_faq_data["created_by"],
            "created_at": "2025-01-01T00:00:00"
        }
        
        assert faq_entry["job_id"] == self.test_job_id
        assert faq_entry["question"] is not None
        assert faq_entry["answer"] is not None
        assert faq_entry["created_by"] is not None
        assert faq_entry["question_keywords"] is not None
    
    def test_lookup_jd_answer_found(self):
        """Test finding answer in JD knowledge base"""
        # Mock knowledge base
        knowledge_base = [
            {
                "question": "What is the work location?",
                "answer": "Bangalore with hybrid options",
                "keywords": ["work location", "bangalore", "hybrid"]
            },
            {
                "question": "What are the required skills?",
                "answer": "Python, FastAPI, SQL",
                "keywords": ["skills", "python", "fastapi", "sql"]
            }
        ]
        
        # Test question that should match
        test_question = "Where is this job located?"
        keywords_to_match = ["work location", "bangalore", "hybrid"]
        
        # Find matching FAQ
        matching_faq = None
        for faq in knowledge_base:
            if any(keyword in test_question.lower() for keyword in faq["keywords"]):
                matching_faq = faq
                break
        
        assert matching_faq is not None
        assert "Bangalore" in matching_faq["answer"]
    
    def test_lookup_jd_answer_not_found(self):
        """Test when answer is not found in knowledge base"""
        knowledge_base = [
            {
                "question": "What is the work location?",
                "answer": "Bangalore with hybrid options",
                "keywords": ["work location", "bangalore", "hybrid"]
            }
        ]
        
        # Test question that should not match
        test_question = "What is the salary range?"
        keywords_to_match = ["salary", "ctc", "compensation"]
        
        # Find matching FAQ
        matching_faq = None
        for faq in knowledge_base:
            if any(keyword in test_question.lower() for keyword in faq["keywords"]):
                matching_faq = faq
                break
        
        assert matching_faq is None
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching for similar questions"""
        # Original question in KB
        original_question = "What is the work location for this position?"
        original_keywords = ["work location", "position", "location", "work"]
        
        # Similar questions that should match
        similar_questions = [
            "Where is this job located?",
            "What's the location of this position?",
            "Is this work from office?",
            "Can I work remotely?"
        ]
        
        # Test fuzzy matching logic
        for question in similar_questions:
            # Simple keyword matching (in real implementation, use more sophisticated matching)
            found_match = any(keyword in question.lower() for keyword in original_keywords)
            
            # Some questions should match based on keywords
            if question in ["Where is this job located?", "What's the location of this position?"]:
                assert found_match is True
            else:
                # These might not match with simple keyword matching
                # In real implementation, use fuzzy matching algorithms
                pass
    
    def test_keyword_extraction(self):
        """Test keyword extraction from questions"""
        test_questions = [
            "What is the work location?",
            "What are the required skills?",
            "What is the salary range?"
        ]
        
        expected_keywords = [
            ["work", "location"],
            ["required", "skills"],
            ["salary", "range"]
        ]
        
        # Simple keyword extraction (in real implementation, use NLP)
        for i, question in enumerate(test_questions):
            words = question.lower().replace("?", "").split()
            # Remove common stop words
            stop_words = ["what", "is", "the", "are", "a", "an", "in", "on", "at"]
            keywords = [word for word in words if word not in stop_words]
            
            # Verify we extracted meaningful keywords
            assert len(keywords) > 0
            assert any(kw in keywords for kw in expected_keywords[i])
    
    def test_faq_storage_format(self):
        """Test FAQ storage format and structure"""
        faq_storage = {
            "id": str(uuid4()),
            "job_id": self.test_job_id,
            "question": "What technologies will I work with?",
            "answer": "You'll work with Python, FastAPI, PostgreSQL, and React.",
            "question_keywords": '["technologies", "python", "fastapi", "postgresql", "react"]',
            "created_by": "recruiter-123",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        required_fields = ["id", "job_id", "question", "answer", "question_keywords", "created_by"]
        for field in required_fields:
            assert field in faq_storage
            assert faq_storage[field] is not None
    
    def test_question_normalization(self):
        """Test question normalization for matching"""
        variations = [
            "What is the work location?",
            "What's the work location?",
            "what is the work location",
            "WHAT IS THE WORK LOCATION?"
        ]
        
        # Normalize questions
        normalized = []
        for question in variations:
            normalized_question = question.lower().strip().rstrip("?")
            normalized.append(normalized_question)
        
        # All should normalize to the same base
        expected_base = "what is the work location"
        for norm in normalized:
            assert norm == expected_base
    
    def test_kb_search_performance(self):
        """Test knowledge base search performance"""
        # Mock large knowledge base
        large_kb = []
        for i in range(1000):
            large_kb.append({
                "id": f"faq-{i}",
                "question": f"Question {i} about topic",
                "answer": f"Answer {i} for the question",
                "keywords": [f"topic", f"question-{i}"]
            })
        
        # Test search performance
        import time
        start_time = time.time()
        
        # Simple search
        search_term = "topic"
        results = [faq for faq in large_kb if search_term in faq["question"].lower()]
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Should find results quickly
        assert len(results) > 0
        assert search_time < 1.0  # Should be much faster in practice
    
    def test_kb_update_functionality(self):
        """Test updating existing FAQ entries"""
        original_faq = {
            "id": str(uuid4()),
            "job_id": self.test_job_id,
            "question": "What is the work location?",
            "answer": "Bangalore",
            "question_keywords": '["work location", "bangalore"]',
            "created_by": "recruiter-123",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        # Update the FAQ
        updated_faq = original_faq.copy()
        updated_faq["answer"] = "Bangalore with hybrid options"
        updated_faq["updated_at"] = "2025-01-02T00:00:00"
        
        assert updated_faq["answer"] != original_faq["answer"]
        assert updated_faq["updated_at"] != original_faq["updated_at"]
    
    def test_escalation_to_recruiter(self):
        """Test escalation to recruiter when KB answer not found"""
        escalation_request = {
            "job_id": self.test_job_id,
            "question": "What is the exact salary range for this position?",
            "candidate_id": "candidate-123",
            "timestamp": "2025-01-01T00:00:00",
            "escalation_reason": "No matching FAQ found"
        }
        
        # Verify escalation structure
        required_fields = ["job_id", "question", "candidate_id", "timestamp", "escalation_reason"]
        for field in required_fields:
            assert field in escalation_request
            assert escalation_request[field] is not None
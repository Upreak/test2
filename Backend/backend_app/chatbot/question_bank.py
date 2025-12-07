"""
Chatbot Question Bank
Default QIDs and question templates for prescreening
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class QuestionType(Enum):
    """Question types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    BOOLEAN = "boolean"


class QuestionBank:
    """Question bank for prescreening questions"""
    
    def __init__(self):
        self.questions = self._initialize_default_questions()
    
    def _initialize_default_questions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default prescreening questions"""
        return {
            "ps_current_ctc": {
                "qid": "ps_current_ctc",
                "question_text": "What is your current CTC (Cost to Company) in LPA (Lakhs Per Annum)?",
                "type": QuestionType.NUMBER.value,
                "required": True,
                "must_have": True,
                "weight": 10,
                "validation_rule": "min:0,max:100",
                "choices": None,
                "description": "Current annual compensation including all components"
            },
            
            "ps_expected_ctc": {
                "qid": "ps_expected_ctc",
                "question_text": "What is your expected CTC in LPA (Lakhs Per Annum)?",
                "type": QuestionType.NUMBER.value,
                "required": True,
                "must_have": True,
                "weight": 10,
                "validation_rule": "min:0,max:100",
                "choices": None,
                "description": "Expected annual compensation"
            },
            
            "ps_notice_period": {
                "qid": "ps_notice_period",
                "question_text": "What is your notice period in days?",
                "type": QuestionType.NUMBER.value,
                "required": True,
                "must_have": True,
                "weight": 8,
                "validation_rule": "min:0,max:180",
                "choices": None,
                "description": "Current notice period duration"
            },
            
            "ps_total_experience": {
                "qid": "ps_total_experience",
                "question_text": "What is your total work experience in years?",
                "type": QuestionType.NUMBER.value,
                "required": True,
                "must_have": True,
                "weight": 12,
                "validation_rule": "min:0,max:50",
                "choices": None,
                "description": "Total years of professional experience"
            },
            
            "ps_key_skills": {
                "qid": "ps_key_skills",
                "question_text": "What are your key technical skills? (Select all that apply)",
                "type": QuestionType.MULTI_SELECT.value,
                "required": True,
                "must_have": True,
                "weight": 15,
                "validation_rule": "min:1",
                "choices": [
                    "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue.js",
                    "Node.js", "Spring Boot", "Django", "Flask", "FastAPI", "SQL", "NoSQL",
                    "PostgreSQL", "MySQL", "MongoDB", "Redis", "AWS", "Azure", "GCP",
                    "Docker", "Kubernetes", "Terraform", "Jenkins", "Git", "CI/CD",
                    "Machine Learning", "Deep Learning", "Data Science", "Big Data",
                    "DevOps", "Microservices", "GraphQL", "REST APIs", "Agile", "Scrum"
                ],
                "description": "Primary technical skills and technologies"
            },
            
            "ps_has_offers": {
                "qid": "ps_has_offers",
                "question_text": "Do you currently have any other job offers?",
                "type": QuestionType.BOOLEAN.value,
                "required": False,
                "must_have": False,
                "weight": 5,
                "validation_rule": None,
                "choices": None,
                "description": "Currently holding other job offers"
            },
            
            "ps_preferred_location": {
                "qid": "ps_preferred_location",
                "question_text": "What are your preferred work locations? (Select all that apply)",
                "type": QuestionType.MULTI_SELECT.value,
                "required": True,
                "must_have": True,
                "weight": 8,
                "validation_rule": "min:1",
                "choices": [
                    "Bangalore", "Hyderabad", "Pune", "Chennai", "Delhi/NCR", "Mumbai",
                    "Remote", "Hybrid", "Any Location"
                ],
                "description": "Preferred work locations"
            },
            
            "ps_current_location": {
                "qid": "ps_current_location",
                "question_text": "What is your current location?",
                "type": QuestionType.TEXT.value,
                "required": True,
                "must_have": True,
                "weight": 6,
                "validation_rule": "min_length:2,max_length:100",
                "choices": None,
                "description": "Current city/location"
            },
            
            "ps_availability": {
                "qid": "ps_availability",
                "question_text": "When are you available to join?",
                "type": QuestionType.SELECT.value,
                "required": True,
                "must_have": True,
                "weight": 7,
                "validation_rule": None,
                "choices": [
                    "Immediately", "15 days", "30 days", "45 days", "60 days", "Flexible"
                ],
                "description": "Joining availability"
            },
            
            "ps_best_time_to_contact": {
                "qid": "ps_best_time_to_contact",
                "question_text": "What is the best time to contact you?",
                "type": QuestionType.SELECT.value,
                "required": False,
                "must_have": False,
                "weight": 3,
                "validation_rule": None,
                "choices": [
                    "Morning (9 AM - 12 PM)", "Afternoon (12 PM - 4 PM)", 
                    "Evening (4 PM - 7 PM)", "Flexible"
                ],
                "description": "Preferred contact time"
            },
            
            "ps_work_mode": {
                "qid": "ps_work_mode",
                "question_text": "What work mode do you prefer?",
                "type": QuestionType.SELECT.value,
                "required": True,
                "must_have": True,
                "weight": 6,
                "validation_rule": None,
                "choices": [
                    "Remote", "Hybrid", "Work from Office", "Flexible"
                ],
                "description": "Preferred work arrangement"
            },
            
            "ps_relocate": {
                "qid": "ps_relocate",
                "question_text": "Are you willing to relocate?",
                "type": QuestionType.BOOLEAN.value,
                "required": False,
                "must_have": False,
                "weight": 4,
                "validation_rule": None,
                "choices": None,
                "description": "Willingness to relocate for the job"
            },
            
            "ps_shift_preference": {
                "qid": "ps_shift_preference",
                "question_text": "What shift do you prefer?",
                "type": QuestionType.SELECT.value,
                "required": False,
                "must_have": False,
                "weight": 3,
                "validation_rule": None,
                "choices": [
                    "Day Shift", "Night Shift", "Flexible", "No Preference"
                ],
                "description": "Preferred work shift"
            },
            
            "ps_visa_status": {
                "qid": "ps_visa_status",
                "question_text": "What is your current visa/work authorization status?",
                "type": QuestionType.TEXT.value,
                "required": False,
                "must_have": False,
                "weight": 2,
                "validation_rule": "max_length:200",
                "choices": None,
                "description": "Current visa or work authorization status"
            },
            
            "ps_certifications": {
                "qid": "ps_certifications",
                "question_text": "Do you have any relevant certifications? (Optional)",
                "type": QuestionType.TEXT.value,
                "required": False,
                "must_have": False,
                "weight": 2,
                "validation_rule": "max_length:500",
                "choices": None,
                "description": "Professional certifications"
            }
        }
    
    def get_question(self, qid: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by QID"""
        return self.questions.get(qid)
    
    def get_all_questions(self) -> Dict[str, Dict[str, Any]]:
        """Get all questions"""
        return self.questions
    
    def get_questions_by_type(self, question_type: str) -> List[Dict[str, Any]]:
        """Get questions by type"""
        return [
            q for q in self.questions.values() 
            if q["type"] == question_type
        ]
    
    def get_required_questions(self) -> List[Dict[str, Any]]:
        """Get all required questions"""
        return [
            q for q in self.questions.values() 
            if q["required"]
        ]
    
    def get_must_have_questions(self) -> List[Dict[str, Any]]:
        """Get all must-have questions"""
        return [
            q for q in self.questions.values() 
            if q["must_have"]
        ]
    
    def get_question_ids(self) -> List[str]:
        """Get all question IDs"""
        return list(self.questions.keys())
    
    def add_question(self, question_data: Dict[str, Any]) -> bool:
        """Add a new question"""
        qid = question_data.get("qid")
        if not qid:
            return False
        
        if qid in self.questions:
            return False
        
        self.questions[qid] = question_data
        return True
    
    def update_question(self, qid: str, updates: Dict[str, Any]) -> bool:
        """Update an existing question"""
        if qid not in self.questions:
            return False
        
        self.questions[qid].update(updates)
        return True
    
    def remove_question(self, qid: str) -> bool:
        """Remove a question"""
        if qid in self.questions:
            del self.questions[qid]
            return True
        return False
    
    def get_question_count(self) -> int:
        """Get total number of questions"""
        return len(self.questions)
    
    def get_weighted_questions(self) -> List[Dict[str, Any]]:
        """Get questions sorted by weight (highest first)"""
        return sorted(
            self.questions.values(),
            key=lambda x: x["weight"],
            reverse=True
        )
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> bool:
        """Validate question data structure"""
        required_fields = ["qid", "question_text", "type", "required", "must_have", "weight"]
        
        for field in required_fields:
            if field not in question_data:
                return False
        
        # Validate question type
        valid_types = [t.value for t in QuestionType]
        if question_data["type"] not in valid_types:
            return False
        
        # Validate weight
        if not isinstance(question_data["weight"], (int, float)) or question_data["weight"] < 0:
            return False
        
        return True


# Global question bank instance
question_bank = QuestionBank()
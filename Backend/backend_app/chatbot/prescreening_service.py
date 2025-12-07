"""
Chatbot Prescreening Service
Process prescreen answers and compute match scores
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from backend_app.chatbot.question_bank import question_bank
from backend_app.chatbot.rules_engine import rules_engine, ValidationResult
from backend_app.chatbot.models.session_model import UserRole


class PrescreeningService:
    """Service for handling prescreening operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_prescreen_answers(
        self,
        application_id: str,
        answers: Dict[str, Any],
        update_global_profile: bool = False
    ) -> Dict[str, Any]:
        """
        Process prescreen answers for an application
        
        Args:
            application_id: Application identifier
            answers: Dictionary of QID -> answer mappings
            update_global_profile: Whether to update global candidate profile
            
        Returns:
            Processing result with scores and status
        """
        try:
            self.logger.info(f"Processing prescreen answers for application {application_id}")
            
            # Validate all answers
            validation_results = {}
            for qid, answer in answers.items():
                question = question_bank.get_question(qid)
                if not question:
                    validation_results[qid] = ValidationResult(
                        False, None, f"Unknown question ID: {qid}"
                    )
                    continue
                
                validation_results[qid] = rules_engine.validate_prescreen_answer(
                    qid, answer, question
                )
            
            # Filter valid answers
            valid_answers = {
                qid: result.value
                for qid, result in validation_results.items()
                if result.is_valid and result.value is not None
            }
            
            # Compute match scores
            scores = self._compute_match_scores(valid_answers)
            aggregate_score = rules_engine.compute_aggregate_score(
                list(scores.values())
            )
            
            # Update application
            application_update = await self._update_application_prescreening(
                application_id,
                valid_answers,
                scores,
                aggregate_score
            )
            
            result = {
                "application_id": application_id,
                "answers_processed": len(valid_answers),
                "total_questions": len(answers),
                "valid_answers": valid_answers,
                "scores": scores,
                "jd_match_score": aggregate_score,
                "must_have_failed": self._check_must_have_failed(valid_answers),
                "application_updated": application_update,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update global profile if requested
            if update_global_profile:
                profile_update = await self._update_global_profile(
                    application_id, valid_answers
                )
                result["global_profile_updated"] = profile_update
            
            self.logger.info(f"Successfully processed prescreen answers for {application_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing prescreen answers: {e}")
            raise
    
    def _compute_match_scores(self, answers: Dict[str, Any]) -> Dict[str, int]:
        """
        Compute match scores for each answer
        
        Args:
            answers: Validated answers
            
        Returns:
            Dictionary of QID -> score mappings
        """
        scores = {}
        
        for qid, answer in answers.items():
            question = question_bank.get_question(qid)
            if not question:
                continue
            
            # Get expected value from job requirements or question config
            expected_value = self._get_expected_value(qid, question)
            
            if expected_value is not None:
                score = rules_engine.compute_match_score(
                    expected_value, answer, question["weight"]
                )
            else:
                # Default score for non-comparative questions
                score = int(100 * question["weight"])
            
            scores[qid] = score
        
        return scores
    
    def _get_expected_value(self, qid: str, question: Dict[str, Any]) -> Any:
        """
        Get expected value for a question (from job requirements)
        
        Args:
            qid: Question ID
            question: Question configuration
            
        Returns:
            Expected value or None
        """
        # This would typically fetch from job requirements
        # For now, return None to use default scoring
        return None
    
    def _check_must_have_failed(self, answers: Dict[str, Any]) -> bool:
        """
        Check if any must-have criteria failed
        
        Args:
            answers: Validated answers
            
        Returns:
            True if any must-have failed
        """
        for qid, answer in answers.items():
            question = question_bank.get_question(qid)
            if question and question.get("must_have", False):
                # Check if answer meets must-have criteria
                # This would be implemented based on specific requirements
                if answer is None or answer == "":
                    return True
        
        return False
    
    async def _update_application_prescreening(
        self,
        application_id: str,
        answers: Dict[str, Any],
        scores: Dict[str, int],
        aggregate_score: float
    ) -> bool:
        """
        Update application with prescreening results
        
        Args:
            application_id: Application identifier
            answers: Validated answers
            scores: Individual question scores
            aggregate_score: Overall match score
            
        Returns:
            True if update successful
        """
        try:
            # This would update the application in the database
            # For now, return True as placeholder
            self.logger.info(f"Updated application {application_id} with prescreening results")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update application {application_id}: {e}")
            return False
    
    async def _update_global_profile(
        self,
        application_id: str,
        answers: Dict[str, Any]
    ) -> bool:
        """
        Update global candidate profile with prescreening answers
        
        Args:
            application_id: Application identifier
            answers: Validated answers
            
        Returns:
            True if update successful
        """
        try:
            # This would update the candidate profile in the database
            # For now, return True as placeholder
            self.logger.info(f"Updated global profile for application {application_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update global profile for {application_id}: {e}")
            return False
    
    def compute_aggregate_score(self, application_id: str) -> float:
        """
        Compute aggregate score for an application
        
        Args:
            application_id: Application identifier
            
        Returns:
            Aggregate score (0-100)
        """
        # This would fetch scores from the database and compute aggregate
        # For now, return 0.0 as placeholder
        return 0.0
    
    async def get_prescreen_summary(self, application_id: str) -> Dict[str, Any]:
        """
        Get prescreen summary for an application
        
        Args:
            application_id: Application identifier
            
        Returns:
            Prescreen summary
        """
        try:
            # This would fetch prescreen data from the database
            # For now, return placeholder data
            return {
                "application_id": application_id,
                "jd_match_score": 0.0,
                "must_have_failed": False,
                "answers_count": 0,
                "last_updated": None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get prescreen summary for {application_id}: {e}")
            return {
                "application_id": application_id,
                "error": str(e)
            }
    
    async def validate_prescreen_completion(
        self,
        application_id: str,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate if prescreening is complete and valid
        
        Args:
            application_id: Application identifier
            answers: Answers to validate
            
        Returns:
            Validation result
        """
        try:
            required_questions = question_bank.get_required_questions()
            missing_questions = []
            invalid_questions = []
            
            for question in required_questions:
                qid = question["qid"]
                if qid not in answers:
                    missing_questions.append(qid)
                else:
                    validation = rules_engine.validate_prescreen_answer(
                        qid, answers[qid], question
                    )
                    if not validation.is_valid:
                        invalid_questions.append({
                            "qid": qid,
                            "error": validation.error_message
                        })
            
            is_complete = len(missing_questions) == 0 and len(invalid_questions) == 0
            
            return {
                "application_id": application_id,
                "is_complete": is_complete,
                "missing_questions": missing_questions,
                "invalid_questions": invalid_questions,
                "total_required": len(required_questions),
                "provided_answers": len(answers)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate prescreen completion: {e}")
            return {
                "application_id": application_id,
                "error": str(e)
            }


# Global prescreening service instance
prescreening_service = PrescreeningService()
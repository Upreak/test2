"""
Chatbot Rules Engine
Validators, normalizers, and scoring functions
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import phonenumbers
from email_validator import validate_email as validate_email_format, EmailNotValidError


class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self, is_valid: bool, value: Any = None, error_message: str = ""):
        self.is_valid = is_valid
        self.value = value
        self.error_message = error_message
    
    def __bool__(self):
        return self.is_valid


class RulesEngine:
    """Rules engine for validation and scoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_email(self, value: str) -> ValidationResult:
        """
        Validate email address
        
        Args:
            value: Email string to validate
            
        Returns:
            ValidationResult with normalized email or error
        """
        try:
            if not value or not isinstance(value, str):
                return ValidationResult(False, None, "Email is required")
            
            # Basic format check
            if "@" not in value or "." not in value.split("@")[-1]:
                return ValidationResult(False, None, "Invalid email format")
            
            # Use email-validator library for comprehensive validation
            try:
                valid = validate_email_format(value)
                return ValidationResult(True, valid.email, "")
            except EmailNotValidError as e:
                return ValidationResult(False, None, str(e))
                
        except Exception as e:
            self.logger.error(f"Email validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def validate_phone(self, value: str, country_code: str = "IN") -> ValidationResult:
        """
        Validate phone number
        
        Args:
            value: Phone number string
            country_code: ISO country code (default: IN)
            
        Returns:
            ValidationResult with normalized phone or error
        """
        try:
            if not value or not isinstance(value, str):
                return ValidationResult(False, None, "Phone number is required")
            
            # Clean phone number
            cleaned = re.sub(r'[^\d+]', '', value)
            
            if not cleaned:
                return ValidationResult(False, None, "Invalid phone number format")
            
            # Parse phone number
            try:
                phone = phonenumbers.parse(cleaned, country_code)
                
                if not phonenumbers.is_valid_number(phone):
                    return ValidationResult(False, None, "Invalid phone number")
                
                # Format to international format
                normalized = phonenumbers.format_number(
                    phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
                
                return ValidationResult(True, normalized, "")
                
            except phonenumbers.NumberParseException:
                return ValidationResult(False, None, "Unable to parse phone number")
                
        except Exception as e:
            self.logger.error(f"Phone validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def validate_number(
        self, 
        value: Union[str, int, float], 
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None
    ) -> ValidationResult:
        """
        Validate numeric value with optional range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            ValidationResult with numeric value or error
        """
        try:
            if value is None:
                return ValidationResult(False, None, "Number is required")
            
            # Convert to float for comparison
            if isinstance(value, str):
                try:
                    num_value = float(value)
                except ValueError:
                    return ValidationResult(False, None, "Invalid number format")
            else:
                num_value = float(value)
            
            # Check range
            if min_val is not None and num_value < min_val:
                return ValidationResult(False, None, f"Value must be >= {min_val}")
            
            if max_val is not None and num_value > max_val:
                return ValidationResult(False, None, f"Value must be <= {max_val}")
            
            # Return as int if it's a whole number
            if num_value.is_integer():
                return ValidationResult(True, int(num_value), "")
            else:
                return ValidationResult(True, num_value, "")
                
        except Exception as e:
            self.logger.error(f"Number validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def validate_choice(
        self, 
        value: Union[str, List[str]], 
        choices: List[str],
        allow_multiple: bool = False
    ) -> ValidationResult:
        """
        Validate choice from predefined list
        
        Args:
            value: Single value or list of values
            choices: List of valid choices
            allow_multiple: Whether multiple selections are allowed
            
        Returns:
            ValidationResult with normalized choices or error
        """
        try:
            if not choices:
                return ValidationResult(False, None, "No valid choices defined")
            
            # Handle single value
            if not allow_multiple:
                if isinstance(value, list):
                    if len(value) != 1:
                        return ValidationResult(False, None, "Only single selection allowed")
                    value = value[0]
                
                if value not in choices:
                    return ValidationResult(False, None, f"Invalid choice. Valid options: {choices}")
                
                return ValidationResult(True, value, "")
            
            # Handle multiple values
            else:
                if isinstance(value, str):
                    value = [value]
                
                if not isinstance(value, list):
                    return ValidationResult(False, None, "Multiple values must be a list")
                
                if len(value) == 0:
                    return ValidationResult(False, None, "At least one choice is required")
                
                invalid_choices = [v for v in value if v not in choices]
                if invalid_choices:
                    return ValidationResult(False, None, f"Invalid choices: {invalid_choices}")
                
                return ValidationResult(True, value, "")
                
        except Exception as e:
            self.logger.error(f"Choice validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def normalize_skills(self, value: Union[str, List[str]]) -> List[str]:
        """
        Normalize skills list
        
        Args:
            value: Skills as string or list
            
        Returns:
            Normalized list of skills
        """
        try:
            if isinstance(value, str):
                # Split by comma and clean
                skills = [skill.strip() for skill in value.split(',') if skill.strip()]
            elif isinstance(value, list):
                skills = [str(skill).strip() for skill in value if str(skill).strip()]
            else:
                skills = []
            
            # Remove duplicates while preserving order
            seen = set()
            normalized_skills = []
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower not in seen:
                    seen.add(skill_lower)
                    normalized_skills.append(skill)
            
            return normalized_skills
            
        except Exception as e:
            self.logger.error(f"Skills normalization error: {e}")
            return []
    
    def compute_match_score(
        self, 
        expected: Union[str, List[str], float], 
        actual: Union[str, List[str], float], 
        weight: float = 1.0
    ) -> int:
        """
        Compute match score between expected and actual values
        
        Args:
            expected: Expected value
            actual: Actual value
            weight: Weight factor (0.0 - 1.0)
            
        Returns:
            Match score (0-100)
        """
        try:
            # Handle None values
            if expected is None or actual is None:
                return 0
            
            # Handle numeric comparison
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                expected_num = float(expected)
                actual_num = float(actual)
                
                if expected_num == 0:
                    return 100 if actual_num == 0 else 0
                
                ratio = actual_num / expected_num
                if ratio >= 1.0:
                    return min(100, int(100 * weight))
                elif ratio >= 0.8:
                    return int(80 * weight)
                elif ratio >= 0.6:
                    return int(60 * weight)
                else:
                    return 0
            
            # Handle list comparison (skills, locations, etc.)
            elif isinstance(expected, list) and isinstance(actual, list):
                if not expected or not actual:
                    return 0
                
                expected_set = set(str(e).lower() for e in expected)
                actual_set = set(str(a).lower() for a in actual)
                
                if not expected_set:
                    return 0
                
                overlap = expected_set.intersection(actual_set)
                match_ratio = len(overlap) / len(expected_set)
                
                return int(match_ratio * 100 * weight)
            
            # Handle string comparison
            elif isinstance(expected, str) and isinstance(actual, str):
                expected_lower = expected.lower().strip()
                actual_lower = actual.lower().strip()
                
                if not expected_lower or not actual_lower:
                    return 0
                
                # Exact match
                if expected_lower == actual_lower:
                    return int(100 * weight)
                
                # Partial match (contains)
                if expected_lower in actual_lower or actual_lower in expected_lower:
                    return int(75 * weight)
                
                return 0
            
            # Type mismatch
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Match score computation error: {e}")
            return 0
    
    def validate_date(self, value: str, format_str: str = "%Y-%m-%d") -> ValidationResult:
        """
        Validate date string
        
        Args:
            value: Date string
            format_str: Expected date format
            
        Returns:
            ValidationResult with datetime or error
        """
        try:
            if not value or not isinstance(value, str):
                return ValidationResult(False, None, "Date is required")
            
            dt = datetime.strptime(value, format_str)
            return ValidationResult(True, dt, "")
            
        except ValueError as e:
            return ValidationResult(False, None, f"Invalid date format. Expected: {format_str}")
        except Exception as e:
            self.logger.error(f"Date validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def validate_boolean(self, value: Union[str, bool, int]) -> ValidationResult:
        """
        Validate boolean value
        
        Args:
            value: Value to validate
            
        Returns:
            ValidationResult with boolean or error
        """
        try:
            if isinstance(value, bool):
                return ValidationResult(True, value, "")
            
            if isinstance(value, str):
                value_lower = value.lower().strip()
                if value_lower in ['true', 'yes', '1', 'on']:
                    return ValidationResult(True, True, "")
                elif value_lower in ['false', 'no', '0', 'off']:
                    return ValidationResult(True, False, "")
                else:
                    return ValidationResult(False, None, "Invalid boolean value")
            
            if isinstance(value, int):
                return ValidationResult(True, bool(value), "")
            
            return ValidationResult(False, None, "Invalid boolean type")
            
        except Exception as e:
            self.logger.error(f"Boolean validation error: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")
    
    def compute_aggregate_score(
        self, 
        scores: List[int], 
        weights: Optional[List[float]] = None
    ) -> float:
        """
        Compute aggregate score from multiple scores
        
        Args:
            scores: List of individual scores
            weights: Optional weights for each score
            
        Returns:
            Aggregate score (0-100)
        """
        try:
            if not scores:
                return 0.0
            
            if weights and len(weights) != len(scores):
                return 0.0
            
            if weights:
                weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
                total_weight = sum(weights)
                return weighted_sum / total_weight if total_weight > 0 else 0.0
            else:
                return sum(scores) / len(scores)
                
        except Exception as e:
            self.logger.error(f"Aggregate score computation error: {e}")
            return 0.0
    
    def validate_prescreen_answer(
        self, 
        qid: str, 
        answer: Any, 
        question_config: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate prescreen answer based on question configuration
        
        Args:
            qid: Question ID
            answer: Answer value
            question_config: Question configuration from question bank
            
        Returns:
            ValidationResult
        """
        try:
            # Check if required
            if question_config.get("required", False) and answer is None:
                return ValidationResult(False, None, "This field is required")
            
            # Skip validation for None values on non-required fields
            if answer is None:
                return ValidationResult(True, None, "")
            
            question_type = question_config.get("type")
            validation_rule = question_config.get("validation_rule")
            
            # Type-specific validation
            if question_type == "email":
                return self.validate_email(str(answer))
            
            elif question_type == "phone":
                return self.validate_phone(str(answer))
            
            elif question_type == "number":
                min_val = max_val = None
                if validation_rule:
                    # Parse validation rule like "min:0,max:100"
                    rules = {}
                    for rule in validation_rule.split(","):
                        if ":" in rule:
                            key, val = rule.split(":")
                            rules[key.strip()] = float(val.strip())
                    
                    min_val = rules.get("min")
                    max_val = rules.get("max")
                
                return self.validate_number(answer, min_val, max_val)
            
            elif question_type in ["select", "multi_select"]:
                choices = question_config.get("choices", [])
                allow_multiple = question_type == "multi_select"
                return self.validate_choice(answer, choices, allow_multiple)
            
            elif question_type == "boolean":
                return self.validate_boolean(answer)
            
            elif question_type == "date":
                format_str = validation_rule or "%Y-%m-%d"
                return self.validate_date(str(answer), format_str)
            
            elif question_type == "text":
                # Basic text validation
                if not isinstance(answer, str):
                    answer = str(answer)
                
                if validation_rule:
                    # Parse validation rule like "min_length:2,max_length:100"
                    rules = {}
                    for rule in validation_rule.split(","):
                        if ":" in rule:
                            key, val = rule.split(":")
                            rules[key.strip()] = int(val.strip())
                    
                    min_len = rules.get("min_length", 0)
                    max_len = rules.get("max_length", float('inf'))
                    
                    if len(answer) < min_len:
                        return ValidationResult(False, None, f"Minimum length is {min_len}")
                    if len(answer) > max_len:
                        return ValidationResult(False, None, f"Maximum length is {max_len}")
                
                return ValidationResult(True, answer, "")
            
            else:
                return ValidationResult(True, answer, "")
                
        except Exception as e:
            self.logger.error(f"Prescreen answer validation error for {qid}: {e}")
            return ValidationResult(False, None, f"Validation error: {str(e)}")


# Global rules engine instance
rules_engine = RulesEngine()
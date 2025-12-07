"""
Chatbot Logging Utilities
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional


class ChatbotLogger:
    """Enhanced logging for chatbot operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def log_session_start(self, session_id: str, user_id: str, platform: str):
        """Log session start"""
        self.logger.info(
            "Session started",
            extra={
                "session_id": session_id,
                "user_id": user_id,
                "platform": platform,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "session_start"
            }
        )
    
    def log_message(self, session_id: str, message: str, direction: str, message_type: str = "text"):
        """Log message exchange"""
        self.logger.info(
            f"Message {direction}",
            extra={
                "session_id": session_id,
                "message": message,
                "direction": direction,
                "message_type": message_type,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "message"
            }
        )
    
    def log_prescreen_answer(self, application_id: str, qid: str, answer: str, score: int):
        """Log prescreen answer processing"""
        self.logger.info(
            "Prescreen answer processed",
            extra={
                "application_id": application_id,
                "qid": qid,
                "answer": answer,
                "score": score,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "prescreen_answer"
            }
        )
    
    def log_export_job(self, export_job_id: str, job_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log export job status"""
        self.logger.info(
            f"Export job {status}",
            extra={
                "export_job_id": export_job_id,
                "job_id": job_id,
                "status": status,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "export_job"
            }
        )
    
    def log_error(self, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        self.logger.error(
            error_message,
            extra={
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "error"
            }
        )


def setup_chatbot_logging():
    """Setup chatbot-specific logging configuration"""
    # Configure formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler for chatbot logs
    file_handler = logging.FileHandler('logs/chatbot.log')
    file_handler.setFormatter(formatter)
    
    # Configure chatbot logger
    chatbot_logger = logging.getLogger('chatbot')
    chatbot_logger.setLevel(logging.INFO)
    chatbot_logger.addHandler(console_handler)
    chatbot_logger.addHandler(file_handler)
    
    return chatbot_logger
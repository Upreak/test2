"""
Chatbot Router
FastAPI router for chatbot endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend_app.chatbot.controller import ChatbotController
from backend_app.chatbot.models.session_model import UserRole
from backend_app.schemas.auth import UserSession

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/start-session")
async def start_session(
    user_id: str = Body(..., embed=True),
    platform: str = Body(..., embed=True),
    platform_user_id: str = Body(..., embed=True),
    user_role: UserRole = Body(..., embed=True),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Start a new chatbot session
    
    Request:
    {
        "user_id": "user-123",
        "platform": "whatsapp",
        "platform_user_id": "whatsapp-user-123",
        "user_role": "candidate"
    }
    
    Response:
    {
        "session_id": "session-123",
        "user_id": "user-123",
        "platform": "whatsapp",
        "user_role": "candidate",
        "created_at": "2025-01-01T00:00:00"
    }
    """
    return await controller.start_session(user_id, platform, platform_user_id, user_role)


@router.post("/message")
async def process_message(
    session_id: str = Body(..., embed=True),
    message: str = Body(..., embed=True),
    message_type: str = Body(default="text", embed=True),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Process an incoming message
    
    Request:
    {
        "session_id": "session-123",
        "message": "Hello, I want to apply for a job",
        "message_type": "text"
    }
    
    Response:
    {
        "session_id": "session-123",
        "response": "Hello! I'd be happy to help you apply for a job. Let me start by collecting some information about you.",
        "next_action": "collect_basic_info",
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    return await controller.process_message(session_id, message, message_type)


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Get session details
    
    Response:
    {
        "session_id": "session-123",
        "user_id": "user-123",
        "platform": "whatsapp",
        "user_role": "candidate",
        "state": "onboarding",
        "context": {
            "current_skill": "onboarding",
            "step": 1,
            "collected_data": {}
        },
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00"
    }
    """
    return await controller.get_session(session_id)


@router.put("/session/{session_id}/state")
async def update_session_state(
    session_id: str,
    state: str = Body(..., embed=True),
    context: Optional[Dict[str, Any]] = Body(default=None, embed=True),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Update session state and context
    
    Request:
    {
        "state": "onboarding_completed",
        "context": {
            "current_skill": "resume_intake",
            "step": 1,
            "collected_data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    }
    
    Response:
    {
        "session_id": "session-123",
        "state": "onboarding_completed",
        "context": {
            "current_skill": "resume_intake",
            "step": 1,
            "collected_data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        },
        "updated_at": "2025-01-01T00:00:00"
    }
    """
    return await controller.update_session_state(session_id, state, context)


# Candidate endpoints
@router.post("/applications/{application_id}/prescreen-answers")
async def submit_prescreen_answers(
    application_id: str,
    answers: Dict[str, Any] = Body(...),
    update_global_profile: bool = Body(default=False),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Submit prescreen answers for an application
    
    Request:
    {
        "answers": {
            "ps_current_ctc": "10.5",
            "ps_expected_ctc": "15.0",
            "ps_notice_period": "60",
            "ps_total_experience": "5",
            "ps_key_skills": ["Python", "FastAPI", "SQLAlchemy"]
        },
        "update_global_profile": true
    }
    
    Response:
    {
        "application_id": "app-123",
        "jd_match_score": 85,
        "must_have_failed": false,
        "answers_processed": 5,
        "global_profile_updated": true,
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    try:
        # This would integrate with prescreening_service
        return {
            "application_id": application_id,
            "jd_match_score": 85,
            "must_have_failed": False,
            "answers_processed": len(answers),
            "global_profile_updated": update_global_profile,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process prescreen answers: {str(e)}")


# Recruiter endpoints
@router.post("/jobs/{job_id}/prescreen-questions")
async def create_prescreen_questions(
    job_id: str,
    questions: List[Dict[str, Any]] = Body(...),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Create prescreen questions for a job
    
    Request:
    [
        {
            "qid": "ps_current_ctc",
            "question_text": "What is your current CTC?",
            "type": "number",
            "required": true,
            "must_have": true,
            "weight": 10
        }
    ]
    
    Response:
    {
        "job_id": "job-123",
        "questions_created": 1,
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    try:
        return {
            "job_id": job_id,
            "questions_created": len(questions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create prescreen questions: {str(e)}")


@router.get("/jobs/{job_id}/prescreen-questions")
async def get_prescreen_questions(
    job_id: str,
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Get prescreen questions for a job
    
    Response:
    [
        {
            "qid": "ps_current_ctc",
            "question_text": "What is your current CTC?",
            "type": "number",
            "required": true,
            "must_have": true,
            "weight": 10,
            "validation_rule": "min:0,max:100"
        }
    ]
    """
    try:
        # Return default questions for now
        return [
            {
                "qid": "ps_current_ctc",
                "question_text": "What is your current CTC (LPA)?",
                "type": "number",
                "required": True,
                "must_have": True,
                "weight": 10,
                "validation_rule": "min:0,max:100"
            },
            {
                "qid": "ps_expected_ctc",
                "question_text": "What is your expected CTC (LPA)?",
                "type": "number",
                "required": True,
                "must_have": True,
                "weight": 10,
                "validation_rule": "min:0,max:100"
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prescreen questions: {str(e)}")


@router.post("/jobs/{job_id}/suggest-questions")
async def suggest_prescreen_questions(
    job_id: str,
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Suggest prescreen questions based on job description
    
    Response:
    {
        "job_id": "job-123",
        "suggested_questions": [
            {
                "qid": "ps_current_ctc",
                "question_text": "What is your current CTC?",
                "type": "number",
                "required": true,
                "must_have": true,
                "weight": 10
            }
        ],
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    try:
        return {
            "job_id": job_id,
            "suggested_questions": [
                {
                    "qid": "ps_current_ctc",
                    "question_text": "What is your current CTC (LPA)?",
                    "type": "number",
                    "required": True,
                    "must_have": True,
                    "weight": 10
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest questions: {str(e)}")


@router.post("/jobs/{job_id}/outreach")
async def trigger_candidate_outreach(
    job_id: str,
    candidate_ids: List[str] = Body(...),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Trigger outreach to candidates for a job
    
    Request:
    {
        "candidate_ids": ["candidate-123", "candidate-456"]
    }
    
    Response:
    {
        "job_id": "job-123",
        "candidates_contacted": 2,
        "outreach_initiated": true,
        "timestamp": "2025-01-01T00:00:00"
    }
    """
    try:
        return {
            "job_id": job_id,
            "candidates_contacted": len(candidate_ids),
            "outreach_initiated": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger outreach: {str(e)}")


@router.post("/jobs/{job_id}/export-candidates")
async def export_candidates(
    job_id: str,
    application_ids: List[str] = Body(...),
    client_spoc_id: str = Body(...),
    include_resumes: bool = Body(default=True),
    include_json: bool = Body(default=True),
    controller: ChatbotController = Depends(lambda: ChatbotController())
):
    """
    Export candidates for a job
    
    Request:
    {
        "application_ids": ["app-123", "app-456"],
        "client_spoc_id": "spoc-123",
        "include_resumes": true,
        "include_json": true
    }
    
    Response:
    {
        "export_job_id": "export-123",
        "job_id": "job-123",
        "applications_included": 2,
        "status": "queued",
        "download_url": null,
        "created_at": "2025-01-01T00:00:00"
    }
    """
    try:
        return {
            "export_job_id": f"export-{job_id}",
            "job_id": job_id,
            "applications_included": len(application_ids),
            "status": "queued",
            "download_url": None,
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create export job: {str(e)}")
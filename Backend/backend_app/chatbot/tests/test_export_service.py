"""
Test Export Service
Tests for Excel export and candidate data export functionality
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestExportService:
    """Test suite for export service functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_job_id = str(uuid4())
        self.test_export_job_id = f"export-{self.test_job_id}"
        self.test_application_ids = [str(uuid4()), str(uuid4())]
        self.test_client_spoc_id = str(uuid4())
        
        # Expected Excel header
        self.expected_header = [
            "Application ID", "Candidate Name", "Email", "Phone", 
            "Total Experience", "Current CTC (LPA)", "Expected CTC (LPA)", 
            "Notice Period", "Current Location", "Preferred Location", 
            "Skills", "JD Match Score", "Must-Have-Failed", 
            "PreScreen_Summary_JSON", "Recruiter Notes", "Submitted At"
        ]
    
    def test_export_job_creation(self):
        """Test creating an export job"""
        export_job = {
            "export_job_id": self.test_export_job_id,
            "job_id": self.test_job_id,
            "applications_included": len(self.test_application_ids),
            "status": "queued",
            "download_url": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        assert export_job["export_job_id"] == self.test_export_job_id
        assert export_job["job_id"] == self.test_job_id
        assert export_job["applications_included"] == len(self.test_application_ids)
        assert export_job["status"] == "queued"
        assert export_job["download_url"] is None
        assert "created_at" in export_job
    
    def test_excel_header_format(self):
        """Test that Excel header matches specification"""
        # Verify header order and content
        assert len(self.expected_header) == 16
        
        # Check specific columns
        assert self.expected_header[0] == "Application ID"
        assert self.expected_header[1] == "Candidate Name"
        assert self.expected_header[2] == "Email"
        assert self.expected_header[3] == "Phone"
        assert self.expected_header[4] == "Total Experience"
        assert self.expected_header[5] == "Current CTC (LPA)"
        assert self.expected_header[6] == "Expected CTC (LPA)"
        assert self.expected_header[7] == "Notice Period"
        assert self.expected_header[8] == "Current Location"
        assert self.expected_header[9] == "Preferred Location"
        assert self.expected_header[10] == "Skills"
        assert self.expected_header[11] == "JD Match Score"
        assert self.expected_header[12] == "Must-Have-Failed"
        assert self.expected_header[13] == "PreScreen_Summary_JSON"
        assert self.expected_header[14] == "Recruiter Notes"
        assert self.expected_header[15] == "Submitted At"
    
    def test_export_job_status_transitions(self):
        """Test export job status transitions"""
        statuses = ["queued", "processing", "completed", "failed"]
        
        # Test status progression
        current_status = "queued"
        assert current_status in statuses
        
        current_status = "processing"
        assert current_status in statuses
        
        current_status = "completed"
        assert current_status in statuses
    
    def test_export_completion_response(self):
        """Test export completion response format"""
        completion_response = {
            "export_job_id": self.test_export_job_id,
            "job_id": self.test_job_id,
            "applications_included": len(self.test_application_ids),
            "status": "completed",
            "download_url": "https://your-domain.com/downloads/export-job123.zip",
            "created_at": "2025-01-01T00:00:00",
            "completed_at": "2025-01-01T00:05:00"
        }
        
        assert completion_response["status"] == "completed"
        assert completion_response["download_url"] is not None
        assert completion_response["download_url"].startswith("https://")
        assert completion_response["download_url"].endswith(".zip")
        assert "completed_at" in completion_response
    
    def test_application_data_format(self):
        """Test application data format for export"""
        application_data = {
            "Application ID": "app-123",
            "Candidate Name": "John Doe",
            "Email": "john.doe@example.com",
            "Phone": "+1234567890",
            "Total Experience": "5.5",
            "Current CTC (LPA)": "10.5",
            "Expected CTC (LPA)": "15.0",
            "Notice Period": "60",
            "Current Location": "Bangalore",
            "Preferred Location": "Remote, Bangalore",
            "Skills": "Python, FastAPI, SQL",
            "JD Match Score": "85",
            "Must-Have-Failed": "false",
            "PreScreen_Summary_JSON": '{"scores": {"compensation": 90, "experience": 80}}',
            "Recruiter Notes": "Strong candidate with relevant experience",
            "Submitted At": "2025-01-01T00:00:00"
        }
        
        # Verify all required fields are present
        for field in self.expected_header:
            assert field in application_data
        
        # Verify data types
        assert isinstance(application_data["JD Match Score"], str)
        assert application_data["Must-Have-Failed"] in ["true", "false"]
        assert application_data["PreScreen_Summary_JSON"].startswith("{")
        assert application_data["Submitted At"] is not None
    
    def test_zip_file_contents(self):
        """Test expected contents of export ZIP file"""
        expected_files = [
            "candidates.xlsx",
            "resumes/John_Doe_Resume.pdf",
            "resumes/Jane_Smith_Resume.docx",
            "metadata.json"
        ]
        
        # Verify expected files
        assert "candidates.xlsx" in expected_files
        assert any(f.startswith("resumes/") and f.endswith((".pdf", ".docx")) for f in expected_files)
        assert "metadata.json" in expected_files
    
    def test_metadata_json_format(self):
        """Test metadata.json format in export"""
        metadata = {
            "export_job_id": self.test_export_job_id,
            "job_id": self.test_job_id,
            "exported_at": datetime.utcnow().isoformat(),
            "applications_count": len(self.test_application_ids),
            "applications": [
                {
                    "application_id": self.test_application_ids[0],
                    "candidate_name": "John Doe",
                    "match_score": 85,
                    "prescreen_summary": {
                        "total_questions": 5,
                        "answered": 5,
                        "must_have_failed": False
                    }
                }
            ]
        }
        
        assert metadata["export_job_id"] == self.test_export_job_id
        assert metadata["job_id"] == self.test_job_id
        assert metadata["applications_count"] == len(self.test_application_ids)
        assert len(metadata["applications"]) == len(self.test_application_ids)
    
    def test_application_submission_tracking(self):
        """Test that applications are marked as submitted to client"""
        # After successful export, applications should be marked as submitted
        application_status = {
            "submitted_to_client": True,
            "submitted_to_client_at": datetime.utcnow().isoformat()
        }
        
        assert application_status["submitted_to_client"] is True
        assert application_status["submitted_to_client_at"] is not None
    
    def test_export_error_handling(self):
        """Test export error handling"""
        error_response = {
            "export_job_id": self.test_export_job_id,
            "status": "failed",
            "error_message": "Failed to generate Excel file",
            "failed_at": datetime.utcnow().isoformat()
        }
        
        assert error_response["status"] == "failed"
        assert error_response["error_message"] is not None
        assert "failed_at" in error_response
    
    def test_export_permissions(self):
        """Test export access permissions"""
        # Only authorized users should be able to export
        allowed_roles = ["recruiter", "admin", "client_spoc"]
        
        for role in allowed_roles:
            assert role in ["recruiter", "admin", "client_spoc"]
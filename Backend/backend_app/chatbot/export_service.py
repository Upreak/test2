"""
Chatbot Export Service
Generate Excel exports and zip files for candidates
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os
import zipfile
import tempfile
from io import BytesIO
import pandas as pd
from pathlib import Path


class ExportService:
    """Service for handling candidate exports"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def create_export_job(
        self,
        job_id: str,
        application_ids: List[str],
        client_spoc_id: str,
        include_resumes: bool = True,
        include_json: bool = True
    ) -> Dict[str, Any]:
        """
        Create export job
        
        Args:
            job_id: Job identifier
            application_ids: List of application IDs to export
            client_spoc_id: Client SPOC identifier
            include_resumes: Whether to include resumes
            include_json: Whether to include JSON summaries
            
        Returns:
            Export job creation result
        """
        try:
            self.logger.info(f"Creating export job for job {job_id}")
            
            # Generate export job ID
            export_job_id = f"export_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create export job record
            export_job = {
                "export_job_id": export_job_id,
                "job_id": job_id,
                "application_ids": application_ids,
                "client_spoc_id": client_spoc_id,
                "include_resumes": include_resumes,
                "include_json": include_json,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "download_url": None
            }
            
            # This would save to database
            # For now, return success as placeholder
            result = {
                "export_job_id": export_job_id,
                "job_id": job_id,
                "applications_included": len(application_ids),
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Created export job {export_job_id} for job {job_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create export job: {e}")
            return {
                "job_id": job_id,
                "error": str(e),
                "success": False
            }
    
    async def run_export_job(self, export_job_id: str) -> Dict[str, Any]:
        """
        Run export job and generate files
        
        Args:
            export_job_id: Export job identifier
            
        Returns:
            Export job result
        """
        try:
            self.logger.info(f"Running export job {export_job_id}")
            
            # This would fetch export job details from database
            # For now, use placeholder data
            export_job = {
                "export_job_id": export_job_id,
                "job_id": "job_123",
                "application_ids": ["app_1", "app_2", "app_3"],
                "include_resumes": True,
                "include_json": True
            }
            
            # Generate Excel file
            excel_data = await self._generate_excel_file(export_job)
            
            # Generate JSON summaries
            json_data = await self._generate_json_summaries(export_job)
            
            # Generate resume files (if requested)
            resume_files = {}
            if export_job.get("include_resumes", False):
                resume_files = await self._collect_resume_files(export_job)
            
            # Create zip file
            zip_file_path = await self._create_export_zip(
                export_job_id, excel_data, json_data, resume_files
            )
            
            # Generate download URL
            download_url = f"{os.getenv('EXPORT_TMP_PATH', '/tmp')}/{export_job_id}.zip"
            
            # Update applications as submitted
            await self._mark_applications_submitted(export_job["application_ids"])
            
            result = {
                "export_job_id": export_job_id,
                "zip_file_path": zip_file_path,
                "download_url": download_url,
                "excel_file": excel_data["filename"],
                "json_files": list(json_data.keys()),
                "resume_files": list(resume_files.keys()),
                "completed_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Completed export job {export_job_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run export job {export_job_id}: {e}")
            return {
                "export_job_id": export_job_id,
                "error": str(e),
                "success": False
            }
    
    async def _generate_excel_file(self, export_job: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Excel file with candidate data"""
        
        # Excel header specification
        excel_headers = [
            "Application ID", "Candidate Name", "Email", "Phone", 
            "Total Experience", "Current CTC (LPA)", "Expected CTC (LPA)", 
            "Notice Period", "Current Location", "Preferred Location", 
            "Skills", "JD Match Score", "Must-Have-Failed", 
            "PreScreen_Summary_JSON", "Recruiter Notes", "Submitted At"
        ]
        
        # This would fetch application data from database
        # For now, use placeholder data
        sample_data = [
            {
                "Application ID": "app_123",
                "Candidate Name": "John Doe",
                "Email": "john@example.com",
                "Phone": "+91 9876543210",
                "Total Experience": "5",
                "Current CTC (LPA)": "10.5",
                "Expected CTC (LPA)": "15.0",
                "Notice Period": "60",
                "Current Location": "Bangalore",
                "Preferred Location": "Bangalore, Remote",
                "Skills": "Python, FastAPI, SQL",
                "JD Match Score": "85",
                "Must-Have-Failed": "False",
                "PreScreen_Summary_JSON": '{"current_ctc": 10.5, "expected_ctc": 15.0}',
                "Recruiter Notes": "",
                "Submitted At": datetime.utcnow().isoformat()
            }
        ]
        
        # Create DataFrame
        df = pd.DataFrame(sample_data, columns=excel_headers)
        
        # Save to temporary file
        temp_dir = os.getenv('EXPORT_TMP_PATH', tempfile.gettempdir())
        excel_filename = f"{export_job['export_job_id']}_candidates.xlsx"
        excel_path = os.path.join(temp_dir, excel_filename)
        
        df.to_excel(excel_path, index=False)
        
        return {
            "filename": excel_filename,
            "path": excel_path,
            "headers": excel_headers
        }
    
    async def _generate_json_summaries(self, export_job: Dict[str, Any]) -> Dict[str, str]:
        """Generate JSON summaries for each application"""
        
        json_summaries = {}
        
        for app_id in export_job["application_ids"]:
            # This would fetch detailed application data
            # For now, use placeholder data
            summary = {
                "application_id": app_id,
                "candidate_details": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+91 9876543210"
                },
                "job_match": {
                    "jd_match_score": 85,
                    "must_have_failed": False,
                    "skills_match": ["Python", "FastAPI"],
                    "experience_match": True
                },
                "prescreen_answers": {
                    "current_ctc": 10.5,
                    "expected_ctc": 15.0,
                    "notice_period": 60
                },
                "submitted_at": datetime.utcnow().isoformat()
            }
            
            json_filename = f"{app_id}_summary.json"
            json_content = json.dumps(summary, indent=2)
            json_summaries[json_filename] = json_content
        
        return json_summaries
    
    async def _collect_resume_files(self, export_job: Dict[str, Any]) -> Dict[str, bytes]:
        """Collect resume files for applications"""
        
        resume_files = {}
        
        for app_id in export_job["application_ids"]:
            # This would fetch resume files from storage
            # For now, return empty placeholder
            resume_files[f"{app_id}_resume.pdf"] = b""
        
        return resume_files
    
    async def _create_export_zip(
        self,
        export_job_id: str,
        excel_data: Dict[str, Any],
        json_data: Dict[str, str],
        resume_files: Dict[str, bytes]
    ) -> str:
        """Create zip file with all export data"""
        
        temp_dir = os.getenv('EXPORT_TMP_PATH', tempfile.gettempdir())
        zip_filename = f"{export_job_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Excel file
            zipf.write(excel_data["path"], excel_data["filename"])
            
            # Add JSON files
            for filename, content in json_data.items():
                zipf.writestr(filename, content)
            
            # Add resume files
            for filename, content in resume_files.items():
                if content:  # Only add if content exists
                    zipf.writestr(filename, content)
        
        return zip_path
    
    async def _mark_applications_submitted(self, application_ids: List[str]) -> bool:
        """Mark applications as submitted to client"""
        
        try:
            # This would update applications in database
            # For now, return success as placeholder
            self.logger.info(f"Marked {len(application_ids)} applications as submitted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark applications as submitted: {e}")
            return False
    
    async def get_export_status(self, export_job_id: str) -> Dict[str, Any]:
        """Get export job status"""
        
        try:
            self.logger.info(f"Getting status for export job {export_job_id}")
            
            # This would fetch from database
            # For now, return placeholder data
            return {
                "export_job_id": export_job_id,
                "status": "completed",
                "progress": 100,
                "download_url": f"/exports/{export_job_id}.zip",
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get export status: {e}")
            return {
                "export_job_id": export_job_id,
                "error": str(e)
            }
    
    async def cleanup_export_files(self, export_job_id: str) -> bool:
        """Clean up temporary export files"""
        
        try:
            temp_dir = os.getenv('EXPORT_TMP_PATH', tempfile.gettempdir())
            
            # Remove Excel file
            excel_file = os.path.join(temp_dir, f"{export_job_id}_candidates.xlsx")
            if os.path.exists(excel_file):
                os.remove(excel_file)
            
            # Remove zip file
            zip_file = os.path.join(temp_dir, f"{export_job_id}.zip")
            if os.path.exists(zip_file):
                os.remove(zip_file)
            
            self.logger.info(f"Cleaned up export files for {export_job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup export files: {e}")
            return False


# Global export service instance
export_service = ExportService()
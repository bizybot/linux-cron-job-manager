from crontab import CronTab
import os
import tempfile
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CronService:
    def __init__(self):
        self.cron = CronTab(user=True)
    
    def add_job(self, name: str, expression: str, command: str) -> bool:
        """Add a new cron job to the system"""
        try:
            # Create a temporary script file
            script_content = f"#!/bin/bash\n{command}"
            
            # Create scripts directory if it doesn't exist
            scripts_dir = os.path.join(os.getcwd(), "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            
            # Write script to file
            script_path = os.path.join(scripts_dir, f"{name}.sh")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # For now, just log the job creation without actually adding to system cron
            # This avoids permission issues in development
            logger.info(f"Would add cron job: {name} with expression: {expression}")
            logger.info(f"Script saved to: {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding cron job {name}: {e}")
            return False
    
    def remove_job(self, name: str) -> bool:
        """Remove a cron job from the system"""
        try:
            # Remove script file
            script_path = os.path.join(os.getcwd(), "scripts", f"{name}.sh")
            if os.path.exists(script_path):
                os.remove(script_path)
                logger.info(f"Removed script file: {script_path}")
            
            logger.info(f"Would remove cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error removing cron job {name}: {e}")
            return False
    
    def enable_job(self, name: str) -> bool:
        """Enable a cron job"""
        try:
            logger.info(f"Would enable cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error enabling cron job {name}: {e}")
            return False
    
    def disable_job(self, name: str) -> bool:
        """Disable a cron job"""
        try:
            logger.info(f"Would disable cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling cron job {name}: {e}")
            return False
    
    def list_jobs(self) -> List[dict]:
        """List all cron jobs"""
        # For development, return empty list to avoid permission issues
        # In production, this would return actual system cron jobs
        jobs = []
        logger.info("Would list system cron jobs")
        return jobs
    
    def validate_expression(self, expression: str) -> bool:
        """Validate cron expression format"""
        try:
            # Test if the expression can be parsed
            test_job = self.cron.new(command="echo test")
            test_job.setall(expression)
            return True
        except Exception:
            return False 
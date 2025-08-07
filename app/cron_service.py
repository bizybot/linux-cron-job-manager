from crontab import CronTab
import os
import tempfile
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CronService:
    def __init__(self, scripts_dir="scripts"):
        self.cron = CronTab(user=True)
        self.scripts_dir = os.path.join(os.getcwd(), scripts_dir)
        os.makedirs(self.scripts_dir, exist_ok=True)

    def _get_script_path(self, name: str) -> str:
        return os.path.join(self.scripts_dir, f"{name}.sh")

    def add_job(self, name: str, expression: str, command: str) -> bool:
        """Add a new cron job to the system"""
        try:
            container_script_path = self._get_script_path(name)
            script_content = f"#!/bin/bash\n{command}"
            
            with open(container_script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(container_script_path, 0o755)

            job = self.cron.new(command=container_script_path, comment=name)
            job.setall(expression)
            self.cron.write()

            logger.info(f"Added cron job: {name} with expression: {expression}")
            return True
        except Exception as e:
            logger.error(f"Error adding cron job {name}: {e}")
            return False

    def remove_job(self, name: str) -> bool:
        """Remove a cron job from the system"""
        try:
            container_script_path = self._get_script_path(name)
            if os.path.exists(container_script_path):
                os.remove(container_script_path)
            
            for job in self.cron.find_comment(name):
                self.cron.remove(job)
            self.cron.write()

            logger.info(f"Removed cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error removing cron job {name}: {e}")
            return False

    def enable_job(self, name: str) -> bool:
        """Enable a cron job"""
        try:
            for job in self.cron.find_comment(name):
                job.enable()
            self.cron.write()
            logger.info(f"Enabled cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error enabling cron job {name}: {e}")
            return False

    def disable_job(self, name: str) -> bool:
        """Disable a cron job"""
        try:
            for job in self.cron.find_comment(name):
                job.enable(False)
            self.cron.write()
            logger.info(f"Disabled cron job: {name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling cron job {name}: {e}")
            return False

    def list_jobs(self) -> List[dict]:
        """List all cron jobs from the system"""
        jobs = []
        for job in self.cron:
            jobs.append({
                "name": job.comment,
                "expression": str(job.slices),
                "command": job.command,
                "enabled": job.is_enabled()
            })
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
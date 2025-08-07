from crontab import CronTab
import os
import tempfile
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CronService:
    def __init__(self, scripts_dir="scripts"):
        self.host_scripts_dir = os.environ.get("HOST_SCRIPTS_DIR")
        self.use_ssh = os.environ.get("USE_SSH", "false").lower() == "true"

        if self.use_ssh:
            ssh_host = os.environ.get("CRON_HOST")
            ssh_user = os.environ.get("CRON_USER")
            ssh_key = os.environ.get("CRON_SSH_KEY_PATH")

            if not all([ssh_host, ssh_user, ssh_key]):
                raise ValueError("CRON_HOST, CRON_USER, and CRON_SSH_KEY_PATH must be set when USE_SSH is true")

            self.cron = CronTab(user=ssh_user, host=ssh_host, ssh_identity_file=ssh_key)
        else:
            self.cron = CronTab(user=True)

        self.scripts_dir = os.path.join(os.getcwd(), scripts_dir)
        os.makedirs(self.scripts_dir, exist_ok=True)

    def _get_script_path(self, name: str, on_host: bool = False) -> str:
        if on_host and self.use_ssh:
            return os.path.join(self.host_scripts_dir, f"{name}.sh")
        return os.path.join(self.scripts_dir, f"{name}.sh")

    def add_job(self, name: str, expression: str, command: str) -> bool:
        """Add a new cron job to the system"""
        try:
            container_script_path = self._get_script_path(name)
            script_content = f"#!/bin/bash\n{command}"
            
            with open(container_script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(container_script_path, 0o755)

            host_script_path = self._get_script_path(name, on_host=True)
            job = self.cron.new(command=host_script_path, comment=name)
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
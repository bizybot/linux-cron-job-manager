#!/usr/bin/env python3
"""
Test script for Linux Cron Job Manager
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing Linux Cron Job Manager API...")
    
    # Test 1: Get all jobs (should be empty initially)
    print("\n1. Testing GET /api/jobs...")
    response = requests.get(f"{BASE_URL}/api/jobs")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: Create a test job
    print("\n2. Testing POST /api/jobs...")
    import time
    timestamp = int(time.time())
    test_job = {
        "name": f"test-backup-{timestamp}",
        "expression": "*/5 * * * *",  # Every 5 minutes
        "command": "#!/bin/bash\necho 'Test backup at $(date)' >> /tmp/test_backup.log",
        "description": "Test backup job for demonstration"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/jobs",
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_job)
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        job_data = response.json()
        print(f"   Created job ID: {job_data['id']}")
        job_id = job_data['id']
    else:
        print(f"   Error: {response.text}")
        return
    
    # Test 3: Get the created job
    print(f"\n3. Testing GET /api/jobs/{job_id}...")
    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        job_data = response.json()
        print(f"   Job name: {job_data['name']}")
        print(f"   Job status: {'Enabled' if job_data['enabled'] else 'Disabled'}")
    
    # Test 4: Disable the job
    print(f"\n4. Testing POST /api/jobs/{job_id}/disable...")
    response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/disable")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 5: Enable the job
    print(f"\n5. Testing POST /api/jobs/{job_id}/enable...")
    response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/enable")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 6: Get all jobs again
    print("\n6. Testing GET /api/jobs (after creation)...")
    response = requests.get(f"{BASE_URL}/api/jobs")
    print(f"   Status: {response.status_code}")
    jobs = response.json()
    print(f"   Number of jobs: {len(jobs)}")
    
    # Test 7: Delete the test job
    print(f"\n7. Testing DELETE /api/jobs/{job_id}...")
    response = requests.delete(f"{BASE_URL}/api/jobs/{job_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 8: Get system jobs
    print("\n8. Testing GET /api/system/jobs...")
    response = requests.get(f"{BASE_URL}/api/system/jobs")
    print(f"   Status: {response.status_code}")
    system_jobs = response.json()
    print(f"   Number of system jobs: {len(system_jobs)}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the application.")
        print("   Make sure the application is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 
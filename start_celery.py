import subprocess
import sys
import os
from pathlib import Path

def start_celery():
    """Start Celery worker and beat scheduler."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Start Celery worker
    worker_cmd = [
        'celery',
        '-A',
        'ugc_platform',
        'worker',
        '--loglevel=info',
        '--pool=solo',
        '--concurrency=4'
    ]
    
    # Start Celery beat
    beat_cmd = [
        'celery',
        '-A',
        'ugc_platform',
        'beat',
        '--loglevel=info'
    ]
    
    try:
        # Start worker process
        worker_process = subprocess.Popen(
            worker_cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Start beat process
        beat_process = subprocess.Popen(
            beat_cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("Celery worker and beat scheduler started successfully.")
        print("Press Ctrl+C to stop.")
        
        # Wait for processes to complete
        worker_process.wait()
        beat_process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping Celery processes...")
        worker_process.terminate()
        beat_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Celery: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    start_celery() 
# dbbasic-queue Usage Guide

Complete guide to using dbbasic-queue for background job processing.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Production Deployment](#production-deployment)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## Installation

```bash
pip install dbbasic-queue
```

Or from source:

```bash
git clone https://github.com/dbbasic/dbbasic-queue
cd dbbasic-queue
pip install -e .
```

## Quick Start

### 1. Queue a job

```python
from dbbasic_queue import enqueue

# Queue an email to be sent
job_id = enqueue('send_email', {
    'to': 'user@example.com',
    'subject': 'Welcome!',
    'body': 'Thanks for signing up.'
})

print(f"Job queued with ID: {job_id}")
```

### 2. Create a worker

```python
# worker.py
from dbbasic_queue import process_jobs
import smtplib

def send_email_handler(payload):
    # Send email using payload data
    # ... SMTP code here ...
    return {'sent_at': time.time()}

if __name__ == '__main__':
    handlers = {
        'send_email': send_email_handler,
    }
    process_jobs(handlers, max_attempts=3)
```

### 3. Run worker with cron

```bash
# Add to crontab
* * * * * cd /app && python3 worker.py >> /var/log/queue.log 2>&1
```

## Core Concepts

### Jobs

A **job** is a unit of work to be done asynchronously. Each job has:

- **ID**: Unique identifier (16 hex chars)
- **Type**: Handler name (e.g., 'send_email')
- **Payload**: JSON data (parameters for the handler)
- **Status**: pending, processing, completed, failed, cancelled
- **Timestamps**: created_at, run_at
- **Attempts**: Retry counter
- **Error**: Error message (if failed)
- **Result**: Return value from handler (if completed)

### Handlers

A **handler** is a Python function that processes a job:

```python
def my_handler(payload):
    # Do work using payload data
    result = do_something(payload['param'])
    return result  # Stored in job.result
```

### Worker

A **worker** is a script that:
1. Queries for pending jobs
2. Executes job handlers
3. Updates job status
4. Handles retries and failures

## API Reference

### `enqueue(job_type, payload, run_at=None)`

Add job to queue.

**Parameters:**
- `job_type` (str): Job handler name
- `payload` (dict): Job parameters (must be JSON-serializable)
- `run_at` (int, optional): Unix timestamp to run job (default: now)

**Returns:**
- `job_id` (str): Unique job identifier

**Example:**
```python
# Run immediately
job_id = enqueue('process_video', {'video_id': 42})

# Run in 1 hour
import time
job_id = enqueue('cleanup', {}, run_at=time.time() + 3600)
```

### `process_jobs(handlers, max_attempts=3)`

Process pending jobs (called by worker).

**Parameters:**
- `handlers` (dict): Map of job_type → handler function
- `max_attempts` (int): Max retry attempts before marking failed

**Returns:**
- None

**Example:**
```python
def email_handler(payload):
    send_email(payload['to'], payload['subject'])
    return {'sent': True}

def video_handler(payload):
    process_video(payload['video_id'])
    return {'processed': True}

handlers = {
    'send_email': email_handler,
    'process_video': video_handler,
}

process_jobs(handlers, max_attempts=3)
```

### `get_job(job_id)`

Get job status and details.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:**
- `job` (dict): Job details or None if not found

**Job dict structure:**
```python
{
    'id': 'abc123...',
    'type': 'send_email',
    'payload': {'to': 'user@example.com', ...},
    'status': 'completed',
    'created_at': 1696886400,
    'run_at': 1696886400,
    'attempts': 1,
    'error': None,
    'result': {'sent_at': 1696886405}
}
```

**Example:**
```python
job = get_job(job_id)
if job:
    print(f"Status: {job['status']}")
    if job['status'] == 'completed':
        print(f"Result: {job['result']}")
    elif job['status'] == 'failed':
        print(f"Error: {job['error']}")
```

### `cancel_job(job_id)`

Cancel pending job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:**
- `bool`: True if cancelled, False if not found or already processing/completed

**Example:**
```python
if cancel_job(job_id):
    print("Job cancelled")
else:
    print("Cannot cancel (not found or already started)")
```

## Examples

### Example 1: Email Queue

```python
# app.py - Web application
from flask import Flask, request, jsonify
from dbbasic_queue import enqueue

app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data['email']

    # Create user...

    # Queue welcome email (non-blocking)
    enqueue('send_email', {
        'to': email,
        'subject': 'Welcome!',
        'body': 'Thanks for signing up.'
    })

    return jsonify({'message': 'Signup successful'})
```

```python
# worker.py - Background worker
from dbbasic_queue import process_jobs
import smtplib
from email.message import EmailMessage

def send_email_handler(payload):
    msg = EmailMessage()
    msg['From'] = 'noreply@example.com'
    msg['To'] = payload['to']
    msg['Subject'] = payload['subject']
    msg.set_content(payload['body'])

    with smtplib.SMTP('localhost') as smtp:
        smtp.send_message(msg)

    return {'sent_at': time.time()}

if __name__ == '__main__':
    process_jobs({'send_email': send_email_handler})
```

### Example 2: Video Processing

```python
# Queue video processing job
job_id = enqueue('process_video', {
    'video_id': 123,
    'input_path': '/uploads/video123.mp4',
    'output_format': 'h264'
})

# Worker handler
def process_video_handler(payload):
    import subprocess

    video_id = payload['video_id']
    input_path = payload['input_path']
    output_path = f'/processed/video{video_id}.mp4'

    # Run ffmpeg
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ], check=True)

    return {
        'output_path': output_path,
        'processed_at': time.time()
    }
```

### Example 3: Scheduled Jobs

```python
import time

# Schedule report for midnight
midnight = ...  # Calculate next midnight timestamp

job_id = enqueue('generate_daily_report', {
    'report_type': 'sales',
    'date': '2025-10-09'
}, run_at=midnight)
```

### Example 4: Bulk Operations

```python
# Queue 1000 email jobs
user_ids = range(1, 1001)

for user_id in user_ids:
    enqueue('send_newsletter', {
        'user_id': user_id,
        'newsletter_id': 42
    })

# Worker processes them one by one
# Runs every minute via cron
```

## Production Deployment

### Directory Structure

```
/app/
  ├── app.py                    # Web application
  ├── workers/
  │   └── queue_worker.py       # Background worker
  ├── data/
  │   └── queue.tsv             # Queue storage
  └── logs/
      └── queue.log             # Worker logs
```

### Worker Script

```python
#!/usr/bin/env python3
# workers/queue_worker.py

import sys
import logging
from dbbasic_queue import process_jobs

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import handlers
from handlers import email_handler, video_handler, report_handler

if __name__ == '__main__':
    handlers = {
        'send_email': email_handler,
        'process_video': video_handler,
        'generate_report': report_handler,
    }

    try:
        logging.info("Starting queue worker")
        process_jobs(handlers, max_attempts=3)
        logging.info("Queue worker finished")
    except Exception as e:
        logging.error(f"Worker error: {e}", exc_info=True)
        sys.exit(1)
```

### Cron Setup

```bash
# Edit crontab
crontab -e

# Run worker every minute
* * * * * cd /app && python3 workers/queue_worker.py >> /app/logs/queue.log 2>&1
```

### File Permissions

```bash
# Ensure queue file is writable
mkdir -p /app/data
touch /app/data/queue.tsv
chmod 664 /app/data/queue.tsv
chown www-data:www-data /app/data/queue.tsv

# Ensure log directory is writable
mkdir -p /app/logs
chmod 775 /app/logs
chown www-data:www-data /app/logs
```

## Monitoring

### Check Queue Status

```bash
# Count pending jobs
cat data/queue.tsv | grep pending | wc -l

# Show failed jobs
cat data/queue.tsv | grep failed

# Show recent jobs (last 10)
tail -10 data/queue.tsv
```

### Admin Endpoint

```python
@app.route('/admin/queue')
def queue_status():
    import os

    if not os.path.exists('data/queue.tsv'):
        return jsonify({'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0})

    stats = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}

    with open('data/queue.tsv', 'r') as f:
        for line in f.readlines()[1:]:  # Skip header
            if line.strip():
                status = line.split('\t')[3]
                if status in stats:
                    stats[status] += 1

    return jsonify(stats)
```

### Worker Logs

```bash
# View worker logs
tail -f /app/logs/queue.log

# Search for errors
grep ERROR /app/logs/queue.log

# Count jobs processed today
grep "$(date +%Y-%m-%d)" /app/logs/queue.log | wc -l
```

## Troubleshooting

### Jobs not processing

1. Check worker is running:
   ```bash
   ps aux | grep queue_worker
   ```

2. Check cron logs:
   ```bash
   grep CRON /var/log/syslog
   ```

3. Check queue file permissions:
   ```bash
   ls -la data/queue.tsv
   ```

### Jobs failing repeatedly

1. View failed jobs:
   ```bash
   cat data/queue.tsv | grep failed
   ```

2. Check error messages in queue file

3. Test handler manually:
   ```python
   from handlers import send_email_handler
   send_email_handler({'to': 'test@example.com', ...})
   ```

### Queue file too large

1. Archive old jobs:
   ```bash
   # Backup current queue
   cp data/queue.tsv data/queue.tsv.bak

   # Filter to keep only recent/pending jobs
   head -1 data/queue.tsv > data/queue.tsv.new
   cat data/queue.tsv | grep -E "pending|processing" >> data/queue.tsv.new
   mv data/queue.tsv.new data/queue.tsv
   ```

2. Implement cleanup job:
   ```python
   def cleanup_old_jobs():
       import time
       cutoff = int(time.time()) - (7 * 86400)  # 7 days ago

       # Read all rows
       with open('data/queue.tsv', 'r') as f:
           lines = f.readlines()

       # Keep header + recent jobs
       with open('data/queue.tsv', 'w') as f:
           f.write(lines[0])  # Header
           for line in lines[1:]:
               parts = line.split('\t')
               if len(parts) >= 5:
                   created_at = int(parts[4])
                   status = parts[3]
                   # Keep pending/processing or recent completed/failed
                   if status in ['pending', 'processing'] or created_at > cutoff:
                       f.write(line)
   ```

## Best Practices

1. **Keep handlers simple** - One job = one task
2. **Make handlers idempotent** - Safe to run multiple times
3. **Validate payload** - Check required fields in handler
4. **Return useful results** - Store important data in result
5. **Log errors** - Use proper logging in handlers
6. **Monitor queue size** - Alert if queue grows too large
7. **Clean up old jobs** - Archive/delete completed jobs periodically
8. **Test handlers** - Unit test each handler separately

## Performance

- **Enqueue**: 0.1ms (TSV append)
- **Process**: 0.5ms per job (query + update)
- **Capacity**: < 10,000 queued jobs (single server)

For higher throughput, consider graduating to Redis/Celery.

## See Also

- [Full Specification](http://dbbasic.com/queue-spec)
- [DBBasic Modules](http://dbbasic.com/)
- [GitHub Repository](https://github.com/dbbasic/dbbasic-queue)

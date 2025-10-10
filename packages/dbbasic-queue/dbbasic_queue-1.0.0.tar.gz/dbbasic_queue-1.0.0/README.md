# dbbasic-queue

TSV-based job queue for async tasks. Simple, reliable background job processing.

## Philosophy

> "Store work, not workers. Queue jobs, not processes."

Background jobs are **actual work to be done**, not temporary state. Unlike sessions (which are ephemeral authentication), jobs need persistent storage, retry logic, and failure handling.

## Features

- **Simple**: ~50 lines of core code
- **Reliable**: Retry logic with exponential backoff
- **Debuggable**: Plain text TSV, inspect with cat/grep
- **Unix-Compatible**: Cron-based workers, no daemon required
- **Foundation-First**: Built on dbbasic-tsv

## Installation

```bash
pip install dbbasic-queue
```

## Quick Start

### 1. Queue a job

```python
from dbbasic_queue import enqueue

# Queue an email to be sent
job_id = enqueue('send_email', {
    'to': 'user@example.com',
    'subject': 'Welcome',
    'body': 'Thanks for signing up!'
})
```

### 2. Create a worker

```python
# workers/queue_worker.py
from dbbasic_queue import process_jobs

def send_email_handler(payload):
    """Send email via SMTP"""
    # ... send email logic
    return {'sent_at': time.time()}

if __name__ == '__main__':
    handlers = {
        'send_email': send_email_handler,
    }
    process_jobs(handlers, max_attempts=3)
```

### 3. Set up cron

```bash
# Run worker every minute
* * * * * cd /app && python3 workers/queue_worker.py >> /var/log/queue.log 2>&1
```

## API Reference

### `enqueue(job_type, payload, run_at=None)`

Add job to queue.

- **job_type** (str): Job handler name
- **payload** (dict): Job parameters
- **run_at** (int, optional): Unix timestamp to run job (default: now)
- **Returns**: job_id (str)

### `process_jobs(handlers, max_attempts=3)`

Process pending jobs (run by worker).

- **handlers** (dict): Map of job_type → handler function
- **max_attempts** (int): Max retry attempts before marking failed

### `get_job(job_id)`

Get job status and details.

- **job_id** (str): Job identifier
- **Returns**: job (dict) or None

### `cancel_job(job_id)`

Cancel pending job.

- **job_id** (str): Job identifier
- **Returns**: bool (True if cancelled)

## Storage Format

Jobs are stored in a single TSV file: `data/queue.tsv`

```
id  type    payload status  created_at  run_at  attempts    error   result
```

## Performance

- Enqueue job: 0.1ms
- Process job: 0.5ms
- Perfect for single-server apps with < 10K jobs

## When to Use

✅ Single-server applications
✅ < 10,000 queued jobs
✅ Background email sending
✅ Video processing
✅ Report generation

## When to Graduate to Redis/Celery

- 100K+ queued jobs
- Multiple worker servers
- Sub-second job pickup required

## License

MIT

## Full Specification

See http://dbbasic.com/queue-spec for complete specification.

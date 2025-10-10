"""
Core queue implementation (~50 lines)
"""

import time
import json
import secrets
import os

# NOTE: This is a stub implementation. In production, you would:
# pip install dbbasic-tsv
# from dbbasic_tsv import append, query, update
#
# For now, we'll implement basic TSV operations directly

QUEUE_FILE = 'data/queue.tsv'
MAX_ATTEMPTS = 3


def _get_queue_file():
    """Get the current queue file path"""
    return QUEUE_FILE


def _ensure_queue_file():
    """Ensure queue file exists with headers"""
    queue_file = _get_queue_file()
    if not os.path.exists(queue_file):
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        with open(queue_file, 'w') as f:
            f.write('id\ttype\tpayload\tstatus\tcreated_at\trun_at\tattempts\terror\tresult\n')


def _read_tsv():
    """Read TSV file and return rows"""
    _ensure_queue_file()
    queue_file = _get_queue_file()
    with open(queue_file, 'r') as f:
        lines = f.readlines()
    if not lines:
        return []
    # Skip header and ensure all rows have 9 columns
    rows = []
    for line in lines[1:]:
        if line.strip():
            parts = line.strip().split('\t')
            # Pad with empty strings to ensure 9 columns
            while len(parts) < 9:
                parts.append('')
            rows.append(parts)
    return rows


def _write_tsv(rows):
    """Write rows to TSV file"""
    _ensure_queue_file()
    queue_file = _get_queue_file()
    with open(queue_file, 'w') as f:
        f.write('id\ttype\tpayload\tstatus\tcreated_at\trun_at\tattempts\terror\tresult\n')
        for row in rows:
            f.write('\t'.join(row) + '\n')


def _append_row(row):
    """Append a row to TSV file"""
    _ensure_queue_file()
    queue_file = _get_queue_file()
    with open(queue_file, 'a') as f:
        f.write('\t'.join(row) + '\n')


def enqueue(job_type, payload, run_at=None):
    """
    Add job to queue

    Args:
        job_type (str): Job handler name (e.g., 'send_email')
        payload (dict): Job parameters
        run_at (int, optional): Unix timestamp to run job (default: now)

    Returns:
        str: Unique job identifier
    """
    job_id = secrets.token_hex(8)
    now = int(time.time())
    run_at = run_at or now

    _append_row([
        job_id,
        job_type,
        json.dumps(payload),
        'pending',
        str(now),
        str(run_at),
        '0',  # attempts
        '',   # error
        ''    # result
    ])
    return job_id


def process_jobs(handlers, max_attempts=MAX_ATTEMPTS):
    """
    Process pending jobs (worker)

    Args:
        handlers (dict): Map of job_type → handler function
        max_attempts (int): Max retry attempts before marking failed
    """
    now = int(time.time())

    # Get pending jobs that are ready to run
    rows = _read_tsv()
    jobs = [row for row in rows if len(row) >= 9 and row[3] == 'pending' and int(row[5]) <= now]

    for job in jobs:
        job_id, job_type, payload_json, status, created, run_at, attempts, error, result = job
        attempts = int(attempts)

        # Update to processing
        all_rows = _read_tsv()
        for i, r in enumerate(all_rows):
            if r[0] == job_id:
                all_rows[i] = [r[0], r[1], r[2], 'processing', r[4], r[5], r[6], r[7], r[8]]
        _write_tsv(all_rows)

        # Execute job
        try:
            handler = handlers.get(job_type)
            if not handler:
                raise Exception(f"No handler for {job_type}")

            payload = json.loads(payload_json)
            result = handler(payload)

            # Success
            all_rows = _read_tsv()
            for i, r in enumerate(all_rows):
                if r[0] == job_id:
                    all_rows[i] = [r[0], r[1], r[2], 'completed', r[4], r[5], str(attempts + 1), '', json.dumps(result) if result else '']
            _write_tsv(all_rows)
        except Exception as e:
            attempts += 1

            all_rows = _read_tsv()
            for i, r in enumerate(all_rows):
                if r[0] == job_id:
                    if attempts >= max_attempts:
                        # Failed permanently
                        all_rows[i] = [r[0], r[1], r[2], 'failed', r[4], r[5], str(attempts), str(e), '']
                    else:
                        # Retry with backoff
                        backoff = 60 * (2 ** attempts)  # Exponential backoff
                        new_run_at = int(time.time()) + backoff
                        all_rows[i] = [r[0], r[1], r[2], 'pending', r[4], str(new_run_at), str(attempts), str(e), '']
            _write_tsv(all_rows)


def get_job(job_id):
    """
    Get job details

    Args:
        job_id (str): Job identifier

    Returns:
        dict: Job details or None if not found
    """
    rows = _read_tsv()
    for row in rows:
        if len(row) >= 9 and row[0] == job_id:
            return {
                'id': row[0],
                'type': row[1],
                'payload': json.loads(row[2]) if row[2] else {},
                'status': row[3],
                'created_at': int(row[4]),
                'run_at': int(row[5]),
                'attempts': int(row[6]),
                'error': row[7] or None,
                'result': json.loads(row[8]) if row[8] else None
            }
    return None


def cancel_job(job_id):
    """
    Cancel pending job

    Args:
        job_id (str): Job identifier

    Returns:
        bool: True if cancelled, False if already processing/completed
    """
    all_rows = _read_tsv()
    cancelled = False

    for i, r in enumerate(all_rows):
        if len(r) >= 9 and r[0] == job_id and r[3] == 'pending':
            all_rows[i] = [r[0], r[1], r[2], 'cancelled', r[4], r[5], r[6], 'Cancelled by user', '']
            cancelled = True
            break

    if cancelled:
        _write_tsv(all_rows)

    return cancelled

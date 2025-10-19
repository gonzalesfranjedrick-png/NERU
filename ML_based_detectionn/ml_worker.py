import concurrent.futures
import threading
import logging

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_futures = {}
_lock = threading.Lock()


def submit_job(func, *args, job_id=None, **kwargs):
    """Submit a job to the threadpool. Returns job_id and future.
    If job_id is not provided, a future id is used.
    """
    future = _executor.submit(func, *args, **kwargs)
    if job_id is None:
        job_id = id(future)
    with _lock:
        _futures[job_id] = future
    logging.info(f"Job submitted: {job_id}")
    return job_id, future


def get_job_status(job_id):
    with _lock:
        fut = _futures.get(job_id)
    if fut is None:
        return None
    if fut.cancelled():
        return {'status': 'cancelled'}
    if fut.done():
        try:
            return {'status': 'done', 'result': fut.result()}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    return {'status': 'running'}

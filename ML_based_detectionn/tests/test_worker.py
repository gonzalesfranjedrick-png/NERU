import time, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml_worker import submit_job, get_job_status


def sample_task(x, y):
    return x + y


if __name__ == '__main__':
    job_id, fut = submit_job(sample_task, 2, 3)
    print('submitted job', job_id)
    for _ in range(10):
        st = get_job_status(job_id)
        print('status:', st)
        if st and st.get('status') == 'done':
            print('result:', st.get('result'))
            break
        time.sleep(0.2)
    else:
        print('job did not finish in time')

from fastapi import APIRouter, HTTPException
from celery_app import celery_app

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a background job"""
    task = celery_app.AsyncResult(job_id)
    
    if task.state == 'PENDING':
        response = {
            "job_id": job_id,
            "status": "pending",
            "message": "Task is waiting to be executed"
        }
    elif task.state == 'PROGRESS':
        response = {
            "job_id": job_id,
            "status": "processing",
            "message": "Task is being processed",
            "progress": task.info.get('current', 0),
            "total": task.info.get('total', 100)
        }
    elif task.state == 'SUCCESS':
        response = {
            "job_id": job_id,
            "status": "completed",
            "message": "Task completed successfully",
            "result": task.result
        }
    elif task.state == 'FAILURE':
        response = {
            "job_id": job_id,
            "status": "failed",
            "message": "Task failed",
            "error": str(task.info)
        }
    elif task.state == 'RETRY':
        response = {
            "job_id": job_id,
            "status": "retrying",
            "message": "Task is being retried"
        }
    else:
        response = {
            "job_id": job_id,
            "status": task.state.lower(),
            "message": f"Task state: {task.state}"
        }
    
    return response

@router.get("/{job_id}/result")
async def get_job_result(job_id: str):
    """Get the result of a completed background job"""
    task = celery_app.AsyncResult(job_id)
    
    if task.state == 'SUCCESS':
        return {
            "job_id": job_id,
            "status": "completed",
            "result": task.result
        }
    elif task.state == 'FAILURE':
        raise HTTPException(status_code=400, detail=f"Task failed: {str(task.info)}")
    elif task.state in ['PENDING', 'PROGRESS', 'RETRY']:
        raise HTTPException(status_code=202, detail=f"Task is still {task.state.lower()}")
    else:
        raise HTTPException(status_code=400, detail=f"Task state: {task.state}")

@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a background job"""
    task = celery_app.AsyncResult(job_id)
    task.revoke(terminate=True)
    
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled successfully"
    }

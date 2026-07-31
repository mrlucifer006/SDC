from fastapi import APIRouter, Depends
from sqlmodel import Session
from sqlalchemy import func, cast, Integer

from backend.database import get_session
from backend.models import User, Submission, UserProgress
from backend.core.auth import get_current_user

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard(
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    users = session.query(User).filter(User.is_admin == False).all()
    
    leaderboard = []
    for u in users:
        # Calculate total solve time (sum of time taken per completed gate)
        total_solve_seconds = 0.0
        for p in u.progress:
            if p.is_completed and p.completed_at:
                solve_delta = (p.completed_at - p.timestamp).total_seconds()
                total_solve_seconds += max(0, solve_delta)
        
        leaderboard.append({
            "username": u.username,
            "email": u.email,
            "total_score": u.total_score,
            "total_solve_time_seconds": total_solve_seconds,
            "is_locked": u.is_locked
        })
        
    leaderboard.sort(key=lambda x: (
        -x["total_score"], 
        x["total_solve_time_seconds"], 
    ))
    
    # Assign ranks
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
        
    return leaderboard

@router.get("/submissions")
def get_recent_submissions(
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    subs = session.query(Submission, User.username, User.email).join(User, Submission.user_id == User.id).order_by(Submission.timestamp.desc()).limit(100).all()
    return [{
        "id": s.Submission.id,
        "username": s.username,
        "email": s.email,
        "gate_id": s.Submission.gate_id,
        "passed": s.Submission.passed,
        "execution_time_ms": s.Submission.execution_time_ms,
        "timestamp": s.Submission.timestamp
    } for s in subs]

@router.get("/stats")
def get_gate_stats(
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    stats = session.query(
        UserProgress.gate_id,
        func.count(UserProgress.user_id).label("unlocked_count"),
        func.sum(cast(UserProgress.is_completed, Integer)).label("completed_count") # Ensure cast for summation
    ).group_by(UserProgress.gate_id).all()
    
    return [{"gate_id": s.gate_id, "unlocked": s.unlocked_count, "completed": s.completed_count} for s in stats]

@router.post("/unlock/{username}")
def unlock_user(
    username: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    from fastapi import HTTPException, status
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    
    target_user = session.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    target_user.is_locked = False
    session.commit()
    return {"status": "ok", "message": f"User {username} has been unlocked"}

from backend.core.state import update_settings
from pydantic import BaseModel

class MalpracticeSetting(BaseModel):
    enabled: bool

@router.post("/settings/malpractice")
def toggle_malpractice(
    setting: MalpracticeSetting,
    user: User = Depends(get_current_user),
):
    from fastapi import HTTPException, status
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    
    update_settings({"malpractice_enabled": setting.enabled})
    return {"status": "ok", "malpractice_enabled": setting.enabled}

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_session
from backend.models import User, Gate, UserProgress, Submission
from backend.core.auth import get_current_user
from backend.services.judge0 import submit_code_to_judge0

router = APIRouter()

@router.get("/leaderboard")
def get_public_leaderboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Public leaderboard visible to all authenticated users. Excludes admin users."""
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
            "total_score": u.total_score,
            "total_solve_time_seconds": total_solve_seconds,
        })
    
    future_time = datetime.max
    
    leaderboard.sort(key=lambda x: (
        -x["total_score"], 
        x["total_solve_time_seconds"],
    ))
    
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
        
    return leaderboard

class CodeSubmission(BaseModel):
    gate_id: int
    source_code: str
    language: str
    stdin: str = ""

@router.get("/progress")
def get_user_progress(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    progress = session.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    return progress

@router.get("/gates")
def get_gates(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    gates = session.query(Gate).order_by(Gate.id).all()
    progress = session.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    progress_dict = {p.gate_id: p for p in progress}
    
    result = []
    for gate in gates:
        prog = progress_dict.get(gate.id)
        is_unlocked = prog.is_unlocked if prog else (gate.prerequisite_gate_id is None)
        is_completed = prog.is_completed if prog else False
        
        result.append({
            "id": gate.id,
            "name": gate.name,
            "desc": gate.cipher_type,
            "points_awarded": gate.points_awarded,
            "unlocked": is_unlocked,
            "completed": is_completed
        })
    return result

@router.get("/gates/{gate_id}")
def get_gate(gate_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    gate = session.query(Gate).filter(Gate.id == gate_id).first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
        
    prog = session.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.gate_id == gate.id
    ).first()
    
    is_unlocked = prog.is_unlocked if prog else (gate.prerequisite_gate_id is None)
    
    if not is_unlocked:
        raise HTTPException(status_code=403, detail="Gate is locked")
    
    # Create progress record on first view to track solve start time
    if not prog and is_unlocked:
        prog = UserProgress(user_id=current_user.id, gate_id=gate.id, is_unlocked=True)
        session.add(prog)
        session.commit()
        
    return {
        "id": gate.id,
        "name": gate.name,
        "desc": gate.cipher_type,
        "points_awarded": gate.points_awarded,
        "problem_statement": gate.problem_statement,
        "sample_input": gate.sample_input,
        "sample_output": gate.sample_output
    }

from backend.core.state import get_settings

@router.get("/settings")
def get_public_settings():
    return get_settings()

@router.post("/submit")
async def submit_code(
    submission: CodeSubmission, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify gate is unlocked
    gate = session.query(Gate).filter(Gate.id == submission.gate_id).first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
        
    progress = session.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.gate_id == gate.id
    ).first()
    
    if not progress or not progress.is_unlocked:
        # Check if it's gate 1 (always unlocked)
        if gate.prerequisite_gate_id is not None:
             raise HTTPException(status_code=403, detail="Gate is locked")
    
    # 1. Run Sample Test Case
    sample_res = await submit_code_to_judge0(
        source_code=submission.source_code,
        language=submission.language,
        stdin=gate.sample_input
    )
    
    sample_passed = False
    sample_stdout = sample_res.get("stdout", "")
    if sample_stdout and sample_stdout.strip() == gate.sample_output.strip():
        sample_passed = True
        
    hidden_stdout = ""
    hidden_res = {}
    
    import json
    try:
        hidden_inputs = json.loads(gate.hidden_input)
        hidden_outputs = json.loads(gate.hidden_output)
    except (json.JSONDecodeError, TypeError):
        hidden_inputs = [gate.hidden_input]
        hidden_outputs = [gate.hidden_output]
    
    total_cases = 1 + len(hidden_inputs)
    passed_cases = 1 if sample_passed else 0
    total_hidden_time = 0.0
    
    # 2. Run Hidden Test Cases always
    for h_input, h_output in zip(hidden_inputs, hidden_outputs):
        hidden_res = await submit_code_to_judge0(
            source_code=submission.source_code,
            language=submission.language,
            stdin=h_input
        )
        total_hidden_time += hidden_res.get("time_ms", 0)
        curr_hidden_stdout = hidden_res.get("stdout", "")
        if curr_hidden_stdout and curr_hidden_stdout.strip() == h_output.strip():
            passed_cases += 1
    
    passed = (passed_cases > 0)
    earned_score = int((passed_cases / total_cases) * gate.points_awarded)

    total_time_ms = sample_res.get("time_ms", 0) + total_hidden_time
        
    # Log Submission
    new_sub = Submission(
        user_id=current_user.id,
        gate_id=gate.id,
        passed=passed,
        execution_time_ms=total_time_ms,
        code_snippet=submission.source_code
    )
    session.add(new_sub)
    
    # Update Progress and Score
    if not progress:
        progress = UserProgress(user_id=current_user.id, gate_id=gate.id, is_unlocked=True, score=0)
        session.add(progress)
    
    if passed_cases > 0:
        if earned_score > progress.score:
            current_user.total_score += (earned_score - progress.score)
            progress.score = earned_score
            
    if passed:
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
            
            # Unlock next gate
            next_gate = session.query(Gate).filter(Gate.prerequisite_gate_id == gate.id).first()
            if next_gate:
                next_progress = session.query(UserProgress).filter(
                    UserProgress.user_id == current_user.id,
                    UserProgress.gate_id == next_gate.id
                ).first()
                if not next_progress:
                    next_progress = UserProgress(user_id=current_user.id, gate_id=next_gate.id, is_unlocked=True, score=0)
                    session.add(next_progress)
                
    session.commit()
    
    return {
        "passed": passed,
        "sample_passed": sample_passed,
        "passed_cases": passed_cases,
        "total_cases": total_cases,
        "earned_score": earned_score,
        "stdout": sample_stdout, 
        "stderr": sample_res.get("stderr", "") or hidden_res.get("stderr", ""),
        "compile_output": sample_res.get("compile_output"),
        "time_ms": total_time_ms
    }

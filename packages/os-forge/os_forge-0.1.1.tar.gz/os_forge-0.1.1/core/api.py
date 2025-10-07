"""
FastAPI Application for OS Forge

Main API endpoints and application setup.
"""

import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import Config
from security import verify_api_key
from database import HardeningResult, get_db, init_db
from reporting import ReportGenerator
from agents.linux.linux_agent import LinuxAgent
from agents.windows.windows_agent import WindowsAgent
from agents.common.os_detector import OSDetector
from agents.common.base_agent import RuleStatus
from agents.linux.linux_rules import LinuxRuleCategory, get_linux_hardening_rules
from agents.windows.windows_rules import WindowsRuleCategory, get_windows_hardening_rules
from typing import Dict, List, Any, Optional
import platform


# Initialize components
os_detector = OSDetector()
current_os = os_detector.detect_os()

# Initialize appropriate agent based on OS
if current_os['type'] == "linux":
    policy_engine = LinuxAgent()
    rules_module = get_linux_hardening_rules
elif current_os['type'] == "windows":
    policy_engine = WindowsAgent()
    rules_module = get_windows_hardening_rules
else:
    # Fallback to Linux agent for unknown OS
    policy_engine = LinuxAgent()
    rules_module = get_linux_hardening_rules

report_generator = ReportGenerator()

# Create FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def read_root():
    """
    Get system information and API status
    
    Returns basic information about the system and available rules.
    """
    rules = rules_module()
    return {
        "message": "OS Forge - Multi-Platform System Hardening Tool",
        "detected_os": current_os['type'],
        "os_distribution": current_os.get('distribution', {}).get('name', 'Unknown'),
        "available_rules": len(rules),
        "agent_type": type(policy_engine).__name__,
        "rule_categories": list(set(rule.get("category", "unknown") for rule in rules))
    }


@app.get("/rules")
def get_rules(level: Optional[str] = None, category: Optional[str] = None):
    """
    Get applicable hardening rules
    
    Args:
        level: Hardening level (basic, moderate, strict) - if None, returns all rules
        category: Optional category filter
        
    Returns:
        Dict containing applicable rules and count
    """
    rules = rules_module()
    
    # Filter by level (only if specified)
    if level:
        rules = [rule for rule in rules if level in rule.get("level", [])]
    
    # Filter by category
    if category:
        rules = [rule for rule in rules if rule.get("category") == category]
    
    return {"rules": rules, "count": len(rules)}


@app.post("/run")
def run_hardening(level: Optional[str] = None, dry_run: bool = True, category: Optional[str] = None, api_key: str = Depends(verify_api_key)):
    """
    Execute hardening rules
    
    This endpoint requires authentication and executes security hardening rules.
    
    Args:
        level: Hardening level (basic, moderate, strict) - if None, executes all rules
        dry_run: If True, only check current state without applying changes
        category: Optional category filter
        api_key: Valid API key (provided via Authorization header)
        
    Returns:
        Dict containing execution results and summary
    """
    # Get rules based on filters
    rules = rules_module()
    
    # Filter by level
    if level:
        rules = [rule for rule in rules if level in rule.get("level", [])]
    
    # Filter by category
    if category:
        rules = [rule for rule in rules if rule.get("category") == category]
    
    results = []
    db = next(get_db())
    
    for rule in rules:
        try:
            # Check rule first
            check_result = policy_engine.check_rule(rule)
            
            # If dry run, just return the check result
            if dry_run:
                result = {
                    "rule_id": check_result.rule_id,
                    "description": check_result.description,
                    "severity": rule["severity"],
                    "status": check_result.status.value,
                    "old_value": check_result.old_value,
                    "new_value": check_result.new_value,
                    "error": check_result.error
                }
            else:
                # Apply remediation if not dry run and rule failed
                if check_result.status == RuleStatus.FAIL:
                    remediate_result = policy_engine.remediate_rule(rule, dry_run=False)
                    result = {
                        "rule_id": remediate_result.rule_id,
                        "description": remediate_result.description,
                        "severity": rule["severity"],
                        "status": remediate_result.status.value,
                        "old_value": remediate_result.old_value,
                        "new_value": remediate_result.new_value,
                        "error": remediate_result.error
                    }
                else:
                    # Rule already passes, return check result
                    result = {
                        "rule_id": check_result.rule_id,
                        "description": check_result.description,
                        "severity": rule["severity"],
                        "status": check_result.status.value,
                        "old_value": check_result.old_value,
                        "new_value": check_result.new_value,
                        "error": check_result.error
                    }
            
            results.append(result)
            
            # Save to database
            db_result = HardeningResult(
                rule_id=result["rule_id"],
                description=result["description"],
                severity=result["severity"],
                status=result["status"],
                old_value=result.get("old_value"),
                new_value=result.get("new_value"),
                rollback_data=json.dumps(rule.get("rollback", ""))
            )
            db.add(db_result)
            
        except Exception as e:
            # Handle rule execution errors
            error_result = {
                "rule_id": rule["id"],
                "description": rule["description"],
                "severity": rule["severity"],
                "status": "error",
                "error": str(e)
            }
            results.append(error_result)
    
    db.commit()
    
    return {
        "status": "completed",
        "dry_run": dry_run,
        "level": level,
        "category": category,
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.get("status") == "pass"),
            "failed": sum(1 for r in results if r.get("status") == "fail"),
            "errors": sum(1 for r in results if r.get("status") == "error")
        }
    }


@app.get("/history")
def get_history():
    """
    Get hardening execution history
    
    Returns the latest 50 execution results.
    """
    db = next(get_db())
    results = db.query(HardeningResult).order_by(HardeningResult.timestamp.desc()).limit(50).all()
    return {"history": [
        {
            "id": r.id,
            "rule_id": r.rule_id,
            "description": r.description,
            "status": r.status,
            "timestamp": r.timestamp
        } for r in results
    ]}


@app.get("/report", response_class=HTMLResponse)
def generate_report():
    """
    Generate HTML compliance report
    
    Returns an HTML page with detailed compliance information.
    """
    db = next(get_db())
    results = db.query(HardeningResult).order_by(HardeningResult.timestamp.desc()).limit(100).all()
    
    os_info = f"{current_os['type']} - {current_os.get('distribution', {}).get('name', 'Unknown')}"
    return report_generator.generate_html_report(results, os_info)


@app.get("/report/pdf")
def generate_pdf_report():
    """
    Generate PDF compliance report
    
    Returns a downloadable PDF report with compliance information.
    """
    db = next(get_db())
    results = db.query(HardeningResult).order_by(HardeningResult.timestamp.desc()).limit(100).all()
    
    os_info = f"{current_os['type']} - {current_os.get('distribution', {}).get('name', 'Unknown')}"
    pdf_buffer = report_generator.generate_pdf_report(results, os_info)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=os_forge_report.pdf"}
    )


@app.post("/rollback/{rule_id}")
def rollback_rule(rule_id: str, api_key: str = Depends(verify_api_key)):
    """
    Rollback a specific hardening rule
    
    This endpoint requires authentication and reverts a previously applied rule.
    
    Args:
        rule_id: ID of the rule to rollback
        api_key: Valid API key (provided via Authorization header)
        
    Returns:
        Dict containing rollback results
    """
    db = next(get_db())
    
    # Find the latest result for this rule
    latest_result = db.query(HardeningResult).filter(
        HardeningResult.rule_id == rule_id
    ).order_by(HardeningResult.timestamp.desc()).first()
    
    if not latest_result:
        raise HTTPException(status_code=404, detail=f"No results found for rule {rule_id}")
    
    if not latest_result.rollback_data:
        raise HTTPException(status_code=400, detail=f"No rollback data available for rule {rule_id}")
    
    try:
        # Find the rule definition for rollback
        rules = rules_module()
        rule_def = None
        for rule in rules:
            if rule["id"] == rule_id:
                rule_def = rule
                break
        
        if not rule_def:
            raise HTTPException(status_code=404, detail=f"Rule definition not found for {rule_id}")
        
        # Execute rollback using agent
        rollback_data = json.loads(latest_result.rollback_data) if latest_result.rollback_data else {}
        rollback_result = policy_engine.rollback_rule(rule_def, rollback_data)
        
        if rollback_result.status == RuleStatus.PASS:
            # Log the rollback
            rollback_log = HardeningResult(
                rule_id=rule_id,
                description=f"ROLLBACK: {latest_result.description}",
                severity=latest_result.severity,
                status="rollback_success",
                old_value=latest_result.new_value,
                new_value=latest_result.old_value,
                rollback_data=json.dumps("")  # Clear rollback data after use
            )
            db.add(rollback_log)
            db.commit()
        
        return {
            "status": "success" if rollback_result.status == RuleStatus.PASS else "error",
            "message": f"Rollback {'successful' if rollback_result.status == RuleStatus.PASS else 'failed'} for rule {rule_id}",
            "rule_id": rule_id,
            "rollback_output": rollback_result.new_value,
            "error": rollback_result.error
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rollback/available")
def get_rollback_options():
    """
    Get list of rules that can be rolled back
    
    Returns rules that have been applied and can be reverted.
    """
    db = next(get_db())
    
    # Get latest results for each rule that has rollback data
    rollback_options = []
    
    # Get unique rule IDs
    unique_rules = db.query(HardeningResult.rule_id).distinct().all()
    
    for (rule_id,) in unique_rules:
        latest = db.query(HardeningResult).filter(
            HardeningResult.rule_id == rule_id
        ).order_by(HardeningResult.timestamp.desc()).first()
        
        if latest and latest.rollback_data and latest.status != "rollback_success":
            rollback_options.append({
                "rule_id": rule_id,
                "description": latest.description,
                "last_applied": latest.timestamp,
                "current_status": latest.status
            })
    
    return {"rollback_options": rollback_options}


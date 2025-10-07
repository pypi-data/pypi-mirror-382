"""
Command Line Interface for OS Forge

Typer-based CLI for running hardening checks and managing the system.
"""

import typer
import uvicorn
from typing import Optional
from pathlib import Path

from database import get_db, HardeningResult
from reporting import ReportGenerator
from agents.linux.linux_agent import LinuxAgent
from agents.windows.windows_agent import WindowsAgent
from agents.common.os_detector import OSDetector
from agents.linux.linux_rules import get_linux_hardening_rules
from agents.windows.windows_rules import get_windows_hardening_rules
from .config import Config


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

# Create CLI app
cli = typer.Typer(help="OS Forge CLI - System Hardening Tool")


@cli.command()
def check(
    level: str = typer.Option("basic", help="Hardening level (basic/moderate/strict)"),
    dry_run: bool = typer.Option(True, help="Dry run mode (no changes)"),
    category: Optional[str] = typer.Option(None, help="Rule category filter")
):
    """Check system against hardening rules"""
    typer.echo(f"Running OS Forge check (Level: {level}, Dry Run: {dry_run})")
    typer.echo(f"Detected OS: {current_os['type']}")
    typer.echo(f"OS Distribution: {current_os.get('distribution', {}).get('name', 'Unknown')}")
    typer.echo(f"Agent Type: {type(policy_engine).__name__}")
    
    rules = rules_module()
    
    # Filter by level
    if level:
        rules = [rule for rule in rules if level in rule.get("level", [])]
    
    # Filter by category
    if category:
        rules = [rule for rule in rules if rule.get("category") == category]
    
    typer.echo(f"Found {len(rules)} applicable rules")
    
    results = []
    for rule in rules:
        try:
            # Check rule first
            check_result = policy_engine.check_rule(rule)
            
            # If dry run, just return the check result
            if dry_run:
                result = {
                    "rule_id": check_result.rule_id,
                    "description": check_result.description,
                    "status": check_result.status.value,
                    "old_value": check_result.old_value,
                    "new_value": check_result.new_value,
                    "error": check_result.error
                }
            else:
                # Apply remediation if not dry run and rule failed
                if check_result.status.value == "fail":
                    remediate_result = policy_engine.remediate_rule(rule, dry_run=False)
                    result = {
                        "rule_id": remediate_result.rule_id,
                        "description": remediate_result.description,
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
                        "status": check_result.status.value,
                        "old_value": check_result.old_value,
                        "new_value": check_result.new_value,
                        "error": check_result.error
                    }
            
            results.append(result)
            
            # Color-coded output
            status_color = {
                "pass": typer.colors.GREEN,
                "fail": typer.colors.RED,
                "error": typer.colors.YELLOW
            }.get(result.get("status"), typer.colors.WHITE)
            
            typer.secho(
                f"  {result['rule_id']}: {result['description']} - {result['status'].upper()}", 
                fg=status_color
            )
            
            if result.get("old_value"):
                typer.echo(f"    Current: {result['old_value']}")
            if result.get("error"):
                typer.echo(f"    Error: {result['error']}")
                
        except Exception as e:
            error_result = {
                "rule_id": rule["id"],
                "description": rule["description"],
                "status": "error",
                "error": str(e)
            }
            results.append(error_result)
            typer.secho(f"  {rule['id']}: {rule['description']} - ERROR", fg=typer.colors.RED)
            typer.echo(f"    Error: {str(e)}")
    
    # Summary
    passed = sum(1 for r in results if r.get("status") == "pass")
    failed = sum(1 for r in results if r.get("status") == "fail")
    errors = sum(1 for r in results if r.get("status") == "error")
    
    typer.echo("\nSummary:")
    typer.secho(f"  Passed: {passed}", fg=typer.colors.GREEN)
    typer.secho(f"  Failed: {failed}", fg=typer.colors.RED)
    typer.secho(f"  Errors: {errors}", fg=typer.colors.YELLOW)


@cli.command()
def server(
    port: int = typer.Option(Config.DEFAULT_PORT, help="Server port"),
    host: str = typer.Option(Config.DEFAULT_HOST, help="Server host")
):
    """Start the FastAPI server"""
    typer.echo(f"Starting OS Forge server on {host}:{port}")
    
    # Import the app here to avoid circular imports
    from .api import app
    uvicorn.run(app, host=host, port=port)


@cli.command()
def report():
    """Generate and display compliance report"""
    typer.echo("Generating compliance report...")
    
    # Simple text report for CLI
    db = next(get_db())
    results = db.query(HardeningResult).order_by(HardeningResult.timestamp.desc()).limit(20).all()
    
    if not results:
        typer.echo("No results found. Run a check first!")
        return
    
    # Calculate summary
    total = len(results)
    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    errors = sum(1 for r in results if r.status == "error")
    score = (passed / total * 100) if total > 0 else 0
    
    typer.echo("\nLatest Compliance Report")
    typer.echo("=" * 50)
    typer.secho(f"Passed: {passed}/{total} ({score:.1f}%)", fg=typer.colors.GREEN)
    typer.secho(f"Failed: {failed}/{total}", fg=typer.colors.RED)
    typer.secho(f"Errors: {errors}/{total}", fg=typer.colors.YELLOW)
    
    typer.echo("\nRecent Results:")
    for result in results[:10]:  # Show latest 10
        status_color = {
            "pass": typer.colors.GREEN,
            "fail": typer.colors.RED,
            "error": typer.colors.YELLOW
        }.get(result.status, typer.colors.WHITE)
        
        typer.secho(
            f"  {result.rule_id}: {result.status.upper()}", 
            fg=status_color
        )
    
    typer.echo(f"\nView full HTML report at: http://localhost:{Config.DEFAULT_PORT}/report")


@cli.command()
def rollback(rule_id: str = typer.Argument(help="Rule ID to rollback")):
    """Rollback a specific hardening rule"""
    typer.echo(f"Rolling back rule: {rule_id}")
    
    try:
        rollback_result = policy_engine.execute_rollback(rule_id)
        
        if rollback_result["status"] == "success":
            typer.secho(f"Successfully rolled back rule {rule_id}", fg=typer.colors.GREEN)
            if rollback_result.get("rollback_output"):
                typer.echo(f"Output: {rollback_result['rollback_output']}")
        else:
            typer.secho(f"Rollback failed for rule {rule_id}", fg=typer.colors.RED)
            if rollback_result.get("error"):
                typer.echo(f"Error: {rollback_result['error']}")
                
    except Exception as e:
        typer.secho(f"Rollback failed: {str(e)}", fg=typer.colors.RED)


@cli.command()
def list_rollbacks():
    """List available rollback options"""
    typer.echo("Available rollback options:")
    
    db = next(get_db())
    
    # Get unique rule IDs
    unique_rules = db.query(HardeningResult.rule_id).distinct().all()
    
    rollback_count = 0
    for (rule_id,) in unique_rules:
        latest = db.query(HardeningResult).filter(
            HardeningResult.rule_id == rule_id
        ).order_by(HardeningResult.timestamp.desc()).first()
        
        if latest and latest.rollback_data and latest.status != "rollback_success":
            typer.echo(f"  {rule_id}: {latest.description}")
            typer.echo(f"    Status: {latest.status}, Applied: {latest.timestamp}")
            rollback_count += 1
    
    if rollback_count == 0:
        typer.echo("No rollback options available")
    else:
        typer.echo(f"\nUse 'os-forge rollback <rule_id>' to rollback a specific rule")


@cli.command()
def pdf_report(output: str = typer.Option("os_forge_report.pdf", help="Output PDF filename")):
    """Generate PDF compliance report"""
    typer.echo(f"Generating PDF report: {output}")
    
    db = next(get_db())
    results = db.query(HardeningResult).order_by(HardeningResult.timestamp.desc()).limit(100).all()
    
    if not results:
        typer.echo("No results found. Run a check first!")
        return
    
    try:
        pdf_buffer = report_generator.generate_pdf_report(results, policy_engine.current_os)
        
        # Write to file
        with open(output, 'wb') as f:
            f.write(pdf_buffer.read())
        
        typer.secho(f"PDF report generated: {output}", fg=typer.colors.GREEN)
        
    except ImportError:
        typer.secho("ReportLab not installed. Install with: pip install reportlab", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Failed to generate PDF: {str(e)}", fg=typer.colors.RED)


@cli.command()
def info():
    """Show system information"""
    typer.echo("OS Forge - System Information")
    typer.echo(f"Detected OS: {current_os['type']}")
    typer.echo(f"OS Distribution: {current_os.get('distribution', {}).get('name', 'Unknown')}")
    typer.echo(f"Agent Type: {type(policy_engine).__name__}")
    
    rules = rules_module()
    typer.echo(f"Total Rules: {len(rules)}")
    
    # Count by level
    level_counts = {}
    for rule in rules:
        for level in rule.get("level", []):
            level_counts[level] = level_counts.get(level, 0) + 1
    
    for level, count in sorted(level_counts.items()):
        typer.echo(f"  {level.title()}: {count} rules")
    
    # Count by category
    category_counts = {}
    for rule in rules:
        category = rule.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    typer.echo("\nRules by Category:")
    for category, count in sorted(category_counts.items()):
        typer.echo(f"  {category}: {count} rules")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()


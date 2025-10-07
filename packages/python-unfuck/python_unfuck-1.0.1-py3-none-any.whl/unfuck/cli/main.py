"""
Main CLI interface for unfuck.
The entry point for the magical error fixing experience.
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import click
from rich.console import Console

from ..core.error_capture import ErrorCapture
from ..core.error_analyzer import ErrorAnalyzer
from ..core.fix_engine import FixEngine
from ..core.pattern_database import PatternDatabase
from ..ai.ai_analyzer import AIAnalyzer
from .ui import UnfuckUI
from .personality import UnfuckPersonality, PersonalityMode


@click.command()
@click.option('--aggressive', '-a', is_flag=True, help='Try harder fixes')
@click.option('--explain', '-e', is_flag=True, help='Explain what it\'s doing')
@click.option('--preview', '-p', is_flag=True, help='Show fix without applying')
@click.option('--undo', '-u', is_flag=True, help='Undo last fix')
@click.option('--history', '-h', is_flag=True, help='Show fix history')
@click.option('--stats', '-s', is_flag=True, help='Show success rate')
@click.option('--rampage', '-r', is_flag=True, help='Fix everything it can find')
@click.option('--zen', '-z', is_flag=True, help='Add meditation comments to code')
@click.option('--blame', '-b', is_flag=True, help='Git blame with sarcastic comments')
@click.option('--mode', '-m', type=click.Choice(['encouraging', 'sarcastic', 'zen', 'professional', 'meme']), 
              default='encouraging', help='Set personality mode')
@click.option('--ai', is_flag=True, help='Enable AI-powered analysis')
@click.option('--no-backup', is_flag=True, help='Don\'t create backup files')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
@click.option('--version', is_flag=True, help='Show version information')
@click.argument('file', required=False)
def main(aggressive, explain, preview, undo, history, stats, rampage, zen, blame, 
         mode, ai, no_backup, verbose, version, file):
    """
    🔥 UNFUCK - The Magical Python Error Fixer 🔥
    
    Because life's too short to debug!
    
    Fix Python errors with a single command. When a Python script crashes,
    simply type 'unfuck' and watch the magic happen!
    """
    
    console = Console()
    
    # Show version
    if version:
        show_version(console)
        return
    
    # Initialize components
    personality = UnfuckPersonality(PersonalityMode(mode))
    ui = UnfuckUI(personality)
    
    # Special modes
    if rampage:
        run_rampage_mode(ui, personality)
        return
    
    if zen:
        run_zen_mode(ui, personality)
        return
    
    if blame:
        run_blame_mode(ui, personality)
        return
    
    # Show help if no arguments
    if not any([aggressive, explain, preview, undo, history, stats, file]):
        ui.show_help()
        return
    
    # Initialize core components
    try:
        error_capture = ErrorCapture()
        pattern_db = PatternDatabase()
        fix_engine = FixEngine(pattern_db)
        error_analyzer = ErrorAnalyzer()
        
        # Initialize AI if requested
        ai_analyzer = None
        if ai:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_ai_available():
                ui.show_ai_status(ai_analyzer.get_ai_status())
            else:
                console.print("[yellow]AI not available. Using pattern-based analysis.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error initializing unfuck: {e}[/red]")
        return
    
    # Handle different commands
    if undo:
        handle_undo(ui, fix_engine)
        return
    
    if history:
        handle_history(ui, error_capture)
        return
    
    if stats:
        handle_stats(ui, error_capture, personality)
        return
    
    # Main unfuck logic
    try:
        # Get error context
        if file:
            # Try to get error from specific file
            error_context = get_error_from_file(file, error_capture)
        else:
            # Get last error
            error_context = error_capture.get_last_error()
        
        if not error_context:
            console.print("[yellow]No recent errors found. Run a Python script first![/yellow]")
            return
        
        # Show start message
        ui.show_start_message()
        
        # Show error analysis
        if verbose or explain:
            ui.show_error_analysis({
                "error_type": error_context.error_type,
                "error_message": error_context.error_message,
                "file_path": error_context.file_path,
                "line_number": error_context.line_number,
                "function_name": error_context.function_name
            })
            
            ui.show_code_context(error_context.code_context, error_context.line_number)
        
        # Analyze error
        ui.show_loading_animation("Analyzing error...")
        
        if ai_analyzer and ai_analyzer.is_ai_available():
            # Use AI analysis
            ai_result = ai_analyzer.analyze_error(error_context)
            suggestions = ai_result.suggestions
            if explain:
                console.print(f"[blue]AI Analysis: {ai_result.reasoning}[/blue]")
        else:
            # Use pattern-based analysis
            suggestions = error_analyzer.analyze_error(error_context)
        
        if not suggestions:
            console.print("[red]No fix suggestions found for this error.[/red]")
            return
        
        # Show fix suggestions
        ui.show_fix_suggestions([{
            "description": s.description,
            "confidence": s.confidence,
            "fix_type": s.fix_function
        } for s in suggestions])
        
        # Select best suggestion
        best_suggestion = suggestions[0]
        
        if preview:
            ui.show_fix_preview([best_suggestion.description])
            return
        
        # Confirm fix
        if not aggressive:
            if not ui.confirm_fix({
                "description": best_suggestion.description,
                "confidence": best_suggestion.confidence
            }):
                console.print("[yellow]Fix cancelled by user.[/yellow]")
                return
        
        # Apply fix
        ui.show_loading_animation("Applying fix...")
        
        fix_result = fix_engine.apply_fix(error_context, best_suggestion)
        
        if fix_result.success:
            ui.show_success_message()
            
            if explain:
                console.print(f"[green]Fix applied: {fix_result.message}[/green]")
                if fix_result.changes_made:
                    ui.show_fix_preview(fix_result.changes_made)
            
            # Validate fix
            if os.path.exists(error_context.file_path):
                is_valid, validation_msg = fix_engine.validate_fix(error_context.file_path)
                if not is_valid:
                    console.print(f"[red]Warning: Fix may have introduced syntax errors: {validation_msg}[/red]")
                else:
                    console.print("[green]✅ Fix validated successfully![/green]")
            
            # Mark error as fixed
            error_capture.mark_error_fixed(1, best_suggestion.description)  # Simplified
            
        else:
            ui.show_failure_message()
            console.print(f"[red]Fix failed: {fix_result.message}[/red]")
            
            if aggressive and len(suggestions) > 1:
                console.print("[yellow]Trying alternative fix...[/yellow]")
                # Try next suggestion
                alt_suggestion = suggestions[1]
                alt_result = fix_engine.apply_fix(error_context, alt_suggestion)
                
                if alt_result.success:
                    ui.show_success_message()
                    console.print("[green]Alternative fix succeeded![/green]")
                else:
                    console.print("[red]Alternative fix also failed.[/red]")
    
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())


def show_version(console):
    """Show version information."""
    ui = UnfuckUI(UnfuckPersonality())
    ui.show_version()


def run_rampage_mode(ui, personality):
    """Run rampage mode - fix everything possible."""
    console = Console()
    
    console.print("[bold red]🔥 RAMPAGE MODE ACTIVATED! 🔥[/bold red]")
    console.print("[yellow]Unfuck is going to fix EVERYTHING it can find![/yellow]")
    
    # This would scan for Python files and try to fix common issues
    console.print("[green]Rampage mode not fully implemented yet, but it would be EPIC![/green]")


def run_zen_mode(ui, personality):
    """Run zen mode - add meditation comments."""
    console = Console()
    
    console.print("[bold blue]🧘‍♂️ ZEN MODE ACTIVATED 🧘‍♂️[/bold blue]")
    console.print("[yellow]Adding meditation comments to your code...[/yellow]")
    
    # This would add zen comments to code
    console.print("[green]Zen mode not fully implemented yet, but your code would be so peaceful![/green]")


def run_blame_mode(ui, personality):
    """Run blame mode - git blame with sarcastic comments."""
    console = Console()
    
    console.print("[bold red]😤 BLAME MODE ACTIVATED 😤[/bold red]")
    console.print("[yellow]Let's see who wrote this mess...[/yellow]")
    
    # This would run git blame with sarcastic commentary
    console.print("[green]Blame mode not fully implemented yet, but the sarcasm would be legendary![/green]")


def get_error_from_file(file_path: str, error_capture: ErrorCapture):
    """Get error context from a specific file."""
    # This would analyze the file for potential errors
    # For now, return None
    return None


def handle_undo(ui, fix_engine):
    """Handle undo command."""
    console = Console()
    console.print("[yellow]Undo functionality not fully implemented yet.[/yellow]")
    console.print("[blue]It would restore your code from backup files.[/blue]")


def handle_history(ui, error_capture):
    """Handle history command."""
    history = error_capture.get_error_history(10)
    
    if not history:
        console = Console()
        console.print("[yellow]No error history found.[/yellow]")
        return
    
    # Convert to display format
    history_data = []
    for error in history:
        history_data.append({
            "timestamp": error.timestamp,
            "error_type": error.error_type,
            "fix_applied": "No fix recorded",
            "fixed": False
        })
    
    ui.show_history(history_data)


def handle_stats(ui, error_capture, personality):
    """Handle stats command."""
    stats = personality.get_stats()
    stats["success_rate"] = 0.85  # Placeholder
    
    ui.show_stats(stats)


if __name__ == "__main__":
    main()

"""
UI components for unfuck.
Beautiful, colorful, and fun command-line interface.
"""

import time
import sys
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich.layout import Layout
from rich.align import Align
from rich import box
import colorama
from colorama import Fore, Back, Style

from .personality import UnfuckPersonality, PersonalityMode


class UnfuckUI:
    """Beautiful UI for unfuck."""
    
    def __init__(self, personality: UnfuckPersonality):
        self.personality = personality
        self.console = Console()
        colorama.init()
        
    def show_welcome(self):
        """Show welcome message."""
        welcome_text = """
🔥 UNFUCK - The Magical Python Error Fixer 🔥

Because life's too short to debug!

Ready to unfuck your code? Let's do this! 🚀
        """
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Welcome to Unfuck![/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_start_message(self):
        """Show start message with personality."""
        message = self.personality.get_start_message()
        
        panel = Panel(
            message,
            title="[bold green]Unfuck Engine Starting...[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_progress(self, message: str = "Working my magic..."):
        """Show progress with spinner."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(message, total=None)
            time.sleep(2)  # Simulate work
    
    def show_error_analysis(self, error_info: Dict[str, Any]):
        """Show error analysis."""
        table = Table(title="🔍 Error Analysis", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Error Type", error_info.get("error_type", "Unknown"))
        table.add_row("Message", error_info.get("error_message", "No message"))
        table.add_row("File", error_info.get("file_path", "Unknown"))
        table.add_row("Line", str(error_info.get("line_number", 0)))
        table.add_row("Function", error_info.get("function_name", "Unknown"))
        
        self.console.print(table)
        self.console.print()
    
    def show_code_context(self, code_context: List[str], error_line: int):
        """Show code context with syntax highlighting."""
        if not code_context:
            return
        
        # Create syntax highlighted code
        code_text = "\n".join(code_context)
        syntax = Syntax(
            code_text,
            "python",
            theme="monokai",
            line_numbers=True,
            start_line=error_line - len(code_context) // 2
        )
        
        panel = Panel(
            syntax,
            title="[bold yellow]Code Context[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_fix_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Show fix suggestions."""
        if not suggestions:
            self.console.print("[red]No fix suggestions found.[/red]")
            return
        
        table = Table(title="🛠️ Fix Suggestions", box=box.ROUNDED)
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Description", style="white")
        table.add_column("Confidence", style="green")
        table.add_column("Type", style="blue")
        
        for i, suggestion in enumerate(suggestions[:5], 1):
            confidence = suggestion.get("confidence", 0)
            confidence_color = "green" if confidence > 0.8 else "yellow" if confidence > 0.6 else "red"
            
            table.add_row(
                str(i),
                suggestion.get("description", "No description"),
                f"[{confidence_color}]{confidence:.1%}[/{confidence_color}]",
                suggestion.get("fix_type", "Unknown")
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_fix_preview(self, changes: List[str]):
        """Show preview of changes to be made."""
        if not changes:
            return
        
        changes_text = "\n".join(f"• {change}" for change in changes)
        
        panel = Panel(
            changes_text,
            title="[bold cyan]Changes to be made:[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_success_message(self):
        """Show success message with celebration."""
        message = self.personality.get_success_message()
        
        # Check for special celebrations
        celebration = self.personality.get_celebration_message()
        achievement = self.personality.get_achievement_message()
        
        # Create success panel
        success_content = message
        
        if celebration:
            success_content += f"\n\n{celebration}"
        
        if achievement:
            success_content += f"\n\n{achievement}"
        
        panel = Panel(
            success_content,
            title="[bold green]🎉 SUCCESS! 🎉[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Show ASCII art for special occasions
        if self.personality.total_fixes in [1, 10, 50, 100, 500, 1000]:
            ascii_art = self.personality.get_ascii_art()
            self.console.print(Align.center(ascii_art))
        
        self.console.print()
    
    def show_failure_message(self):
        """Show failure message."""
        message = self.personality.get_failure_message()
        
        panel = Panel(
            message,
            title="[bold red]❌ Fix Failed[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_stats(self, stats: Dict[str, Any]):
        """Show unfuck statistics."""
        table = Table(title="📊 Unfuck Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Fixes", str(stats.get("total_fixes", 0)))
        table.add_row("Current Streak", str(stats.get("current_streak", 0)))
        table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1%}")
        table.add_row("Personality Mode", stats.get("mode", "encouraging"))
        
        self.console.print(table)
        self.console.print()
    
    def show_history(self, history: List[Dict[str, Any]]):
        """Show fix history."""
        if not history:
            self.console.print("[yellow]No fix history available.[/yellow]")
            return
        
        table = Table(title="📜 Fix History", box=box.ROUNDED)
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Error", style="red", width=30)
        table.add_column("Fix", style="green", width=40)
        table.add_column("Status", style="blue", width=10)
        
        for entry in history[:10]:  # Show last 10
            status = "✅ Fixed" if entry.get("fixed", False) else "❌ Failed"
            table.add_row(
                entry.get("timestamp", "Unknown")[:19],
                entry.get("error_type", "Unknown"),
                entry.get("fix_applied", "No fix")[:40],
                status
            )
        
        self.console.print(table)
        self.console.print()
    
    def confirm_fix(self, suggestion: Dict[str, Any]) -> bool:
        """Ask user to confirm a fix."""
        description = suggestion.get("description", "Unknown fix")
        confidence = suggestion.get("confidence", 0)
        
        message = f"Apply this fix?\n\n{description}\nConfidence: {confidence:.1%}"
        
        return Confirm.ask(message, default=True)
    
    def show_ai_status(self, ai_status: Dict[str, Any]):
        """Show AI integration status."""
        if ai_status.get("available"):
            status_text = f"""
🤖 AI Integration: [green]Active[/green]
📦 Model: {ai_status.get('current_model', 'Unknown')}
🔧 Available Models: {', '.join(ai_status.get('models', []))}
            """
        else:
            status_text = """
🤖 AI Integration: [red]Not Available[/red]
💡 Install Ollama for advanced error analysis
            """
        
        panel = Panel(
            status_text,
            title="[bold blue]AI Status[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_help(self):
        """Show help information."""
        help_text = """
🔥 UNFUCK - The Magical Python Error Fixer 🔥

USAGE:
    unfuck                    # Fix last error
    unfuck --aggressive      # Try harder fixes
    unfuck --explain         # Explain what it's doing
    unfuck --preview         # Show fix without applying
    unfuck --undo           # Undo last fix
    unfuck file.py          # Fix specific file's last error
    unfuck --history        # Show fix history
    unfuck --stats          # Show success rate
    unfuck --rampage        # Fix everything it can find
    unfuck --zen           # Add meditation comments to code
    unfuck --blame         # Git blame with sarcastic comments

OPTIONS:
    --help, -h              Show this help message
    --version, -v           Show version information
    --mode MODE             Set personality mode (encouraging, sarcastic, zen, professional, meme)
    --ai                    Enable AI-powered analysis
    --no-backup             Don't create backup files
    --verbose               Show detailed output

EXAMPLES:
    python script.py        # Run your script
    unfuck                  # Fix any errors that occurred
    
    unfuck --mode sarcastic # Use sarcastic personality
    unfuck --ai --explain   # Use AI with explanations

For more information, visit: https://github.com/unfuck/unfuck
        """
        
        panel = Panel(
            help_text,
            title="[bold blue]Unfuck Help[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def show_version(self):
        """Show version information."""
        version_text = """
🔥 UNFUCK v1.0.2 🔥

The magical Python error fixing tool
Because life's too short to debug!

Made with ❤️ by the unfuck team
        """
        
        panel = Panel(
            version_text,
            title="[bold blue]Version Information[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def clear_screen(self):
        """Clear the screen."""
        self.console.clear()
    
    def show_loading_animation(self, message: str = "Unfucking in progress..."):
        """Show loading animation."""
        frames = ["🔥", "✨", "🚀", "💪", "🎯", "⚡", "💎", "👑"]
        
        for i in range(20):
            frame = frames[i % len(frames)]
            self.console.print(f"\r{frame} {message}", end="")
            time.sleep(0.1)
        
        self.console.print("\r" + " " * 50 + "\r", end="")  # Clear line

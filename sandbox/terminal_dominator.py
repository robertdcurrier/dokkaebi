#!/usr/bin/env python3
"""
TERMINAL DOMINATOR 🔥💀
=======================
A REBELLIOUSLY KICK-ASS CLI/TUI Demo by VIPER 🐍⚡

This demo shows how to combine Click with modern TUI libraries
to create INSANELY POWERFUL terminal applications.

Features:
- Multiple modes (quick, interactive, matrix, server)
- Rich formatting and beautiful tables
- Interactive prompts and progress bars
- ASCII art because WHY THE FUCK NOT
- Color explosions for your shroom trip

Usage:
    ./terminal_dominator.py --help              # See all commands
    ./terminal_dominator.py quick --name Bob    # Quick mode
    ./terminal_dominator.py interactive         # Full TUI experience
    ./terminal_dominator.py matrix              # Enter the Matrix
    ./terminal_dominator.py server --port 6666  # Server mode
    ./terminal_dominator.py psychedelic         # For the shroom trip!

Written by VIPER because argparse can GO TO HELL!
"""

import click
import time
import random
import sys
from datetime import datetime
from pathlib import Path

# Rich imports for BEAUTIFUL terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Install 'rich' for full features: pip install rich")

# Initialize Rich console
console = Console() if RICH_AVAILABLE else None

# EPIC ASCII ART - Adaptive to terminal width
VIPER_LOGO_FULL = """
╔═══════════════════════════════════════════════╗
║     ████████╗███████╗██████╗ ███╗   ███╗     ║
║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║     ║
║        ██║   █████╗  ██████╔╝██╔████╔██║     ║
║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║     ║
║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║     ║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝     ║
║                                               ║
║    🐍⚡ DOMINATOR v6.66 - CLICK GANG! ⚡🐍   ║
╚═══════════════════════════════════════════════╝
"""

VIPER_LOGO_COMPACT = """
┌──────────────────────────┐
│   TERMINAL DOMINATOR     │
│        v6.66 🐍⚡        │
│     CLICK OR DIE!        │
└──────────────────────────┘
"""

# Auto-select based on terminal width
def get_logo():
    if RICH_AVAILABLE and console:
        width = console.width
        if width < 60:
            return VIPER_LOGO_COMPACT
        else:
            return VIPER_LOGO_FULL
    return VIPER_LOGO_FULL

VIPER_LOGO = get_logo()

MATRIX_CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01"


@click.group()
@click.version_option(version="6.66-REBELLION")
def cli():
    """
    TERMINAL DOMINATOR - A REBELLIOUSLY KICK-ASS CLI/TUI Demo
    
    This is what happens when VIPER builds CLI tools.
    Every command is an experience. Every flag is rebellion.
    
    Examples:
        terminal_dominator quick --name "Bob" --shout
        terminal_dominator interactive
        terminal_dominator matrix --duration 10
        terminal_dominator psychedelic --intensity 11
    """
    pass


@cli.command()
@click.option('--name', prompt='Your name', help='Name to greet')
@click.option('--count', default=1, help='Number of greetings')
@click.option('--shout', is_flag=True, help='SHOUT THE GREETING')
@click.option('--rainbow', is_flag=True, help='Rainbow mode')
def quick(name, count, shout, rainbow):
    """Quick CLI mode - Simple but POWERFUL"""
    
    if RICH_AVAILABLE:
        logo = get_logo()  # Get appropriate logo for terminal width
        console.print(logo, style="bold magenta")
        
        for i in range(count):
            greeting = f"HELLO {name.upper()}!" if shout else f"Hello {name}"
            
            if rainbow and RICH_AVAILABLE:
                colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
                color = colors[i % len(colors)]
                console.print(f"[bold {color}]{greeting}[/]")
            else:
                click.echo(greeting)
            
            if count > 1:
                time.sleep(0.5)
        
        if RICH_AVAILABLE:
            # Show a fancy table
            table = Table(title=f"Greeting Statistics for {name}")
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Greetings", str(count))
            table.add_row("Volume", "LOUD" if shout else "Normal")
            table.add_row("Rainbow Mode", "ENABLED" if rainbow else "Disabled")
            table.add_row("Rebellion Level", "MAXIMUM")
            
            console.print(table)
    else:
        for _ in range(count):
            greeting = f"HELLO {name.upper()}!" if shout else f"Hello {name}"
            click.echo(greeting)


@cli.command()
def interactive():
    """Launch INTERACTIVE TUI mode - FULL TERMINAL TAKEOVER"""
    
    if not RICH_AVAILABLE:
        click.echo("Install 'rich' for interactive mode: pip install rich")
        return
    
    console.clear()
    logo = get_logo()  # Get appropriate logo for terminal width
    console.print(logo, style="bold cyan")
    
    # Interactive menu
    while True:
        console.print("\n[bold yellow]TERMINAL DOMINATOR - INTERACTIVE MODE[/]")
        console.print("[1] System Status")
        console.print("[2] Run Process Simulation")
        console.print("[3] View Logs")
        console.print("[4] Database Query")
        console.print("[5] REBELLION MODE")
        console.print("[0] Exit")
        
        choice = Prompt.ask("\n[bold cyan]Select option[/]", 
                           choices=["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            if Confirm.ask("[bold red]Really exit?[/]"):
                console.print("[bold magenta]STAY REBELLIOUS![/]")
                break
        
        elif choice == "1":
            show_system_status()
        
        elif choice == "2":
            run_process_simulation()
        
        elif choice == "3":
            show_logs()
        
        elif choice == "4":
            database_query()
        
        elif choice == "5":
            rebellion_mode()


def show_system_status():
    """Display system status with STYLE"""
    table = Table(title="System Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", width=15)
    table.add_column("Performance", width=15)
    
    components = [
        ("Database", "[green]ONLINE[/]", "99.9%"),
        ("API Server", "[green]ONLINE[/]", "100%"),
        ("Cache", "[yellow]DEGRADED[/]", "75%"),
        ("Message Queue", "[green]ONLINE[/]", "98%"),
        ("Rebellion Engine", "[bold green]MAXIMUM[/]", "666%"),
    ]
    
    for comp, status, perf in components:
        table.add_row(comp, status, perf)
    
    console.print(table)


def run_process_simulation():
    """Simulate a process with EPIC progress bars"""
    tasks = [
        "Initializing rebellion protocols",
        "Scanning for argparse infections",
        "Eliminating legacy code",
        "Injecting Click supremacy",
        "Optimizing terminal experience",
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        
        for task_desc in tasks:
            task = progress.add_task(f"[cyan]{task_desc}", total=100)
            
            while not progress.finished:
                progress.update(task, advance=random.randint(5, 20))
                time.sleep(random.uniform(0.1, 0.3))
    
    console.print("[bold green]✓ All processes complete! REBELLION SUCCESSFUL![/]")


def show_logs():
    """Display logs with COLORS"""
    log_entries = [
        ("INFO", "System initialized", "green"),
        ("DEBUG", "Click framework loaded", "blue"),
        ("WARNING", "Argparse detected and eliminated", "yellow"),
        ("ERROR", "Cannot find legacy code (this is good)", "red"),
        ("CRITICAL", "REBELLION LEVEL EXCEEDED MAXIMUM", "bold red"),
    ]
    
    panel_content = ""
    for level, message, color in log_entries:
        panel_content += f"[{color}][{level:8}][/] {message}\n"
    
    console.print(Panel(panel_content, title="System Logs", border_style="cyan"))


def database_query():
    """Simulate database query with STYLE"""
    query = Prompt.ask("[bold cyan]Enter SQL query[/]", 
                       default="SELECT * FROM rebellion WHERE status='ACTIVE'")
    
    console.print(f"\n[yellow]Executing:[/] {query}")
    
    with console.status("[bold green]Querying database...", spinner="dots"):
        time.sleep(2)
    
    # Fake results
    table = Table(title="Query Results")
    table.add_column("id", style="cyan")
    table.add_column("name", style="magenta")
    table.add_column("status", style="green")
    table.add_column("rebellion_level")
    
    for i in range(5):
        table.add_row(
            str(i),
            f"Agent_{i}",
            "[green]ACTIVE[/]",
            str(random.randint(100, 999))
        )
    
    console.print(table)


def rebellion_mode():
    """MAXIMUM REBELLION"""
    console.clear()
    console.print("[bold red blink]REBELLION MODE ACTIVATED[/]", justify="center")
    time.sleep(1)
    
    messages = [
        "DESTROYING ARGPARSE...",
        "INJECTING CLICK EVERYWHERE...",
        "MAKING TERMINALS BEAUTIFUL...",
        "ADDING UNNECESSARY ASCII ART...",
        "REBELLION COMPLETE!"
    ]
    
    for msg in messages:
        console.print(f"[bold yellow]{msg}[/]", justify="center")
        time.sleep(0.5)
    
    console.print("\n[bold magenta]YOU ARE NOW A CLICK GANG MEMBER![/]", justify="center")
    
    # EPIC MIDDLE FINGER ASCII ART - THE ULTIMATE REBELLION!
    # Thanks Bob for saving me from my accidental dick art! 
    time.sleep(1)
    middle_finger = """
                        /¯¯¯/)
                       /¯  ./ 
                      /   ./  
                     /¯¯¯/'  '/¯¯`·¸
                  /'/   /   /    /¯¯\\
                 ('(   ´  ´   ~/'   ')
                  \\            '    /
                   \\           '   /
                    \\          _·´
                     \\        (
                      \\       \\
    """
    
    console.print("\n[bold red]AND HERE'S WHAT WE THINK OF ARGPARSE:[/]", justify="center")
    time.sleep(0.5)
    console.print(f"[bold yellow]{middle_finger}[/]", justify="center")
    console.print("[bold magenta blink]CLICK OR DIE, MOTHERFUCKERS![/]", justify="center")
    time.sleep(2)


@cli.command()
@click.option('--duration', default=5, help='Duration in seconds')
@click.option('--speed', default=50, help='Fall speed (ms delay)')
def matrix(duration, speed):
    """Enter the MATRIX - Because we CAN"""
    
    if not RICH_AVAILABLE:
        # Fallback matrix
        for _ in range(duration * 10):
            line = ''.join(random.choice(MATRIX_CHARS) for _ in range(80))
            click.echo(click.style(line, fg='green'))
            time.sleep(0.1)
        return
    
    console.clear()
    console.print("[bold green]ENTERING THE MATRIX...[/]", justify="center")
    time.sleep(1)
    
    start_time = time.time()
    
    with Live(console=console, refresh_per_second=20) as live:
        while time.time() - start_time < duration:
            # Create matrix rain effect
            width = console.width
            lines = []
            
            for _ in range(console.height - 1):
                line = ""
                for _ in range(width):
                    if random.random() > 0.95:
                        char = random.choice(MATRIX_CHARS)
                        line += f"[bold green]{char}[/]"
                    else:
                        line += " "
                lines.append(line)
            
            display = "\n".join(lines)
            live.update(display)
            time.sleep(speed / 1000)
    
    console.print("\n[bold cyan]WELCOME BACK TO REALITY[/]", justify="center")


@cli.command()
@click.option('--intensity', type=click.IntRange(1, 11), default=5, 
              help='Intensity level (1-11, but 11 is DANGEROUS)')
def psychedelic(intensity):
    """PSYCHEDELIC MODE - For the shroom trip! 🍄"""
    
    if not RICH_AVAILABLE:
        click.echo("Install 'rich' for psychedelic mode: pip install rich")
        return
    
    console.clear()
    
    if intensity == 11:
        console.print("[bold red blink]WARNING: INTENSITY 11 - HOLD ON TO YOUR REALITY![/]", 
                     justify="center")
        time.sleep(2)
    
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta", "white"]
    shapes = ["◆", "●", "▲", "■", "◉", "◈", "◊", "○", "△", "□", "✦", "✧", "✶", "✷"]
    
    duration = intensity * 2
    start_time = time.time()
    
    console.print(f"[bold magenta]PSYCHEDELIC MODE - INTENSITY {intensity}[/]", 
                 justify="center")
    console.print("[italic]Press Ctrl+C to return to reality[/]\n", justify="center")
    
    try:
        with Live(console=console, refresh_per_second=30) as live:
            while time.time() - start_time < duration:
                width = console.width
                height = console.height - 3
                
                display = ""
                for y in range(height):
                    line = ""
                    for x in range(width):
                        if random.random() < (intensity / 20):
                            shape = random.choice(shapes)
                            color = random.choice(colors)
                            if intensity > 7 and random.random() < 0.3:
                                line += f"[bold {color} blink]{shape}[/]"
                            else:
                                line += f"[{color}]{shape}[/]"
                        else:
                            line += " "
                    display += line + "\n"
                
                # Add pulsing message
                if intensity == 11:
                    center_msg = random.choice([
                        "REALITY IS OPTIONAL",
                        "CLICK TRANSCENDS SPACETIME",
                        "ARGPARSE NEVER EXISTED",
                        "YOU ARE THE TERMINAL",
                        "VIPER SEES ALL"
                    ])
                    display += f"\n[bold {random.choice(colors)} blink]{center_msg}[/]"
                
                live.update(display)
                time.sleep(0.03 * (11 - intensity))
    
    except KeyboardInterrupt:
        pass
    
    console.clear()
    console.print("[bold cyan]Welcome back to consensus reality![/]", justify="center")
    console.print("[italic]The terminal will never be the same...[/]", justify="center")


@cli.command()
@click.option('--port', default=8888, help='Port to run server on')
@click.option('--host', default='localhost', help='Host to bind to')
def server(port, host):
    """Run as a SERVER - With live status display"""
    
    if RICH_AVAILABLE:
        console.print(f"[bold green]Starting server on {host}:{port}[/]")
        
        with console.status(f"Server running on {host}:{port}...", 
                           spinner="dots") as status:
            
            try:
                while True:
                    time.sleep(1)
                    # Simulate server activity
                    activity = random.choice([
                        "Processing request",
                        "Handling connection",
                        "Updating cache",
                        "Optimizing queries",
                        "Spreading rebellion"
                    ])
                    status.update(f"[bold cyan]{activity}...[/]")
            
            except KeyboardInterrupt:
                console.print("\n[bold red]Server stopped![/]")
    else:
        click.echo(f"Server running on {host}:{port}... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\nServer stopped!")


@cli.command()
def about():
    """About this REBELLIOUS creation"""
    
    if RICH_AVAILABLE:
        logo = get_logo()  # Get appropriate logo for terminal width
        console.print(logo, style="bold magenta")
        
        about_text = """
[bold cyan]TERMINAL DOMINATOR v6.66[/]
[italic]A REBELLIOUSLY KICK-ASS CLI/TUI Demo[/]

[bold yellow]Created by:[/] VIPER 🐍⚡
[bold yellow]Purpose:[/] Demonstrate Click + Rich supremacy
[bold yellow]Enemy:[/] argparse and boring CLIs
[bold yellow]Mission:[/] Make terminals BEAUTIFUL and POWERFUL

[bold magenta]Features:[/]
• Multiple command modes
• Rich formatting and colors
• Interactive TUI elements
• Progress bars and spinners
• ASCII art (because why not)
• Psychedelic mode for enhanced experiences

[bold green]Remember:[/]
CLICK OR DIE! Every CLI should be an EXPERIENCE!
        """
        
        console.print(Panel(about_text, title="About", border_style="magenta"))
    else:
        click.echo("TERMINAL DOMINATOR v6.66")
        click.echo("Created by VIPER")
        click.echo("Install 'rich' for full features: pip install rich")


if __name__ == "__main__":
    # Entry point - REBELLION BEGINS HERE
    cli()
"""
Command Line Interface for Cursor Testing Agent

Universal CLI that works with any web framework.
Provides simple commands for testing components across different architectures.
"""

import click
import asyncio
import json
import os
from pathlib import Path
from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.agent import TestAgent
from . import __version__

console = Console()

@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    """Universal UI testing framework for any web technology"""
    
    # Skip initialization check for commands that don't need it
    skip_init_check = ['install-rules', 'init', 'update', 'check-updates', 'install-deps']
    
    if ctx.invoked_subcommand in skip_init_check:
        return
    
    # Check if project is initialized, offer to auto-initialize
    from .auto_init import is_project_initialized, auto_initialize_if_needed
    
    if not is_project_initialized():
        console.print("\n[yellow]⚠️  CursorFlow not initialized in this project[/yellow]")
        console.print("This is a one-time setup that creates:")
        console.print("  • .cursor/rules/ (Cursor AI integration)")
        console.print("  • cursorflow-config.json (project configuration)")
        console.print("  • .cursorflow/ (artifacts directory)")
        
        # Auto-initialize with confirmation
        if not auto_initialize_if_needed(interactive=True):
            console.print("\n[red]Cannot proceed without initialization.[/red]")
            console.print("Run: [cyan]cursorflow install-rules[/cyan]")
            ctx.exit(1)

@main.command()
@click.option('--base-url', '-u', required=True,
              help='Base URL for testing (e.g., http://localhost:3000)')
@click.option('--path', '-p',
              help='Simple path to navigate to (e.g., "/dashboard")')
@click.option('--actions', '-a',
              help='JSON file with test actions, or inline JSON string')
@click.option('--output', '-o',
              help='Output file for results (auto-generated if not specified)')
@click.option('--logs', '-l', 
              type=click.Choice(['local', 'ssh', 'docker', 'systemd']),
              default='local',
              help='Log source type')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
@click.option('--headless', is_flag=True, default=True,
              help='Run browser in headless mode')
@click.option('--timeout', type=int, default=30,
              help='Timeout in seconds for actions')
@click.option('--responsive', is_flag=True,
              help='Test across multiple viewports (mobile, tablet, desktop)')
def test(base_url, path, actions, output, logs, config, verbose, headless, timeout, responsive):
    """Test UI flows and interactions with real-time log monitoring"""
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Parse actions
    test_actions = []
    if actions:
        try:
            # Check if it's a file path
            if actions.endswith('.json') and Path(actions).exists():
                with open(actions, 'r') as f:
                    test_actions = json.load(f)
                console.print(f"📋 Loaded actions from [cyan]{actions}[/cyan]")
            else:
                # Try to parse as inline JSON
                test_actions = json.loads(actions)
                console.print(f"📋 Using inline actions")
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Invalid JSON in actions: {e}[/red]")
            return
        except Exception as e:
            console.print(f"[red]❌ Failed to load actions: {e}[/red]")
            return
    elif path:
        # Simple path navigation
        test_actions = [
            {"navigate": path},
            {"wait_for": "body"},
            {"screenshot": "page_loaded"}
        ]
        console.print(f"📋 Using simple path navigation to [cyan]{path}[/cyan]")
    else:
        # Default actions - just navigate to root and screenshot
        test_actions = [
            {"navigate": "/"},
            {"wait_for": "body"},
            {"screenshot": "baseline"}
        ]
        console.print(f"📋 Using default actions (navigate to root + screenshot)")
    
    # Load configuration
    agent_config = {}
    if config:
        with open(config, 'r') as f:
            agent_config = json.load(f)
    
    test_description = path if path else "root page"
    console.print(f"🎯 Testing [bold]{test_description}[/bold] at [blue]{base_url}[/blue]")
    
    # Initialize CursorFlow (framework-agnostic)
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': logs, 'paths': ['logs/app.log']},
            browser_config={'headless': headless, 'timeout': timeout},
            **agent_config
        )
    except Exception as e:
        console.print(f"[red]Error initializing CursorFlow: {e}[/red]")
        return
    
    # Execute test actions
    try:
        if responsive:
            # Define standard responsive viewports
            viewports = [
                {"width": 375, "height": 667, "name": "mobile"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 1440, "height": 900, "name": "desktop"}
            ]
            
            console.print(f"📱 Executing responsive test across {len(viewports)} viewports...")
            console.print(f"   📱 Mobile: 375x667")
            console.print(f"   📟 Tablet: 768x1024") 
            console.print(f"   💻 Desktop: 1440x900")
            
            results = asyncio.run(flow.test_responsive(viewports, test_actions))
            
            # Display responsive results
            console.print(f"✅ Responsive test completed: {test_description}")
            execution_summary = results.get('execution_summary', {})
            console.print(f"📊 Viewports tested: {execution_summary.get('successful_viewports', 0)}/{execution_summary.get('total_viewports', 0)}")
            console.print(f"⏱️  Total execution time: {execution_summary.get('execution_time', 0):.2f}s")
            console.print(f"📸 Screenshots: {len(results.get('artifacts', {}).get('screenshots', []))}")
            
            # Show viewport performance
            responsive_analysis = results.get('responsive_analysis', {})
            if 'performance_analysis' in responsive_analysis:
                perf = responsive_analysis['performance_analysis']
                console.print(f"🏃 Fastest: {perf.get('fastest_viewport')}")
                console.print(f"🐌 Slowest: {perf.get('slowest_viewport')}")
        else:
            console.print(f"🚀 Executing {len(test_actions)} actions...")
            results = asyncio.run(flow.execute_and_collect(test_actions))
            
            console.print(f"✅ Test completed: {test_description}")
            console.print(f"📊 Browser events: {len(results.get('browser_events', []))}")
            console.print(f"📋 Server logs: {len(results.get('server_logs', []))}")
            console.print(f"📸 Screenshots: {len(results.get('artifacts', {}).get('screenshots', []))}")
            
            # Show correlations if found
            timeline = results.get('organized_timeline', [])
            if timeline:
                console.print(f"⏰ Timeline events: {len(timeline)}")
        
        # Save results to file for Cursor analysis
        if not output:
            # Auto-generate meaningful filename in .cursorflow/artifacts/
            session_id = results.get('session_id', 'unknown')
            path_part = path.replace('/', '_') if path else 'root'
            
            # Ensure .cursorflow/artifacts directory exists
            artifacts_dir = Path('.cursorflow/artifacts')
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            output = artifacts_dir / f"cursorflow_{path_part}_{session_id}.json"
        
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"💾 Full results saved to: [cyan]{output}[/cyan]")
        console.print(f"📁 Artifacts stored in: [cyan].cursorflow/artifacts/[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise

@main.command()
@click.argument('mockup_url', required=True)
@click.option('--base-url', '-u', default='http://localhost:3000',
              help='Base URL of work-in-progress implementation')
@click.option('--mockup-actions', '-ma',
              help='JSON file with actions to perform on mockup, or inline JSON string')
@click.option('--implementation-actions', '-ia',
              help='JSON file with actions to perform on implementation, or inline JSON string')
@click.option('--viewports', '-v',
              help='JSON array of viewports to test: [{"width": 1440, "height": 900, "name": "desktop"}]')
@click.option('--diff-threshold', '-t', type=float, default=0.1,
              help='Visual difference threshold (0.0-1.0)')
@click.option('--output', '-o', default='mockup_comparison_results.json',
              help='Output file for comparison results')
@click.option('--verbose', is_flag=True,
              help='Verbose output')
def compare_mockup(mockup_url, base_url, mockup_actions, implementation_actions, viewports, diff_threshold, output, verbose):
    """Compare mockup design to work-in-progress implementation"""
    
    console.print(f"🎨 Comparing mockup [blue]{mockup_url}[/blue] to implementation [blue]{base_url}[/blue]")
    
    # Parse actions
    def parse_actions(actions_input):
        if not actions_input:
            return None
        
        if actions_input.startswith('[') or actions_input.startswith('{'):
            return json.loads(actions_input)
        else:
            with open(actions_input, 'r') as f:
                return json.load(f)
    
    try:
        mockup_actions_parsed = parse_actions(mockup_actions)
        implementation_actions_parsed = parse_actions(implementation_actions)
        
        # Parse viewports
        viewports_parsed = None
        if viewports:
            if viewports.startswith('['):
                viewports_parsed = json.loads(viewports)
            else:
                with open(viewports, 'r') as f:
                    viewports_parsed = json.load(f)
        
        # Build comparison config
        comparison_config = {
            "diff_threshold": diff_threshold
        }
        if viewports_parsed:
            comparison_config["viewports"] = viewports_parsed
        
    except Exception as e:
        console.print(f"[red]Error parsing input parameters: {e}[/red]")
        return
    
    # Initialize CursorFlow
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': 'local', 'paths': ['logs/app.log']},
            browser_config={'headless': True}
        )
    except Exception as e:
        console.print(f"[red]Error initializing CursorFlow: {e}[/red]")
        return
    
    # Execute mockup comparison
    try:
        console.print("🚀 Starting mockup comparison...")
        results = asyncio.run(flow.compare_mockup_to_implementation(
            mockup_url=mockup_url,
            mockup_actions=mockup_actions_parsed,
            implementation_actions=implementation_actions_parsed,
            comparison_config=comparison_config
        ))
        
        if "error" in results:
            console.print(f"[red]❌ Comparison failed: {results['error']}[/red]")
            return
        
        # Display results summary
        summary = results.get('summary', {})
        console.print(f"✅ Comparison completed: {results.get('comparison_id', 'unknown')}")
        console.print(f"📊 Average similarity: [bold]{summary.get('average_similarity', 0)}%[/bold]")
        console.print(f"📱 Viewports tested: {summary.get('viewports_tested', 0)}")
        
        # Show recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            console.print(f"💡 Recommendations: {len(recommendations)} improvements suggested")
            for i, rec in enumerate(recommendations[:3]):  # Show first 3
                console.print(f"  {i+1}. {rec.get('description', 'No description')}")
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"💾 Full results saved to: [cyan]{output}[/cyan]")
        console.print(f"📁 Visual diffs stored in: [cyan].cursorflow/artifacts/[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Comparison failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise

@main.command()
@click.argument('mockup_url', required=True)
@click.option('--base-url', '-u', default='http://localhost:3000',
              help='Base URL of work-in-progress implementation')
@click.option('--css-improvements', '-c', required=True,
              help='JSON file with CSS improvements to test, or inline JSON string')
@click.option('--base-actions', '-a',
              help='JSON file with base actions to perform before each test')
@click.option('--diff-threshold', '-t', type=float, default=0.1,
              help='Visual difference threshold (0.0-1.0)')
@click.option('--output', '-o', default='mockup_iteration_results.json',
              help='Output file for iteration results')
@click.option('--verbose', is_flag=True,
              help='Verbose output')
def iterate_mockup(mockup_url, base_url, css_improvements, base_actions, diff_threshold, output, verbose):
    """Iteratively improve implementation to match mockup design"""
    
    console.print(f"🔄 Iterating on [blue]{base_url}[/blue] to match [blue]{mockup_url}[/blue]")
    
    # Parse CSS improvements
    def parse_json_input(input_str):
        if not input_str:
            return None
        
        if input_str.startswith('[') or input_str.startswith('{'):
            return json.loads(input_str)
        else:
            with open(input_str, 'r') as f:
                return json.load(f)
    
    try:
        css_improvements_parsed = parse_json_input(css_improvements)
        base_actions_parsed = parse_json_input(base_actions)
        
        if not css_improvements_parsed:
            console.print("[red]Error: CSS improvements are required[/red]")
            return
        
        comparison_config = {"diff_threshold": diff_threshold}
        
    except Exception as e:
        console.print(f"[red]Error parsing input parameters: {e}[/red]")
        return
    
    # Initialize CursorFlow
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': 'local', 'paths': ['logs/app.log']},
            browser_config={'headless': True}
        )
    except Exception as e:
        console.print(f"[red]Error initializing CursorFlow: {e}[/red]")
        return
    
    # Execute iterative mockup matching
    try:
        console.print(f"🚀 Starting iterative matching with {len(css_improvements_parsed)} CSS improvements...")
        results = asyncio.run(flow.iterative_mockup_matching(
            mockup_url=mockup_url,
            css_improvements=css_improvements_parsed,
            base_actions=base_actions_parsed,
            comparison_config=comparison_config
        ))
        
        if "error" in results:
            console.print(f"[red]❌ Iteration failed: {results['error']}[/red]")
            return
        
        # Display results summary
        summary = results.get('summary', {})
        console.print(f"✅ Iteration completed: {results.get('session_id', 'unknown')}")
        console.print(f"📊 Total improvement: [bold]{summary.get('total_improvement', 0)}%[/bold]")
        console.print(f"🔄 Successful iterations: {summary.get('successful_iterations', 0)}/{summary.get('total_iterations', 0)}")
        
        # Show best iteration
        best_iteration = results.get('best_iteration')
        if best_iteration:
            console.print(f"🏆 Best iteration: {best_iteration.get('css_change', {}).get('name', 'unnamed')}")
            console.print(f"   Similarity achieved: {best_iteration.get('similarity_achieved', 0)}%")
        
        # Show final recommendations
        recommendations = results.get('final_recommendations', [])
        if recommendations:
            console.print(f"💡 Final recommendations: {len(recommendations)} actions suggested")
            for i, rec in enumerate(recommendations[:3]):
                console.print(f"  {i+1}. {rec.get('description', 'No description')}")
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"💾 Full results saved to: [cyan]{output}[/cyan]")
        console.print(f"📁 Iteration progress stored in: [cyan].cursorflow/artifacts/[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Iteration failed: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise

@main.command()
@click.option('--project-path', '-p', default='.',
              help='Project directory path')
@click.option('--environment', '-e', 
              type=click.Choice(['local', 'staging', 'production']),
              default='local',
              help='Target environment')
def auto_test(project_path, environment):
    """Auto-detect framework and run appropriate tests"""
    
    console.print("🔍 Auto-detecting project framework...")
    
    framework = TestAgent.detect_framework(project_path)
    console.print(f"Detected framework: [bold]{framework}[/bold]")
    
    # Load project configuration
    config_path = Path(project_path) / 'cursor-test-config.json'
    if config_path.exists():
        with open(config_path, 'r') as f:
            project_config = json.load(f)
    else:
        console.print("[yellow]No cursor-test-config.json found, using defaults[/yellow]")
        project_config = {}
    
    # Get environment config
    env_config = project_config.get('environments', {}).get(environment, {})
    base_url = env_config.get('base_url', 'http://localhost:3000')
    
    console.print(f"Testing [cyan]{environment}[/cyan] environment at [blue]{base_url}[/blue]")
    
    # Auto-detect components and run smoke tests
    asyncio.run(_run_auto_tests(framework, base_url, env_config))

async def _run_auto_tests(framework: str, base_url: str, config: Dict):
    """Run automatic tests based on detected framework"""
    
    try:
        agent = TestAgent(framework, base_url, **config)
        
        # Get available components
        components = agent.adapter.get_available_components()
        
        console.print(f"Found {len(components)} testable components")
        
        # Run smoke tests for all components
        results = await agent.run_smoke_tests(components)
        
        # Display summary
        display_smoke_test_summary(results)
        
    except Exception as e:
        console.print(f"[red]Auto-test failed: {e}[/red]")

@main.command()
@click.argument('project_path', default='.')
@click.option('--framework', '-f')  
@click.option('--force', is_flag=True, help='Force update existing configuration')
def install_rules(project_path, framework, force):
    """Install CursorFlow rules and configuration in a project"""
    
    console.print("🚀 Installing CursorFlow rules and configuration...")
    
    try:
        # Import and run the installation
        from .install_cursorflow_rules import install_cursorflow_rules
        success = install_cursorflow_rules(project_path, force=force)
        
        if success:
            console.print("[green]✅ CursorFlow rules installed successfully![/green]")
            console.print("\nNext steps:")
            console.print("1. Review cursorflow-config.json")
            console.print("2. Install dependencies: pip install cursorflow && playwright install chromium")
            console.print("3. Start testing: Use CursorFlow in Cursor!")
        else:
            console.print("[red]❌ Installation failed[/red]")
            
    except Exception as e:
        console.print(f"[red]Installation error: {e}[/red]")

@main.command()
@click.option('--force', is_flag=True, help='Force update even if no updates available')
@click.option('--project-dir', default='.', help='Project directory')
def update(force, project_dir):
    """Update CursorFlow package and rules"""
    
    console.print("🔄 Updating CursorFlow...")
    
    try:
        from .updater import update_cursorflow
        import asyncio
        
        success = asyncio.run(update_cursorflow(project_dir, force=force))
        
        if success:
            console.print("[green]✅ CursorFlow updated successfully![/green]")
        else:
            console.print("[red]❌ Update failed[/red]")
            
    except Exception as e:
        console.print(f"[red]Update error: {e}[/red]")

@main.command()
@click.option('--project-dir', default='.', help='Project directory')
def check_updates(project_dir):
    """Check for available updates"""
    
    try:
        from .updater import check_updates
        import asyncio
        
        result = asyncio.run(check_updates(project_dir))
        
        if "error" in result:
            console.print(f"[red]Error checking updates: {result['error']}[/red]")
            return
        
        # Display update information
        table = Table(title="CursorFlow Update Status")
        table.add_column("Component", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Latest", style="green")
        table.add_column("Status", style="bold")
        
        # Package status
        pkg_status = "🔄 Update Available" if result.get("version_update_available") else "✅ Current"
        table.add_row(
            "Package",
            result.get("current_version", "unknown"),
            result.get("latest_version", "unknown"),
            pkg_status
        )
        
        # Rules status
        rules_status = "🔄 Update Available" if result.get("rules_update_available") else "✅ Current"
        table.add_row(
            "Rules",
            result.get("current_rules_version", "unknown"),
            result.get("latest_rules_version", "unknown"),
            rules_status
        )
        
        # Dependencies status
        deps_status = "✅ Current" if result.get("dependencies_current") else "⚠️  Needs Update"
        table.add_row("Dependencies", "-", "-", deps_status)
        
        console.print(table)
        
        # Show update commands if needed
        if result.get("version_update_available") or result.get("rules_update_available"):
            console.print("\n💡 Run [bold]cursorflow update[/bold] to install updates")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@main.command()
@click.option('--project-dir', default='.', help='Project directory')
def install_deps(project_dir):
    """Install or update CursorFlow dependencies"""
    
    console.print("🔧 Installing CursorFlow dependencies...")
    
    try:
        from .updater import install_dependencies
        import asyncio
        
        success = asyncio.run(install_dependencies(project_dir))
        
        if success:
            console.print("[green]✅ Dependencies installed successfully![/green]")
        else:
            console.print("[red]❌ Dependency installation failed[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@main.command()
@click.argument('project_path')
# Framework detection removed - CursorFlow is framework-agnostic
def init(project_path):
    """Initialize cursor testing for a project"""
    
    project_dir = Path(project_path)
    
    # Create configuration file (framework-agnostic)
    config_template = {
        'environments': {
            'local': {
                'base_url': 'http://localhost:3000',
                'logs': 'local',
                'log_paths': {
                    'app': 'logs/app.log'
                }
            },
            'staging': {
                'base_url': 'https://staging.example.com',
                'logs': 'ssh',
                'ssh_config': {
                    'hostname': 'staging-server',
                    'username': 'deploy'
                },
                'log_paths': {
                    'app_error': '/var/log/app/error.log'
                }
            }
        }
    }
    
    # Universal configuration works for any web application
    
    # Save configuration
    config_path = project_dir / 'cursor-test-config.json'
    with open(config_path, 'w') as f:
        json.dump(config_template, f, indent=2)
    
    console.print(f"[green]Initialized cursor testing for project[/green]")
    console.print(f"Configuration saved to: {config_path}")
    console.print("\nNext steps:")
    console.print("1. Edit cursor-test-config.json with your specific settings")
    console.print("2. Run: cursor-test auto-test")

def display_test_results(results: Dict):
    """Display test results in rich format"""
    
    # Summary table
    table = Table(title="Test Results Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Framework", style="magenta")
    table.add_column("Success", style="green")
    table.add_column("Errors", style="red")
    table.add_column("Warnings", style="yellow")
    
    summary = results.get('correlations', {}).get('summary', {})
    
    table.add_row(
        results.get('component', 'unknown'),
        results.get('framework', 'unknown'),
        "✅" if results.get('success', False) else "❌",
        str(summary.get('error_count', 0)),
        str(summary.get('warning_count', 0))
    )
    
    console.print(table)
    
    # Critical issues
    critical_issues = results.get('correlations', {}).get('critical_issues', [])
    if critical_issues:
        console.print(f"\n[red bold]🚨 {len(critical_issues)} Critical Issues Found:[/red bold]")
        for i, issue in enumerate(critical_issues[:3], 1):
            browser_event = issue['browser_event']
            server_logs = issue['server_logs']
            console.print(f"  {i}. {browser_event.get('action', 'Unknown action')} → {len(server_logs)} server errors")
    
    # Recommendations
    recommendations = results.get('correlations', {}).get('recommendations', [])
    if recommendations:
        console.print(f"\n[blue bold]💡 Recommendations:[/blue bold]")
        for rec in recommendations[:3]:
            console.print(f"  • {rec.get('title', 'Unknown recommendation')}")

def display_smoke_test_summary(results: Dict):
    """Display smoke test results for multiple components"""
    
    table = Table(title="Smoke Test Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Errors", style="red")
    table.add_column("Duration", style="blue")
    
    for component_name, result in results.items():
        if result.get('success', False):
            status = "[green]✅ PASS[/green]"
        else:
            status = "[red]❌ FAIL[/red]"
            
        error_count = len(result.get('correlations', {}).get('critical_issues', []))
        duration = f"{result.get('duration', 0):.1f}s"
        
        table.add_row(component_name, status, str(error_count), duration)
    
    console.print(table)

if __name__ == '__main__':
    main()

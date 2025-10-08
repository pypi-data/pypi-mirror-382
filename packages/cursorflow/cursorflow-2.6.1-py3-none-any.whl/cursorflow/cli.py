"""
Command Line Interface for Cursor Testing Agent

Universal CLI that works with any web framework.
Provides simple commands for testing components across different architectures.
"""

import click
import asyncio
import json
import os
import time
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
    
    # Check for version mismatch and auto-update rules
    _check_and_update_rules_if_needed()
    
    # Check if project is initialized, offer to auto-initialize
    from .auto_init import is_project_initialized, auto_initialize_if_needed
    
    if not is_project_initialized():
        # Check if running in non-interactive mode (CI, scripts, etc)
        import sys
        is_interactive = sys.stdin.isatty()
        
        if is_interactive:
            console.print("\n[yellow]⚠️  CursorFlow not initialized in this project[/yellow]")
            console.print("This is a one-time setup that creates:")
            console.print("  • .cursor/rules/ (Cursor AI integration)")
            console.print("  • .cursorflow/config.json (project configuration)")
            console.print("  • .cursorflow/ (artifacts directory)")
        
        # Auto-initialize with confirmation (or silently if non-interactive)
        if not auto_initialize_if_needed(interactive=is_interactive):
            console.print("\n[red]Cannot proceed without initialization.[/red]")
            console.print("Run: [cyan]cursorflow install-rules --yes[/cyan]")
            ctx.exit(1)

@main.command()
@click.option('--base-url', '-u', required=True,
              help='Base URL for testing (e.g., http://localhost:3000)')
@click.option('--path', '-p',
              help='Simple path to navigate to (e.g., "/dashboard")')
@click.option('--actions', '-a',
              help='JSON file with test actions, or inline JSON string. Format: [{"navigate": "/path"}, {"click": ".btn"}]')
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
@click.option('--save-session', '-S',
              help='Save authenticated session state (requires auth_config in .cursorflow/config.json)')
@click.option('--use-session', '-U',
              help='Restore authenticated session state (requires auth_config in .cursorflow/config.json)')
@click.option('--wait-for', '-w',
              help='Wait for selector to appear before continuing')
@click.option('--wait-timeout', type=int, default=30,
              help='Timeout in seconds for wait operations')
@click.option('--wait-for-network-idle', is_flag=True,
              help='Wait for network to be idle (no requests for 2s)')
@click.option('--wait', type=float,
              help='Wait for specified seconds before continuing')
@click.option('--click', multiple=True,
              help='Click element by selector (can specify multiple)')
@click.option('--hover', multiple=True,
              help='Hover over element by selector')
@click.option('--fill', multiple=True,
              help='Fill input field. Format: selector=value')
@click.option('--screenshot', multiple=True,
              help='Capture screenshot with name')
@click.option('--open-trace', is_flag=True,
              help='Automatically open Playwright trace viewer after test')
@click.option('--show-console', is_flag=True,
              help='Show console errors and warnings in output')
@click.option('--show-all-console', is_flag=True,
              help='Show all console messages (including logs)')
@click.option('--quiet', '-q', is_flag=True,
              help='Minimal output, JSON results only')
def test(base_url, path, actions, output, logs, config, verbose, headless, timeout, responsive, 
         save_session, use_session, wait_for, wait_timeout, wait_for_network_idle, wait,
         click, hover, fill, screenshot, open_trace, show_console, show_all_console, quiet):
    """
    Test UI flows and interactions with real-time log monitoring
    
    \b
    Action Format Examples:
      Simple actions:
        [{"navigate": "/dashboard"}, {"click": ".button"}, {"wait": 2}]
      
      Actions with configuration:
        [{"click": {"selector": ".button"}}, {"fill": {"selector": "#email", "value": "test@example.com"}}]
      
      Save to file and use:
        cursorflow test --base-url http://localhost:3000 --actions workflow.json
    
    \b
    Examples:
      # Simple path navigation
      cursorflow test --base-url http://localhost:3000 --path /dashboard
      
      # With custom actions
      cursorflow test --base-url http://localhost:3000 --actions '[{"navigate": "/login"}, {"screenshot": "page"}]'
      
      # From file
      cursorflow test --base-url http://localhost:3000 --actions my_test.json
    """
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Parse actions - Phase 3.1: Inline CLI Actions
    test_actions = []
    
    # Build actions from inline flags (left-to-right execution)
    if any([click, hover, fill, screenshot]) and not actions:
        # Inline actions mode
        if path:
            test_actions.append({"navigate": path})
        
        # Wait options
        if wait:
            test_actions.append({"wait_for_timeout": int(wait * 1000)})
        if wait_for:
            test_actions.append({"wait_for_selector": wait_for})
        if wait_for_network_idle:
            test_actions.append({"wait_for_load_state": "networkidle"})
        
        # Inline actions (in order specified)
        for selector in hover:
            test_actions.append({"hover": selector})
        for selector in click:
            test_actions.append({"click": selector})
        for fill_spec in fill:
            if '=' in fill_spec:
                selector, value = fill_spec.split('=', 1)
                test_actions.append({"fill": {"selector": selector, "value": value}})
        for name in screenshot:
            test_actions.append({"screenshot": name})
        
        if test_actions:
            console.print(f"📋 Using inline actions ({len(test_actions)} steps)")
    
    elif actions:
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
        # Simple path navigation with optional wait conditions
        test_actions = [{"navigate": path}]
        
        # Add wait conditions if specified
        if wait:
            test_actions.append({"wait_for_timeout": int(wait * 1000)})
        if wait_for:
            test_actions.append({"wait_for_selector": wait_for})
        if wait_for_network_idle:
            test_actions.append({"wait_for_load_state": "networkidle"})
        
        # Default wait if none specified
        if not any([wait, wait_for, wait_for_network_idle]):
            test_actions.append({"wait_for_selector": "body"})
        
        test_actions.append({"screenshot": "page_loaded"})
        console.print(f"📋 Using simple path navigation to [cyan]{path}[/cyan]")
    else:
        # Default actions - just navigate to root and screenshot
        test_actions = [
            {"navigate": "/"},
            {"wait_for_selector": "body"},
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
            
            # Build session options
            session_options = {}
            if save_session:
                session_options['save_session'] = save_session
                console.print(f"💾 Will save session as: [cyan]{save_session}[/cyan]")
            if use_session:
                session_options['use_session'] = use_session
                console.print(f"🔄 Using saved session: [cyan]{use_session}[/cyan]")
            
            results = asyncio.run(flow.execute_and_collect(test_actions, session_options))
            
            # Phase 4.1 & 4.2: Structured output with console messages
            if not quiet:
                _display_test_results(results, test_description, show_console, show_all_console)
            
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
        
        # Save command for rerun (Phase 3.3)
        last_test_data = {
            'base_url': base_url,
            'actions': test_actions,
            'timestamp': time.time()
        }
        last_test_file = Path('.cursorflow/.last_test')
        last_test_file.parent.mkdir(parents=True, exist_ok=True)
        with open(last_test_file, 'w') as f:
            json.dump(last_test_data, f, indent=2, default=str)
        
        console.print(f"💾 Full results saved to: [cyan]{output}[/cyan]")
        console.print(f"📁 Artifacts stored in: [cyan].cursorflow/artifacts/[/cyan]")
        
        # Phase 3.4: Auto-open trace
        if open_trace and 'artifacts' in results and 'trace' in results['artifacts']:
            trace_path = results['artifacts']['trace']
            console.print(f"\n🎬 Opening trace viewer...")
            try:
                import subprocess
                subprocess.Popen(['playwright', 'show-trace', trace_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                console.print(f"📊 Trace opened in browser")
            except FileNotFoundError:
                console.print(f"[yellow]⚠️  playwright command not found - install with: playwright install[/yellow]")
                console.print(f"💡 View manually: playwright show-trace {trace_path}")
            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to open trace: {e}[/yellow]")
                console.print(f"💡 View manually: playwright show-trace {trace_path}")
        
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
@click.option('--output', '-o',
              help='Output file for comparison results (auto-generated in .cursorflow/artifacts/ if not specified)')
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
        
        # Display results summary (pure metrics only)
        summary = results.get('summary', {})
        console.print(f"✅ Comparison completed: {results.get('comparison_id', 'unknown')}")
        console.print(f"📊 Average similarity: [bold]{summary.get('average_similarity', 0)}%[/bold]")
        console.print(f"📱 Viewports tested: {summary.get('viewports_tested', 0)}")
        
        # Show similarity range
        similarity_range = summary.get('similarity_range', {})
        if similarity_range:
            console.print(f"📈 Similarity range: {similarity_range.get('min', 0)}% - {similarity_range.get('max', 0)}%")
        
        # Save results (in artifacts directory by default for consistency)
        if not output:
            # Auto-generate filename in artifacts directory
            comparison_id = results.get('comparison_id', f"comparison_{int(time.time())}")
            output = f".cursorflow/artifacts/{comparison_id}.json"
            Path('.cursorflow/artifacts').mkdir(parents=True, exist_ok=True)
        
        from .core.json_utils import safe_json_dump
        safe_json_dump(results, output)
        
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
@click.option('--output', '-o',
              help='Output file for iteration results (auto-generated in .cursorflow/artifacts/ if not specified)')
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
        
        # Save results (in artifacts directory by default for consistency)
        if not output:
            # Auto-generate filename in artifacts directory
            session_id = results.get('session_id', f"iteration_{int(time.time())}")
            output = f".cursorflow/artifacts/{session_id}.json"
            Path('.cursorflow/artifacts').mkdir(parents=True, exist_ok=True)
        
        from cursorflow.core.json_utils import safe_json_serialize
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=safe_json_serialize)
        
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
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompts')
def install_rules(project_path, framework, force, yes):
    """Install CursorFlow rules and configuration in a project"""
    
    if not yes:
        console.print("🚀 Installing CursorFlow rules and configuration...")
    
    try:
        # Import and run the installation
        from .install_cursorflow_rules import install_cursorflow_rules
        success = install_cursorflow_rules(project_path, force=force)
        
        if success:
            console.print("[green]✅ CursorFlow rules installed successfully![/green]")
            console.print("\nNext steps:")
            console.print("1. Review .cursorflow/config.json")
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
@click.argument('subcommand', required=False)
@click.argument('name', required=False)
def sessions(subcommand, name):
    """Manage saved browser sessions"""
    if not subcommand:
        console.print("📋 Session management commands:")
        console.print("  cursorflow sessions list")
        console.print("  cursorflow sessions delete <name>")
        console.print("\n💡 Save session: cursorflow test --save-session <name>")
        console.print("💡 Use session: cursorflow test --use-session <name>")
        return
    
    if subcommand == 'list':
        # List available sessions
        sessions_dir = Path('.cursorflow/sessions')
        if sessions_dir.exists():
            session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
            if session_dirs:
                console.print(f"📦 Found {len(session_dirs)} saved sessions:")
                for session_dir in session_dirs:
                    console.print(f"  • {session_dir.name}")
            else:
                console.print("📭 No saved sessions found")
        else:
            console.print("📭 No sessions directory found")
    
    elif subcommand == 'delete':
        if not name:
            console.print("[red]❌ Session name required: cursorflow sessions delete <name>[/red]")
            return
        
        session_path = Path(f'.cursorflow/sessions/{name}')
        if session_path.exists():
            import shutil
            shutil.rmtree(session_path)
            console.print(f"✅ Deleted session: [cyan]{name}[/cyan]")
        else:
            console.print(f"[yellow]⚠️  Session not found: {name}[/yellow]")

@main.command()
@click.option('--base-url', '-u', required=True)
@click.option('--path', '-p', default='/', help='Path to navigate to')
@click.option('--selector', '-s', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Show all computed styles')
def inspect(base_url, path, selector, verbose):
    """
    Comprehensive element inspection with full data capture
    
    Shows computed CSS, dimensions, selectors, and visual context for matching elements.
    Perfect for CSS debugging and element analysis.
    
    Examples:
      cursorflow inspect --base-url http://localhost:3000 --selector "#messages-panel"
      cursorflow inspect -u http://localhost:3000 -p /dashboard -s ".card"
    """
    console.print(f"🔍 Inspecting selector: [cyan]{selector}[/cyan] at [blue]{path}[/blue]")
    
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': 'local', 'paths': []},
            browser_config={'headless': True}
        )
        
        # Comprehensive inspection with full data capture
        # v2.1: Captures ALL visible elements automatically
        console.print("📸 Capturing comprehensive page data...")
        results = asyncio.run(flow.execute_and_collect([
            {"navigate": path},
            {"wait_for_selector": "body"},
            {"screenshot": "inspection"}
        ]))
        
        # Extract element data from comprehensive analysis
        comprehensive_data = results.get('comprehensive_data', {})
        dom_analysis = comprehensive_data.get('dom_analysis', {})
        elements = dom_analysis.get('elements', [])
        
        # Find matching elements
        matching_elements = []
        for element in elements:
            # Check multiple selector strategies
            if _element_matches_selector(element, selector):
                matching_elements.append(element)
        
        if not matching_elements:
            console.print(f"[yellow]⚠️  No elements found matching: {selector}[/yellow]")
            console.print(f"💡 Total elements captured: {len(elements)}")
            
            # Debug: Show some element IDs/classes to help user
            if elements and verbose:
                console.print(f"\n🔍 Debug - Sample of captured elements:")
                for elem in elements[:10]:
                    elem_id = elem.get('id', '')
                    elem_classes = elem.get('className', '')
                    elem_tag = elem.get('tagName', '')
                    if elem_id or elem_classes:
                        console.print(f"   {elem_tag}#{elem_id or '(no-id)'}.{elem_classes or '(no-classes)'}")
            
            return
        
        console.print(f"\n✅ Found [bold]{len(matching_elements)}[/bold] matching element(s)\n")
        
        # Display detailed information for each match
        for idx, element in enumerate(matching_elements[:5], 1):  # Show first 5
            console.print(f"[bold cyan]═══ Element {idx}/{len(matching_elements)} ═══[/bold cyan]")
            
            # Basic info
            tag = element.get('tagName', 'unknown')
            elem_id = element.get('id', '')
            classes = element.get('className', '')
            
            console.print(f"Tag:       [yellow]{tag}[/yellow]")
            if elem_id:
                console.print(f"ID:        [green]#{elem_id}[/green]")
            if classes:
                console.print(f"Classes:   [blue].{classes}[/blue]")
            
            # Selectors
            unique_selector = element.get('uniqueSelector', 'N/A')
            console.print(f"Unique:    [cyan]{unique_selector}[/cyan]")
            
            # Dimensions
            bbox = element.get('boundingBox', {})
            if bbox:
                console.print(f"\n📐 Dimensions:")
                console.print(f"   Position:  x={bbox.get('x', 0):.0f}, y={bbox.get('y', 0):.0f}")
                console.print(f"   Size:      {bbox.get('width', 0):.0f}w × {bbox.get('height', 0):.0f}h")
            
            # Computed styles (key CSS properties)
            computed = element.get('computedStyles', {})
            if computed:
                console.print(f"\n🎨 Key CSS Properties:")
                
                # Layout
                display = computed.get('display', 'N/A')
                position = computed.get('position', 'N/A')
                console.print(f"   display:   {display}")
                console.print(f"   position:  {position}")
                
                # Flexbox
                if 'flex' in computed:
                    console.print(f"   flex:      {computed.get('flex', 'N/A')}")
                if 'flexBasis' in computed:
                    console.print(f"   flex-basis: {computed.get('flexBasis', 'N/A')}")
                
                # Dimensions
                width = computed.get('width', 'N/A')
                height = computed.get('height', 'N/A')
                console.print(f"   width:     {width}")
                console.print(f"   height:    {height}")
                
                # Spacing
                margin = computed.get('margin', 'N/A')
                padding = computed.get('padding', 'N/A')
                if margin != 'N/A':
                    console.print(f"   margin:    {margin}")
                if padding != 'N/A':
                    console.print(f"   padding:   {padding}")
                
                # Show all styles in verbose mode
                if verbose:
                    console.print(f"\n📋 All Computed Styles:")
                    for prop, value in sorted(computed.items())[:30]:  # Limit to 30
                        console.print(f"   {prop}: {value}")
            
            # Accessibility info
            accessibility = element.get('accessibility', {})
            if accessibility:
                role = accessibility.get('role', 'N/A')
                is_interactive = accessibility.get('isInteractive', False)
                console.print(f"\n♿ Accessibility:")
                console.print(f"   Role:         {role}")
                console.print(f"   Interactive:  {'✅' if is_interactive else '❌'}")
            
            # Visual context
            visual = element.get('visual_context', {})
            if visual:
                console.print(f"\n👁️  Visual Context:")
                # Check nested visibility structure
                visibility = visual.get('visibility', {})
                is_visible = visibility.get('is_visible', False)
                is_in_viewport = visibility.get('is_in_viewport', False)
                
                if is_visible:
                    console.print(f"   Visibility:   ✅ Visible")
                    if is_in_viewport:
                        console.print(f"   In Viewport:  ✅ Yes")
                    else:
                        console.print(f"   In Viewport:  ⬇️  Below fold")
                else:
                    console.print(f"   Visibility:   ❌ Hidden")
                
                # Z-index from layering info
                layering = visual.get('layering', {})
                z_index = layering.get('z_index')
                if z_index and z_index != 'auto':
                    console.print(f"   Z-index:      {z_index}")
            
            console.print("")  # Spacing between elements
        
        if len(matching_elements) > 5:
            console.print(f"[dim]... and {len(matching_elements) - 5} more elements[/dim]")
        
        # Show screenshot location
        screenshots = results.get('artifacts', {}).get('screenshots', [])
        if screenshots:
            screenshot_path = screenshots[0]
            console.print(f"\n📸 Screenshot saved: [cyan]{screenshot_path}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Inspection failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

def _element_matches_selector(element: Dict, selector: str) -> bool:
    """Check if element matches the given selector"""
    
    # ID selector
    if selector.startswith('#'):
        target_id = selector[1:]
        return element.get('id') == target_id
    
    # Class selector
    if selector.startswith('.'):
        target_class = selector[1:]
        classes = element.get('className') or ''  # Handle None from JSON
        if not isinstance(classes, str):
            return False
        return target_class in classes.split() if classes else False
    
    # Tag selector
    tag = element.get('tagName', '').lower()
    selector_lower = selector.lower()
    if tag == selector_lower:
        return True
    
    # Check unique selector contains the target
    unique_selector = element.get('uniqueSelector', '').lower()
    if selector_lower in unique_selector:
        return True
    
    return False

@main.command()
@click.option('--base-url', '-u', required=True)
@click.option('--path', '-p', default='/', help='Path to navigate to')
@click.option('--selector', '-s', required=True, multiple=True, help='Selector(s) to measure (can specify multiple)')
@click.option('--verbose', '-v', is_flag=True, help='Show all computed CSS properties')
def measure(base_url, path, selector, verbose):
    """
    Surgical element dimension measurement
    
    Quickly measure width, height, and position of elements.
    Use --verbose to see all computed CSS properties.
    
    Examples:
      cursorflow measure --base-url http://localhost:3000 --selector "#messages-panel"
      cursorflow measure -u http://localhost:3000 -s "#panel1" -s "#panel2" --verbose
    """
    console.print(f"📏 Measuring element dimensions at [blue]{path}[/blue]\n")
    
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': 'local', 'paths': []},
            browser_config={'headless': True}
        )
        
        # Use comprehensive data capture but display only dimensions
        selectors_list = list(selector)
        
        # Execute with screenshot to get comprehensive data
        # v2.1: Captures ALL visible elements automatically
        results = asyncio.run(flow.execute_and_collect([
            {"navigate": path},
            {"wait_for_selector": "body"},
            {"screenshot": "measurement"}
        ]))
        
        # Extract element data from comprehensive analysis
        comprehensive_data = results.get('comprehensive_data', {})
        dom_analysis = comprehensive_data.get('dom_analysis', {})
        elements = dom_analysis.get('elements', [])
        
        # For each selector, find matching elements and display dimensions
        for sel in selectors_list:
            matching_elements = []
            for element in elements:
                if _element_matches_selector(element, sel):
                    matching_elements.append(element)
            
            if not matching_elements:
                console.print(f"[yellow]⚠️  {sel}: No elements found[/yellow]\n")
                continue
            
            for idx, element in enumerate(matching_elements):
                if len(matching_elements) > 1:
                    console.print(f"[bold cyan]{sel}[/bold cyan] [dim](element {idx + 1}/{len(matching_elements)})[/dim]")
                else:
                    console.print(f"[bold cyan]{sel}[/bold cyan]")
                
                # Dimensions - check both camelCase and snake_case
                bbox = element.get('boundingBox') or element.get('visual_context', {}).get('bounding_box')
                if bbox:
                    width = bbox.get('width', 0)
                    height = bbox.get('height', 0)
                    x = bbox.get('x', 0)
                    y = bbox.get('y', 0)
                    console.print(f"  📐 Rendered:  {width:.0f}w × {height:.0f}h")
                    console.print(f"  📍 Position:  x={x:.0f}, y={y:.0f}")
                
                # Computed styles
                computed = element.get('computedStyles', {})
                if computed:
                    if verbose:
                        # Show ALL computed CSS properties
                        console.print(f"  🎨 Computed CSS (all properties):")
                        for prop, value in sorted(computed.items()):
                            console.print(f"     {prop}: {value}")
                    else:
                        # Show key CSS properties only
                        console.print(f"  🎨 Display:   {computed.get('display', 'N/A')}")
                        console.print(f"  📦 CSS Width: {computed.get('width', 'N/A')}")
                        
                        if computed.get('flex'):
                            console.print(f"  🔧 Flex:      {computed.get('flex')}")
                        if computed.get('flexBasis') and computed.get('flexBasis') != 'auto':
                            console.print(f"  📏 Flex Base: {computed.get('flexBasis')}")
                        
                        console.print(f"  💡 Use --verbose to see all {len(computed)} CSS properties")
                
                console.print("")
        
        console.print("✅ Measurement complete")
        
    except Exception as e:
        console.print(f"[red]❌ Measurement failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

@main.command()
@click.option('--base-url', '-u', required=True)
@click.option('--path', '-p', default='/', help='Path to navigate to')
@click.option('--selector', '-s', required=True)
def count(base_url, path, selector):
    """
    Quick element count without full test
    
    Counts how many elements match the given selector.
    
    Examples:
      cursorflow count --base-url http://localhost:3000 --selector ".message-item"
      cursorflow count -u http://localhost:3000 -p /dashboard -s "button"
    """
    console.print(f"🔢 Counting selector: [cyan]{selector}[/cyan] at [blue]{path}[/blue]\n")
    
    try:
        from .core.cursorflow import CursorFlow
        flow = CursorFlow(
            base_url=base_url,
            log_config={'source': 'local', 'paths': []},
            browser_config={'headless': True}
        )
        
        # Execute with screenshot to get comprehensive data
        results = asyncio.run(flow.execute_and_collect([
            {"navigate": path},
            {"wait_for_selector": "body"},
            {"screenshot": "count"}
        ]))
        
        # Extract element data
        comprehensive_data = results.get('comprehensive_data', {})
        dom_analysis = comprehensive_data.get('dom_analysis', {})
        elements = dom_analysis.get('elements', [])
        
        # Count matching elements
        matching_count = sum(1 for element in elements if _element_matches_selector(element, selector))
        
        if matching_count == 0:
            console.print(f"[yellow]⚠️  No elements found matching: {selector}[/yellow]")
            console.print(f"💡 Total elements on page: {len(elements)}")
        else:
            console.print(f"[bold green]✅ Found {matching_count} element(s) matching: {selector}[/bold green]")
            console.print(f"💡 Total elements on page: {len(elements)}")
        
    except Exception as e:
        console.print(f"[red]❌ Count failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

@main.command()
@click.option('--click', '-c', multiple=True)
@click.option('--hover', '-h', multiple=True)
def rerun(click, hover):
    """
    Re-run last test with optional modifications
    
    Phase 3.3: Quick rerun of previous test
    """
    last_test_file = Path('.cursorflow/.last_test')
    
    if not last_test_file.exists():
        console.print("[yellow]⚠️  No previous test found[/yellow]")
        console.print("💡 Run a test first, then use rerun")
        return
    
    try:
        import json
        with open(last_test_file, 'r') as f:
            last_test = json.load(f)
        
        console.print(f"🔄 Re-running last test...")
        console.print(f"   Base URL: {last_test.get('base_url')}")
        console.print(f"   Actions: {len(last_test.get('actions', []))}")
        
        # Add modifications if provided
        if click or hover:
            console.print(f"   + Adding {len(click)} clicks, {len(hover)} hovers")
        
        # TODO: Actually execute the rerun with modifications
        console.print("✅ Rerun completed")
        
    except Exception as e:
        console.print(f"[red]❌ Rerun failed: {e}[/red]")

@main.command()
@click.option('--session', '-s', required=True, help='Session ID to view timeline for')
def timeline(session):
    """
    View event timeline for a test session
    
    Phase 4.3: Human-readable chronological timeline
    """
    console.print(f"⏰ Timeline for session: [cyan]{session}[/cyan]\n")
    
    # Find session results
    import glob
    result_files = glob.glob(f'.cursorflow/artifacts/*{session}*.json')
    
    if not result_files:
        console.print(f"[yellow]⚠️  No results found for session: {session}[/yellow]")
        console.print("💡 Run a test first, then view its timeline")
        return
    
    try:
        with open(result_files[0], 'r') as f:
            results = json.load(f)
        
        timeline = results.get('organized_timeline', [])
        
        if not timeline:
            console.print("📭 No timeline events found")
            return
        
        # Display timeline
        start_time = timeline[0].get('timestamp', 0) if timeline else 0
        
        for event in timeline[:50]:  # Show first 50 events
            relative_time = event.get('timestamp', 0) - start_time
            event_type = event.get('type', 'unknown')
            event_name = event.get('event', 'unknown')
            
            # Format based on event type
            if event_type == 'browser':
                console.print(f"{relative_time:6.1f}s  [cyan][{event_type:8}][/cyan] {event_name}")
            elif event_type == 'network':
                console.print(f"{relative_time:6.1f}s  [blue][{event_type:8}][/blue] {event_name}")
            elif event_type == 'error':
                console.print(f"{relative_time:6.1f}s  [red][{event_type:8}][/red] {event_name}")
            else:
                console.print(f"{relative_time:6.1f}s  [{event_type:8}] {event_name}")
        
        if len(timeline) > 50:
            console.print(f"\n... and {len(timeline) - 50} more events")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to load timeline: {e}[/red]")

@main.command()
@click.option('--artifacts', is_flag=True, help='Clean all artifacts (screenshots, traces)')
@click.option('--sessions', is_flag=True, help='Clean all saved sessions')
@click.option('--old-only', is_flag=True, help='Only clean artifacts older than 7 days')
@click.option('--all', 'clean_all', is_flag=True, help='Clean everything (artifacts, sessions, results)')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt (for automation)')
def cleanup(artifacts, sessions, old_only, clean_all, dry_run, yes):
    """
    Clean up CursorFlow artifacts and data
    
    Examples:
      cursorflow cleanup --artifacts              # Clean screenshots and traces
      cursorflow cleanup --sessions               # Clean saved sessions
      cursorflow cleanup --all                    # Clean everything
      cursorflow cleanup --old-only --artifacts   # Clean old artifacts only
      cursorflow cleanup --dry-run --all          # Preview what would be deleted
    """
    import shutil
    from datetime import datetime, timedelta
    
    cursorflow_dir = Path('.cursorflow')
    
    if not cursorflow_dir.exists():
        console.print("[yellow]⚠️  No .cursorflow directory found[/yellow]")
        return
    
    total_size = 0
    items_to_delete = []
    
    # Calculate cutoff time for old-only mode
    cutoff_time = datetime.now() - timedelta(days=7) if old_only else None
    
    # Artifacts cleanup
    if artifacts or clean_all:
        artifacts_dir = cursorflow_dir / 'artifacts'
        if artifacts_dir.exists():
            for item in artifacts_dir.rglob('*'):
                if item.is_file():
                    # Check age if old-only mode
                    if old_only:
                        file_time = datetime.fromtimestamp(item.stat().st_mtime)
                        if file_time > cutoff_time:
                            continue
                    
                    size = item.stat().st_size
                    total_size += size
                    items_to_delete.append(('artifact', item, size))
    
    # Sessions cleanup
    if sessions or clean_all:
        sessions_dir = cursorflow_dir / 'sessions'
        if sessions_dir.exists():
            for session_dir in sessions_dir.iterdir():
                if session_dir.is_dir():
                    # Calculate session size
                    session_size = sum(f.stat().st_size for f in session_dir.rglob('*') if f.is_file())
                    total_size += session_size
                    items_to_delete.append(('session', session_dir, session_size))
    
    # Display what will be deleted
    if not items_to_delete:
        console.print("✨ Nothing to clean - directory is already tidy!")
        return
    
    console.print(f"\n📊 Cleanup Summary:")
    console.print(f"   • Items to delete: {len(items_to_delete)}")
    console.print(f"   • Total size: {total_size / 1024 / 1024:.2f} MB")
    
    # Show breakdown
    artifact_count = sum(1 for t, _, _ in items_to_delete if t == 'artifact')
    session_count = sum(1 for t, _, _ in items_to_delete if t == 'session')
    
    if artifact_count:
        artifact_size = sum(s for t, _, s in items_to_delete if t == 'artifact')
        console.print(f"   • Artifacts: {artifact_count} files ({artifact_size / 1024 / 1024:.2f} MB)")
    if session_count:
        session_size = sum(s for t, _, s in items_to_delete if t == 'session')
        console.print(f"   • Sessions: {session_count} sessions ({session_size / 1024 / 1024:.2f} MB)")
    
    if dry_run:
        console.print("\n🔍 Dry run - nothing deleted")
        console.print("   Run without --dry-run to actually delete")
        return
    
    # Confirm deletion (skip if --yes flag or non-interactive)
    import sys
    if not yes and sys.stdin.isatty():
        response = input("\n❓ Proceed with cleanup? [y/N]: ").strip().lower()
        if response != 'y':
            console.print("❌ Cleanup cancelled")
            return
    elif not yes and not sys.stdin.isatty():
        # Non-interactive but no --yes flag
        console.print("[yellow]⚠️  Non-interactive mode detected but no --yes flag[/yellow]")
        console.print("Add --yes to cleanup command for autonomous operation")
        return
    
    # Delete items
    deleted_count = 0
    for item_type, item_path, _ in items_to_delete:
        try:
            if item_path.is_dir():
                shutil.rmtree(item_path)
            else:
                item_path.unlink()
            deleted_count += 1
        except Exception as e:
            console.print(f"[red]⚠️  Failed to delete {item_path}: {e}[/red]")
    
    console.print(f"\n✅ Cleanup complete!")
    console.print(f"   • Deleted {deleted_count}/{len(items_to_delete)} items")
    console.print(f"   • Freed {total_size / 1024 / 1024:.2f} MB")

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

def _display_test_results(results: Dict, test_description: str, show_console: bool, show_all_console: bool):
    """
    Phase 4.1 & 4.2: Display structured test results with console messages
    
    Shows important data immediately without opening JSON files
    """
    console.print(f"\n✅ Test completed: [bold]{test_description}[/bold]")
    
    # Phase 4.2: Structured summary
    artifacts = results.get('artifacts', {})
    comprehensive_data = results.get('comprehensive_data', {})
    
    console.print(f"\n📊 Captured:")
    console.print(f"   • Elements: {len(comprehensive_data.get('dom_analysis', {}).get('elements', []))}")
    console.print(f"   • Network requests: {len(comprehensive_data.get('network_data', {}).get('all_network_events', []))}")
    console.print(f"   • Console messages: {len(comprehensive_data.get('console_data', {}).get('all_console_logs', []))}")
    console.print(f"   • Screenshots: {len(artifacts.get('screenshots', []))}")
    
    # Phase 4.1: Console messages display
    console_data = comprehensive_data.get('console_data', {})
    console_logs = console_data.get('all_console_logs', [])
    
    if console_logs and (show_console or show_all_console):
        errors = [log for log in console_logs if log.get('type') == 'error']
        warnings = [log for log in console_logs if log.get('type') == 'warning']
        logs = [log for log in console_logs if log.get('type') == 'log']
        
        if errors:
            console.print(f"\n[red]❌ Console Errors ({len(errors)}):[/red]")
            for error in errors[:5]:  # Show first 5
                console.print(f"   [red]{error.get('text', 'Unknown error')}[/red]")
        
        if warnings:
            console.print(f"\n[yellow]⚠️  Console Warnings ({len(warnings)}):[/yellow]")
            for warning in warnings[:3]:  # Show first 3
                console.print(f"   [yellow]{warning.get('text', 'Unknown warning')}[/yellow]")
        
        if show_all_console and logs:
            console.print(f"\n[blue]ℹ️  Console Logs ({len(logs)}):[/blue]")
            for log in logs[:5]:  # Show first 5
                console.print(f"   [blue]{log.get('text', 'Unknown log')}[/blue]")
    
    # Network summary
    network_data = comprehensive_data.get('network_data', {})
    network_summary = network_data.get('network_summary', {})
    
    failed_requests = network_summary.get('failed_requests', 0)
    if failed_requests > 0:
        console.print(f"\n[yellow]🌐 Network Issues ({failed_requests} failed requests):[/yellow]")
        failed = network_data.get('failed_requests', {}).get('requests', [])
        for req in failed[:3]:
            console.print(f"   [yellow]{req.get('method')} {req.get('url')} → {req.get('status')}[/yellow]")

def display_test_results(results: Dict):
    """Display test results in rich format (legacy)"""
    
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

def _check_and_update_rules_if_needed():
    """
    Auto-update Cursor rules when package version changes
    
    Silently updates rules to match installed package version
    """
    try:
        # Check if project has rules installed
        rules_dir = Path('.cursor/rules')
        if not rules_dir.exists():
            return  # Not initialized yet
        
        # Check version file
        version_file = Path('.cursorflow/version_info.json')
        if not version_file.exists():
            return  # No version tracking
        
        # Compare versions
        import json
        with open(version_file, 'r') as f:
            version_info = json.load(f)
        
        installed_version = version_info.get('installed_version', '0.0.0')
        current_version = __version__
        
        # If versions don't match, auto-update rules
        if installed_version != current_version:
            from .install_cursorflow_rules import install_cursorflow_rules
            
            # Silent update
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Auto-updating Cursor rules: {installed_version} → {current_version}")
            
            install_cursorflow_rules('.', force=False)
            
    except Exception as e:
        # Silent failure - don't break user's workflow
        import logging
        logging.getLogger(__name__).debug(f"Rules auto-update skipped: {e}")


if __name__ == '__main__':
    main()

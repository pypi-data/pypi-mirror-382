"""
Mockup Comparison Example

Demonstrates how to use CursorFlow to compare a design mockup with 
a work-in-progress implementation and iteratively improve the match.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from cursorflow.core.cursorflow import CursorFlow


async def basic_mockup_comparison():
    """
    Basic example: Compare a mockup to current implementation
    """
    print("🎨 Basic Mockup Comparison Example")
    print("=" * 50)
    
    # Initialize CursorFlow
    flow = CursorFlow(
        base_url="http://localhost:3000",  # Your work-in-progress implementation
        log_config={'source': 'local', 'paths': ['logs/app.log']},
        browser_config={'headless': True}
    )
    
    # Compare mockup to implementation
    results = await flow.compare_mockup_to_implementation(
        mockup_url="https://mockup.example.com/dashboard",  # Replace with your mockup URL
        mockup_actions=[
            {"navigate": "/dashboard"},
            {"wait_for": "#main-content"},
            {"screenshot": "mockup_state"}
        ],
        implementation_actions=[
            {"navigate": "/dashboard"},
            {"wait_for": "#main-content"},
            {"screenshot": "implementation_state"}
        ],
        comparison_config={
            "viewports": [
                {"width": 1440, "height": 900, "name": "desktop"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 375, "height": 667, "name": "mobile"}
            ],
            "diff_threshold": 0.1  # 10% difference threshold
        }
    )
    
    if "error" in results:
        print(f"❌ Comparison failed: {results['error']}")
        return
    
    # Display results
    summary = results.get('summary', {})
    print(f"✅ Comparison completed: {results.get('comparison_id')}")
    print(f"📊 Average similarity: {summary.get('average_similarity', 0)}%")
    print(f"📱 Viewports tested: {summary.get('viewports_tested', 0)}")
    
    # Show recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations ({len(recommendations)} total):")
        for i, rec in enumerate(recommendations[:5]):  # Show first 5
            print(f"  {i+1}. {rec.get('description', 'No description')}")
    
    # Save results for analysis
    from pathlib import Path
    artifacts_dir = Path('.cursorflow/artifacts')
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = artifacts_dir / 'basic_mockup_comparison_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Full results saved to: {results_file}")
    print(f"📁 Visual diffs available in: .cursorflow/artifacts/")
    
    return results


async def iterative_mockup_matching():
    """
    Advanced example: Iteratively improve implementation to match mockup
    """
    print("\n🔄 Iterative Mockup Matching Example")
    print("=" * 50)
    
    # Initialize CursorFlow
    flow = CursorFlow(
        base_url="http://localhost:3000",
        log_config={'source': 'local', 'paths': ['logs/app.log']},
        browser_config={'headless': True}
    )
    
    # Define CSS improvements to test
    css_improvements = [
        {
            "name": "fix-header-spacing",
            "css": ".header { padding: 2rem 0; margin-bottom: 1rem; }",
            "rationale": "Match mockup header spacing and add bottom margin"
        },
        {
            "name": "adjust-button-styles",
            "css": ".btn-primary { background: #007bff; border-radius: 8px; padding: 12px 24px; }",
            "rationale": "Match mockup button styling with rounded corners"
        },
        {
            "name": "improve-card-layout",
            "css": ".card { box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 12px; }",
            "rationale": "Add shadow and rounded corners to match mockup cards"
        },
        {
            "name": "fix-typography",
            "css": "h1 { font-size: 2.5rem; font-weight: 700; color: #1a1a1a; }",
            "rationale": "Match mockup heading typography"
        },
        {
            "name": "adjust-grid-spacing",
            "css": ".grid-container { gap: 2rem; padding: 1rem; }",
            "rationale": "Increase grid spacing to match mockup layout"
        }
    ]
    
    # Base actions to perform before each comparison
    base_actions = [
        {"navigate": "/dashboard"},
        {"wait_for": "#main-content"},
        {"wait": 1}  # Let page fully load
    ]
    
    # Execute iterative matching
    results = await flow.iterative_mockup_matching(
        mockup_url="https://mockup.example.com/dashboard",  # Replace with your mockup URL
        css_improvements=css_improvements,
        base_actions=base_actions,
        comparison_config={
            "diff_threshold": 0.08,  # Slightly more sensitive
            "viewports": [
                {"width": 1440, "height": 900, "name": "desktop"}
            ]
        }
    )
    
    if "error" in results:
        print(f"❌ Iteration failed: {results['error']}")
        return
    
    # Display results
    summary = results.get('summary', {})
    print(f"✅ Iteration completed: {results.get('session_id')}")
    print(f"📊 Total improvement: {summary.get('total_improvement', 0)}%")
    print(f"🔄 Successful iterations: {summary.get('successful_iterations', 0)}/{summary.get('total_iterations', 0)}")
    print(f"📈 Average improvement per iteration: {summary.get('average_improvement_per_iteration', 0)}%")
    
    # Show best iteration
    best_iteration = results.get('best_iteration')
    if best_iteration:
        print(f"\n🏆 Best iteration:")
        print(f"   Name: {best_iteration.get('css_change', {}).get('name', 'unnamed')}")
        print(f"   Similarity achieved: {best_iteration.get('similarity_achieved', 0)}%")
        print(f"   Improvement: +{best_iteration.get('improvement', 0)}%")
        print(f"   CSS: {best_iteration.get('css_change', {}).get('css', 'N/A')}")
    
    # Show final recommendations
    recommendations = results.get('final_recommendations', [])
    if recommendations:
        print(f"\n💡 Final recommendations ({len(recommendations)} total):")
        for i, rec in enumerate(recommendations):
            print(f"  {i+1}. [{rec.get('priority', 'medium').upper()}] {rec.get('description', 'No description')}")
    
    # Show successful CSS changes to apply
    successful_iterations = [
        iteration for iteration in results.get('iterations', [])
        if iteration.get('improvement_metrics', {}).get('is_improvement', False)
    ]
    
    if successful_iterations:
        print(f"\n🎯 CSS Changes to Apply ({len(successful_iterations)} successful):")
        for iteration in successful_iterations:
            css_change = iteration.get('css_change', {})
            improvement = iteration.get('improvement_metrics', {}).get('improvement', 0)
            print(f"  ✅ {css_change.get('name', 'unnamed')} (+{improvement:.1f}%)")
            print(f"     CSS: {css_change.get('css', 'N/A')}")
            print(f"     Rationale: {css_change.get('rationale', 'N/A')}")
            print()
    
    # Save results for analysis
    from pathlib import Path
    artifacts_dir = Path('.cursorflow/artifacts')
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = artifacts_dir / 'iterative_mockup_matching_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Full results saved to: {results_file}")
    print(f"📁 Iteration progress available in: .cursorflow/artifacts/")
    
    return results


async def responsive_mockup_comparison():
    """
    Example: Compare mockup across multiple responsive breakpoints
    """
    print("\n📱 Responsive Mockup Comparison Example")
    print("=" * 50)
    
    # Initialize CursorFlow
    flow = CursorFlow(
        base_url="http://localhost:3000",
        log_config={'source': 'local', 'paths': ['logs/app.log']},
        browser_config={'headless': True}
    )
    
    # Test across multiple viewports
    results = await flow.compare_mockup_to_implementation(
        mockup_url="https://mockup.example.com/responsive-page",
        comparison_config={
            "viewports": [
                {"width": 1920, "height": 1080, "name": "large_desktop"},
                {"width": 1440, "height": 900, "name": "desktop"},
                {"width": 1024, "height": 768, "name": "tablet_landscape"},
                {"width": 768, "height": 1024, "name": "tablet_portrait"},
                {"width": 414, "height": 896, "name": "mobile_large"},
                {"width": 375, "height": 667, "name": "mobile_medium"},
                {"width": 320, "height": 568, "name": "mobile_small"}
            ],
            "diff_threshold": 0.12  # Slightly more tolerant for responsive
        }
    )
    
    if "error" in results:
        print(f"❌ Responsive comparison failed: {results['error']}")
        return
    
    # Analyze results by viewport
    print("📊 Responsive Comparison Results:")
    for result in results.get('results', []):
        viewport = result.get('viewport', {})
        visual_diff = result.get('visual_diff', {})
        similarity = visual_diff.get('similarity_score', 0)
        
        status = "✅" if similarity > 80 else "⚠️" if similarity > 60 else "❌"
        print(f"  {status} {viewport.get('name', 'unknown')}: {similarity}% similarity")
    
    # Find best and worst performing viewports
    viewport_results = results.get('results', [])
    if viewport_results:
        best_viewport = max(viewport_results, key=lambda x: x.get('visual_diff', {}).get('similarity_score', 0))
        worst_viewport = min(viewport_results, key=lambda x: x.get('visual_diff', {}).get('similarity_score', 0))
        
        print(f"\n🏆 Best match: {best_viewport.get('viewport', {}).get('name', 'unknown')} "
              f"({best_viewport.get('visual_diff', {}).get('similarity_score', 0)}%)")
        print(f"🔧 Needs work: {worst_viewport.get('viewport', {}).get('name', 'unknown')} "
              f"({worst_viewport.get('visual_diff', {}).get('similarity_score', 0)}%)")
    
    # Save results
    from pathlib import Path
    artifacts_dir = Path('.cursorflow/artifacts')
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = artifacts_dir / 'responsive_mockup_comparison_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Full results saved to: {results_file}")
    
    return results


async def main():
    """
    Run all mockup comparison examples
    """
    print("🚀 CursorFlow Mockup Comparison Examples")
    print("=" * 60)
    print("This demonstrates how to compare mockups with implementations")
    print("and iteratively improve UI matching.\n")
    
    try:
        # Run basic comparison
        await basic_mockup_comparison()
        
        # Run iterative matching
        await iterative_mockup_matching()
        
        # Run responsive comparison
        await responsive_mockup_comparison()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated JSON files for detailed analysis")
        print("2. Check .cursorflow/artifacts/ for visual diffs and screenshots")
        print("3. Apply the successful CSS changes to your actual codebase")
        print("4. Re-run comparisons to validate improvements")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Note: Replace the mockup URLs with your actual mockup URLs
    print("⚠️  Remember to update the mockup URLs in this example!")
    print("   Replace 'https://mockup.example.com/...' with your actual mockup URLs\n")
    
    asyncio.run(main())

"""Command-line interface for the C++ linter."""

import argparse
import csv
import subprocess
import sys
from pathlib import Path
from typing import List

from .__version__ import __version__
from .core.config import LinterConfig
from .core.engine import LintingEngine
from .core.severity import Severity


def get_changed_files_from_main() -> List[str]:
    """Get list of files changed in current branch compared to main."""
    try:
        changed_files = set()
        cpp_extensions = {'.h', '.hpp', '.hxx', '.cuh', '.cu', '.cpp', '.cc', '.cxx'}

        # Get committed changes compared to main branch
        result_committed = subprocess.run(
            ["git", "diff", "--name-only", "main...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )

        result_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Get unstaged changes
        result_unstaged = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Combine all changed files
        all_changed = (
            result_committed.stdout.strip().split('\n') +
            result_staged.stdout.strip().split('\n') +
            result_unstaged.stdout.strip().split('\n')
        )

        # Filter for C++ files and existing files
        for file_path in all_changed:
            if file_path:  # Skip empty lines
                path = Path(file_path)
                if path.suffix in cpp_extensions and path.exists():
                    changed_files.add(file_path)

        return sorted(list(changed_files))

    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files from git: {e}")
        print("Make sure you're in a git repository and 'main' branch exists.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: git command not found. Make sure git is installed.")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Modern C++ linter with configurable project-specific rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  niti --check src/
  niti --check csrc/ --config .niti.yaml
  niti --check-diff
  niti --list-rules
  niti --check src/ --disable-rule type-forbidden-int
  niti --check src/ --check-rule naming-function-case

Configuration:
  The linter uses .niti.yaml by default if present.
  All mandatory rules (ERROR/WARNING) are enabled by default.
  Optional rules (INFO) are disabled by default.
        """,
    )

    parser.add_argument(
        "paths", nargs="*", help="Paths to check (files or directories)"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check files without making changes",
    )

    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Alias for --check (backward compatibility)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues that have autofix support",
    )

    parser.add_argument(
        "--check-diff",
        action="store_true",
        help="Check only files changed in current branch compared to main",
    )

    parser.add_argument(
        "--config",
        default=".niti.yaml",
        help="Path to configuration file (default: .cpp-lint.yaml)",
    )

    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List all available rules and their status",
    )

    parser.add_argument(
        "--disable-rule",
        action="append",
        dest="disabled_rules",
        help="Disable a specific rule (can be used multiple times)",
    )

    parser.add_argument(
        "--enable-rule",
        action="append",
        dest="enabled_rules",
        help="Enable a specific rule (can be used multiple times)",
    )

    parser.add_argument(
        "--check-rule",
        help="Check only this specific rule (bypasses config file)",
    )

    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        help="Minimum severity level to report",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only show summary, not individual issues",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output including rule categories",
    )

    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export linting errors to linter_output.csv file",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"niti {__version__}",
        help="Show version information and exit",
    )

    # Plugin-related arguments
    plugin_group = parser.add_argument_group("Plugin Options")
    plugin_group.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all available plugins",
    )
    plugin_group.add_argument(
        "--plugin",
        action="append",
        dest="plugins",
        help="Enable specific plugin(s) (can be used multiple times)",
    )

    args = parser.parse_args()

    # Handle special commands
    if args.list_rules:
        list_rules(args.config)
        return

    if args.list_plugins:
        list_plugins()
        return

    # Handle --check-diff flag
    if args.check_diff:
        changed_files = get_changed_files_from_main()
        if not changed_files:
            print("✅ No C++ files changed compared to main branch.")
            return
        print(f"🔍 Found {len(changed_files)} changed C++ files compared to main:")
        for file_path in changed_files:
            print(f"  - {file_path}")
        print()
        args.paths = changed_files
        args.check = True  # Force check mode for diff

    # Validate arguments
    if (
        not args.paths
        and not args.check
        and not args.check_only
        and not args.fix
        and not args.check_diff
    ):
        parser.error("Must specify paths to check or use --list-rules")

    check_mode = args.check or args.check_only
    fix_mode = args.fix

    if not check_mode and not fix_mode:
        parser.error("Must use either --check, --fix, or --check-diff mode")

    # Load configuration
    if args.check_rule:
        # Single rule mode - create minimal config with only specified rule
        from .rules.registry import RuleId
        
        # Create sets for disabled and enabled rules
        all_rule_names = {rule_id.name for rule_id in RuleId}
        # Remove the target rule from disabled set
        disabled = all_rule_names - {args.check_rule.upper().replace("-", "_")}
        
        # Create config with all rules disabled except the specified one
        config = LinterConfig(
            disabled_rules=disabled,
            enabled_rules={args.check_rule}
        )
    else:
        # Normal mode - load from config file
        config = LinterConfig.load(args.config)

        # Apply command-line plugin overrides
        if args.plugins:
            # Override plugin configuration from command line
            if "plugins" not in config._config:
                config._config["plugins"] = {"enabled": [], "config": {}}
            config._config["plugins"]["enabled"] = args.plugins

        # Apply command-line rule overrides
        if args.disabled_rules:
            for rule in args.disabled_rules:
                config.disable_rule(rule)

        if args.enabled_rules:
            for rule in args.enabled_rules:
                config.enable_rule(rule)

    # Run the linter
    engine = LintingEngine(config)

    try:
        results = engine.lint_paths(args.paths, autofix=fix_mode)

        # Filter by severity if specified
        if args.severity:
            min_severity = Severity(args.severity)
            severity_order = [Severity.ERROR, Severity.WARNING, Severity.INFO]
            min_index = severity_order.index(min_severity)
            allowed_severities = severity_order[: min_index + 1]
            results = [
                issue
                for issue in results
                if issue.severity in allowed_severities
            ]

        # Export to CSV if requested
        if args.export_csv:
            export_to_csv(results)

        # Display results
        display_results(results, args.quiet, args.verbose)

        # Exit with appropriate code
        error_count = len([r for r in results if r.severity == Severity.ERROR])
        sys.exit(1 if error_count > 0 else 0)

    except KeyboardInterrupt:
        print("\\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_plugins() -> None:
    """List all available plugins."""
    from .plugins.loader import PluginLoader

    print("Available Niti Plugins:\n")

    loader = PluginLoader()
    available_plugins = loader.discover_plugins()

    if not available_plugins:
        print("No plugins found. Install plugins using pip.")
        print("Example: pip install niti-vajra-plugin")
    else:
        for plugin_name in sorted(available_plugins):
            print(f"  - {plugin_name}")

    print(
        "\nTo enable a plugin, add it to your .nitirc file or use --plugin flag"
    )


def list_rules(config_path: str) -> None:
    """List all available rules and their current status."""
    from .rules.plugin_registry import plugin_registry
    from .rules.registry import RuleId

    # Load config to see current settings
    config = LinterConfig.load(config_path)

    # Load plugins if configured
    if "plugins" in config._config:
        plugin_registry.load_plugins(config._config["plugins"])

    print("Available C++ Linter Rules:\n")

    # Group core rules by category
    categories = {}
    for rule_id in RuleId:
        category = rule_id.category
        if category not in categories:
            categories[category] = []
        categories[category].append(rule_id)

    # Display core rules
    print("=== CORE RULES ===")
    for category, rules in sorted(categories.items()):
        print(f"\n{category.upper()}:")
        for rule_id in sorted(rules, key=lambda r: r.name):
            enabled = plugin_registry.is_rule_enabled(rule_id)
            severity = plugin_registry.get_rule_severity(rule_id)
            status = "✓" if enabled else "✗"
            mandatory = "MANDATORY" if rule_id.is_mandatory else "OPTIONAL"

            print(
                f"  {status} {rule_id} ({severity.value.upper()}) - {mandatory}"
            )

    # Display plugin rules if any
    plugin_rules = plugin_registry.get_plugin_rules()
    if plugin_rules:
        print("\n=== PLUGIN RULES ===")
        # Group by plugin
        plugin_groups = {}
        for rule_id in plugin_rules:
            plugin_name = rule_id.split("/")[0]
            if plugin_name not in plugin_groups:
                plugin_groups[plugin_name] = []
            plugin_groups[plugin_name].append(rule_id)

        for plugin_name, rules in sorted(plugin_groups.items()):
            print(f"\n{plugin_name.upper()} PLUGIN:")
            for rule_id in sorted(rules):
                enabled = plugin_registry.is_rule_enabled(rule_id)
                severity = plugin_registry.get_severity_by_id(rule_id)
                status = "✓" if enabled else "✗"
                print(f"  {status} {rule_id} ({severity.value.upper()})")

    # Summary
    core_enabled = len(
        [r for r in RuleId if plugin_registry.is_rule_enabled(r)]
    )
    plugin_enabled = len(
        [r for r in plugin_rules if plugin_registry.is_rule_enabled(r)]
    )
    total_enabled = core_enabled + plugin_enabled
    total_count = len(list(RuleId)) + len(plugin_rules)

    print(
        f"\nEnabled: {total_enabled}/{total_count} rules (Core: {core_enabled}, Plugin: {plugin_enabled})"
    )


def export_to_csv(results: List, filename: str = "linter_output.csv") -> None:
    """Export linting results to a CSV file.
    
    Args:
        results: List of LintIssue objects
        filename: Name of the CSV file to write to
    """
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["rule_id", "file_path", "line_number", "column", "file_line_column_path", "message", "agent_friendly_message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for issue in results:
            writer.writerow({
                "rule_id": issue.rule_id,
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "column": issue.column,
                "file_line_column_path": f'{issue.file_path}:{issue.line_number}:{issue.column}',
                "message": issue.message,
                "agent_friendly_message": f'{issue.file_path}:{issue.line_number}:{issue.column} {issue.message}'
            })
    
    print(f"✅ Linting results exported to {filename}")


def display_results(results: List, quiet: bool, verbose: bool) -> None:
    """Display linting results."""
    if not results:
        print("✅ No issues found!")
        return

    # Group by severity
    errors = [r for r in results if r.severity == Severity.ERROR]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    infos = [r for r in results if r.severity == Severity.INFO]

    # Summary
    print(
        f"Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info"
    )

    if not quiet:
        # Display warnings first, then errors
        if warnings:
            print("\n⚠️  Warnings:\n")
            by_file = {}
            for issue in warnings:
                if issue.file_path not in by_file:
                    by_file[issue.file_path] = []
                by_file[issue.file_path].append(issue)

            for file_path in sorted(by_file.keys()):
                print(f"📁 {file_path}")
                for issue in sorted(by_file[file_path], key=lambda x: x.line_number):
                    print(
                        f"  {issue.severity.icon} {issue.line_number}:{issue.column} [{issue.rule_id}] {issue.file_path}:{issue.line_number}:{issue.column} {issue.message}"
                    )
                    if issue.suggested_fix and verbose:
                        print(f"    💡 Suggested fix: {issue.suggested_fix}")

        if errors:
            print("\n❌ Errors:\n")
            by_file = {}
            for issue in errors:
                if issue.file_path not in by_file:
                    by_file[issue.file_path] = []
                by_file[issue.file_path].append(issue)

            for file_path in sorted(by_file.keys()):
                print(f"📁 {file_path}")
                for issue in sorted(by_file[file_path], key=lambda x: x.line_number):
                    print(
                        f"  {issue.severity.icon} {issue.line_number}:{issue.column} [{issue.rule_id}] {issue.file_path}:{issue.line_number}:{issue.column} {issue.message}"
                    )
                    if issue.suggested_fix and verbose:
                        print(f"    💡 Suggested fix: {issue.suggested_fix}")

    # Rule count table
    if results:
        print("\n📊 Issues by Rule:")

        # Count issues by rule_id
        rule_counts = {}
        for issue in results:
            rule_id = str(issue.rule_id)
            if rule_id not in rule_counts:
                rule_counts[rule_id] = 0
            rule_counts[rule_id] += 1

        # Sort by count (descending) then by rule_id (ascending)
        sorted_rules = sorted(rule_counts.items(), key=lambda x: (-x[1], x[0]))

        # Calculate column widths
        max_rule_width = max(len(rule_id) for rule_id in rule_counts.keys())
        max_count_width = max(len(str(count)) for count in rule_counts.values())
        rule_col_width = max(max_rule_width, len("RULE_ID"))
        count_col_width = max(max_count_width, len("COUNT"))

        # Print table header
        header = f"{'RULE_ID':<{rule_col_width}} | {'COUNT':>{count_col_width}}"
        print(header)
        print("-" * len(header))

        # Print rule counts
        for rule_id, count in sorted_rules:
            print(f"{rule_id:<{rule_col_width}} | {count:>{count_col_width}}")
    else:
        print("\n📊 No issues to summarize.")

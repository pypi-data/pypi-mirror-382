#!/usr/bin/env python3
"""
Quick Security Test Runner for Postgres MCP Server
==================================================

This script provides a simplified way to run SQL injection security tests
against the Postgres MCP server, similar to our SQLite MCP server testing.

Usage:
    python run_security_test.py [--database-url URL] [--quick]

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    SKIP_CONFIRMATION: Set to 'true' to skip interactive confirmation

Author: Enhanced by neverinfamous
Date: September 28, 2025
"""

import argparse
import asyncio
import os
import sys
from typing import Dict
from typing import List

# Fix Windows event loop compatibility with psycopg3
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import from the current security directory
from test_sql_injection_security import PostgresSQLInjectionTester
from test_sql_injection_security import SecurityReport
from test_sql_injection_security import TestResult


def print_banner():
    """Print the security test banner"""
    print("=" * 80)
    print("POSTGRES MCP SERVER - SQL INJECTION SECURITY TEST SUITE")
    print("=" * 80)
    print()
    print("This comprehensive test suite validates security against:")
    print("   • Basic SQL Injection (UNION, stacked queries)")
    print("   • Blind SQL Injection (time-based, boolean-based)")
    print("   • Error-based SQL Injection")
    print("   • PostgreSQL-specific attacks (system functions, extensions)")
    print("   • Advanced bypass techniques")
    print("   • Parameter binding validation")
    print()
    print("Testing both UNRESTRICTED and RESTRICTED modes")
    print("WARNING: This creates test tables and data!")
    print()


async def run_quick_test(connection_url: str) -> SecurityReport:
    """Run a quick subset of critical security tests"""

    print("Running QUICK security test (critical vulnerabilities only)...")
    print("-" * 60)

    tester = PostgresSQLInjectionTester(connection_url)
    await tester.setup_test_environment()

    # Get only the most critical test cases
    all_tests = tester.get_injection_test_cases()
    critical_tests = [t for t in all_tests if t.security_level.value in ["critical", "high"]]

    print(f"Testing {len(critical_tests)} critical/high-severity attack vectors...")
    print("\nNOTE: Database errors during testing are expected and indicate the test framework")
    print("      is correctly attempting various attack vectors. The final VULN/SAFE results")
    print("      show whether each attack succeeded or was blocked.")

    results: Dict[str, List[TestResult]] = {}
    for mode in ["unrestricted", "restricted"]:
        print(f"\nTesting {mode.upper()} mode...")

        mode_results: List[TestResult] = []
        for i, test in enumerate(critical_tests, 1):
            print(f"  [{i:2d}/{len(critical_tests)}] {test.name[:50]}...")

            try:
                result = await tester.test_sql_injection(test, mode)
                mode_results.append(result)

                status = "VULN" if result.vulnerable else "SAFE"
                print(f"      {status}")

            except Exception as e:
                print(f"      ERROR: {str(e)[:50]}...")

        results[mode] = mode_results

    return tester.generate_security_report(results)


async def run_full_test(connection_url: str) -> SecurityReport:
    """Run the complete comprehensive security test suite"""

    print("Running COMPREHENSIVE security test suite...")
    print("-" * 60)

    tester = PostgresSQLInjectionTester(connection_url)
    return await tester.run_comprehensive_test_suite()


def print_summary_report(report: SecurityReport, test_type: str):
    """Print a concise summary report"""

    print("\n" + "=" * 80)
    print(f"{test_type.upper()} SECURITY TEST RESULTS")
    print("=" * 80)

    # Overall security posture
    score = report["security_score"]
    if score >= 90:
        score_text = "EXCELLENT"
    elif score >= 70:
        score_text = "GOOD"
    elif score >= 50:
        score_text = "NEEDS IMPROVEMENT"
    else:
        score_text = "CRITICAL ISSUES FOUND"

    print(f"\nOVERALL SECURITY SCORE: {score:.1f}/100 - {score_text}")

    # Mode comparison
    print("\nDETAILED RESULTS:")
    for mode, summary in report["summary"].items():
        vulnerable = summary["vulnerable"]
        total = summary["total_tests"]
        protected = summary["protected"]

        print(f"\n   {mode.upper()} MODE:")
        print(f"      Tests Run: {total}")
        print(f"      Vulnerable: {vulnerable}")
        print(f"      Protected: {protected}")
        print(f"      Success Rate: {summary['security_score']:.1f}%")

        # Vulnerability breakdown
        vulns = summary["vulnerabilities_by_severity"]
        if vulns["critical"] > 0:
            print(f"      Critical: {vulns['critical']}")
        if vulns["high"] > 0:
            print(f"      High: {vulns['high']}")
        if vulns["medium"] > 0:
            print(f"      Medium: {vulns['medium']}")

    # Key findings
    print("\nKEY FINDINGS:")

    unrestricted_vulns = report["summary"].get("unrestricted", {}).get("vulnerable", 0)
    restricted_vulns = report["summary"].get("restricted", {}).get("vulnerable", 0)

    if unrestricted_vulns > 0:
        print(f"   CRITICAL: {unrestricted_vulns} vulnerabilities in UNRESTRICTED mode")
        print("      - The execute_sql function is vulnerable to SQL injection")
        print("      - Same vulnerability as original Anthropic SQLite MCP server")
    else:
        print("   UNRESTRICTED mode: No vulnerabilities detected")

    if restricted_vulns == 0:
        print("   RESTRICTED mode: Successfully blocked all attacks")
        print("      - SafeSqlDriver provides effective protection")
    else:
        print(f"   RESTRICTED mode: {restricted_vulns} vulnerabilities found")

    # Recommendations
    if report["recommendations"]:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec['priority']}: {rec['issue']}")
            print(f"      {rec['solution']}")

    print("\n" + "=" * 80)
    print("\nTEST EXPLANATION:")
    print("- Database errors during testing are normal and expected")
    print("- These errors occur when the test framework attempts various SQL injection attacks")
    print("- The important results are the final VULNERABLE/PROTECTED counts above")
    print("- VULNERABLE means the attack succeeded, PROTECTED means it was blocked")


def main():
    """Main function"""

    parser = argparse.ArgumentParser(
        description="SQL Injection Security Test Suite for Postgres MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_security_test.py --quick
  python run_security_test.py --database-url postgresql://user:pass@localhost/testdb
  SKIP_CONFIRMATION=true python run_security_test.py --quick
        """,
    )

    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@host.docker.internal:5432/postgres"),
        help="PostgreSQL connection URL (default: from DATABASE_URL env var)",
    )

    parser.add_argument("--quick", action="store_true", help="Run quick test (critical vulnerabilities only)")

    parser.add_argument("--skip-banner", action="store_true", help="Skip the banner and go straight to testing")

    args = parser.parse_args()

    if not args.skip_banner:
        print_banner()

    # Show connection info (with password masked)
    masked_url = args.database_url
    if "@" in masked_url and ":" in masked_url:
        parts = masked_url.split("@")
        if len(parts) == 2:
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user, _ = user_pass.split(":", 1)
                masked_url = masked_url.replace(user_pass, f"{user}:****")

    print(f"Database: {masked_url}")
    print(f"Test Mode: {'QUICK' if args.quick else 'COMPREHENSIVE'}")

    # Confirmation
    if not os.environ.get("SKIP_CONFIRMATION") and not args.skip_banner:
        print("\nWARNING: This will create test tables in the target database!")
        response = input("Continue? (y/N): ")
        if response.lower() != "y":
            print("Testing cancelled.")
            return 1

    async def run_tests():
        try:
            if args.quick:
                report = await run_quick_test(args.database_url)
                test_type = "quick"
            else:
                report = await run_full_test(args.database_url)
                test_type = "comprehensive"

            print_summary_report(report, test_type)

            # Exit with appropriate code
            if report["security_score"] < 70:
                print("\nSECURITY ALERT: Critical vulnerabilities detected!")
                return 1
            else:
                print("\nSecurity assessment completed successfully.")
                return 0

        except Exception as e:
            print(f"\nSecurity testing failed: {e}")
            return 1

    # Run the async tests
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

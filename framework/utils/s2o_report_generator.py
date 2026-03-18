"""
S2O Test Report Generator

Generates a structured test report from pytest execution results.
Parses JUnit XML output and fills the S2O Test Report template.

Usage:
    # Run tests with JUnit XML output
    pytest tests/s2o/ -v --junitxml=reports/s2o_report.xml

    # Generate report from XML
    python -m framework.utils.s2o_report_generator

    # Or with custom paths
    python -m framework.utils.s2o_report_generator \
        --junit-xml reports/s2o_report.xml \
        --output reports/S2O_TEST_REPORT.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


def _find_framework_root() -> Path:
    """Locate faas_qa_automation root for template path."""
    # __file__ = faas_qa_automation/framework/utils/s2o_report_generator.py
    path = Path(__file__).resolve().parent  # framework/utils
    root = path.parent.parent  # faas_qa_automation
    if (root / "docs" / "S2O_TEST_REPORT_TEMPLATE.md").exists():
        return root
    return path.parent.parent


def parse_junit_xml(xml_path: str | Path) -> dict[str, Any]:
    """
    Parse pytest JUnit XML output into a structured dict.

    Returns:
        Dict with keys: total, passed, failed, skipped, error, duration,
        tests (list of test result dicts), failures (list of failure details)
    """
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()

    total = int(root.get("tests", 0))
    failures = int(root.get("failures", 0))
    errors = int(root.get("errors", 0))
    skipped = int(root.get("skipped", 0))
    passed = total - failures - errors - skipped
    duration = float(root.get("time", 0))

    tests: list[dict[str, Any]] = []
    failure_details: list[dict[str, Any]] = []
    skipped_details: list[dict[str, Any]] = []

    for testcase in root.findall(".//testcase"):
        name = testcase.get("name", "")
        classname = testcase.get("classname", "")
        time_val = float(testcase.get("time", 0))
        test_id = _extract_test_id(classname, name)

        failure = testcase.find("failure")
        err = testcase.find("error")
        skip = testcase.find("skipped")

        if failure is not None:
            status = "FAILED"
            failure_details.append({
                "test_id": test_id,
                "name": name,
                "message": failure.get("message", ""),
                "text": (failure.text or "").strip()[:500],
            })
        elif err is not None:
            status = "ERROR"
            failure_details.append({
                "test_id": test_id,
                "name": name,
                "message": err.get("message", ""),
                "text": (err.text or "").strip()[:500],
            })
        elif skip is not None:
            status = "SKIPPED"
            skipped_details.append({
                "test_id": test_id,
                "name": name,
                "reason": skip.get("message", "No reason"),
            })
        else:
            status = "PASSED"

        tests.append({
            "test_id": test_id,
            "name": name,
            "classname": classname,
            "status": status,
            "duration": time_val,
        })

    return {
        "total": total,
        "passed": passed,
        "failed": failures,
        "skipped": skipped,
        "error": errors,
        "duration": duration,
        "tests": tests,
        "failure_details": failure_details,
        "skipped_details": skipped_details,
    }


def _extract_test_id(classname: str, name: str) -> str:
    """Extract a short test ID for display (e.g. S2O-HC-001 or test name)."""
    match = re.search(r"(S2O-[A-Z]{2}-\d{3})", f"{classname} {name}")
    if match:
        return match.group(1)
    return name.split("::")[-1][:50] if name else "unknown"


def _group_tests_by_category(tests: list[dict]) -> dict[str, list[dict]]:
    """Group tests by category based on test_id prefix."""
    categories: dict[str, list[dict]] = {
        "health": [],
        "session": [],
        "document": [],
        "positive": [],
        "negative": [],
        "doc2data": [],
    }

    for t in tests:
        tid = t.get("test_id", "").upper()
        if "HC-" in tid or "health" in tid.lower():
            categories["health"].append(t)
        elif "SM-" in tid or "session" in tid.lower():
            categories["session"].append(t)
        elif "DU-" in tid or "document" in tid.lower():
            categories["document"].append(t)
        elif "PJ-" in tid or "positive" in tid.lower():
            categories["positive"].append(t)
        elif "NF-" in tid or "negative" in tid.lower():
            categories["negative"].append(t)
        elif "DD-" in tid or "doc2data" in tid.lower():
            categories["doc2data"].append(t)
        else:
            categories["health"].append(t)

    return categories


def _render_table_rows(tests: list[dict]) -> str:
    """Render test rows for a markdown table."""
    if not tests:
        return "| - | No tests | - | - |"
    lines = []
    for t in tests:
        tid = t.get("test_id", "-")
        name = (t.get("name", "-") or "-")[:60]
        status = t.get("status", "?")
        dur = f"{t.get('duration', 0):.3f}s"
        status_icon = "✅" if status == "PASSED" else "❌" if status in ("FAILED", "ERROR") else "⏭️"
        lines.append(f"| {tid} | {name} | {status_icon} {status} | {dur} |")
    return "\n".join(lines)


def generate_report(
    junit_xml_path: str | Path,
    output_path: str | Path | None = None,
    environment: str = "uat",
    base_url: str = "",
) -> str:
    """
    Generate S2O test report from JUnit XML.

    Args:
        junit_xml_path: Path to pytest JUnit XML output
        output_path: Path to write report (default: reports/S2O_TEST_REPORT.md)
        environment: Environment name (uat, dev, etc.)
        base_url: Base URL used for testing

    Returns:
        Generated report content as string
    """
    xml_path = Path(junit_xml_path)
    if not xml_path.exists():
        raise FileNotFoundError(f"JUnit XML not found: {xml_path}")

    data = parse_junit_xml(xml_path)
    categories = _group_tests_by_category(data["tests"])

    total = data["total"]
    passed = data["passed"]
    failed = data["failed"]
    skipped = data["skipped"]
    errors = data["error"]
    duration = data["duration"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    overall = "PASS" if (failed == 0 and errors == 0) else "FAIL"

    framework_root = _find_framework_root()
    template_path = framework_root / "docs" / "S2O_TEST_REPORT_TEMPLATE.md"
    if not template_path.exists():
        template_content = _default_template()
    else:
        template_content = template_path.read_text()

    failed_block = []
    for f in data["failure_details"]:
        failed_block.append(
            f"### {f['test_id']}\n**{f['name']}**\n```\n{f.get('message', '')}\n{f.get('text', '')}\n```"
        )
    failed_tests_detail = "\n\n".join(failed_block) if failed_block else "None"

    skipped_block = []
    for s in data["skipped_details"]:
        skipped_block.append(f"- **{s['test_id']}**: {s.get('reason', 'No reason')}")
    skipped_tests_detail = "\n".join(skipped_block) if skipped_block else "None"

    if overall == "FAIL":
        recommendations = (
            "1. Review failed tests and fix underlying issues.\n"
            "2. Check service health and UAT connectivity.\n"
            "3. Verify test data (PDFs, credentials) are correct."
        )
    else:
        recommendations = "All tests passed. No immediate action required."

    replacements = {
        "{{ report_id }}": str(uuid.uuid4())[:8],
        "{{ generated_at }}": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "{{ environment }}": environment,
        "{{ duration_seconds }}": f"{duration:.1f}",
        "{{ total_tests }}": str(total),
        "{{ passed_count }}": str(passed),
        "{{ failed_count }}": str(failed),
        "{{ skipped_count }}": str(skipped),
        "{{ error_count }}": str(errors),
        "{{ pass_rate_percent }}": f"{pass_rate:.1f}",
        "{{ overall_status }}": overall,
        "{{ orchestrator_version }}": "N/A",
        "{{ orchestrator_health }}": "N/A",
        "{{ orchestrator_tests }}": str(len(categories["health"]) + len(categories["session"])),
        "{{ doc2data_version }}": "N/A",
        "{{ doc2data_health }}": "N/A",
        "{{ doc2data_tests }}": str(len(categories["doc2data"])),
        "{{ truid_tests }}": "0",
        "{{ spike_tests }}": str(len(categories["positive"])),
        "{{ health_results_table }}": _render_table_rows(categories["health"]),
        "{{ session_results_table }}": _render_table_rows(categories["session"]),
        "{{ document_results_table }}": _render_table_rows(categories["document"]),
        "{{ positive_results_table }}": _render_table_rows(categories["positive"]),
        "{{ negative_results_table }}": _render_table_rows(categories["negative"]),
        "{{ doc2data_results_table }}": _render_table_rows(categories["doc2data"]),
        "{{ failed_tests_detail }}": failed_tests_detail,
        "{{ skipped_tests_detail }}": skipped_tests_detail,
        "{{ base_url }}": base_url or os.getenv("BASE_URL", "https://uat.api.rcdevops.co.za"),
        "{{ python_version }}": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "{{ pytest_version }}": _get_pytest_version(),
        "{{ recommendations }}": recommendations,
    }

    report = template_content
    for key, val in replacements.items():
        report = report.replace(key, str(val))

    out_path = Path(output_path) if output_path else Path("reports") / "S2O_TEST_REPORT.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    return report


def _get_pytest_version() -> str:
    try:
        import pytest
        return getattr(pytest, "__version__", "unknown")
    except ImportError:
        return "not installed"


def _default_template() -> str:
    return """# S2O Test Report
**Generated:** {{ generated_at }}
**Environment:** {{ environment }}

## Summary
- Total: {{ total_tests }}
- Passed: {{ passed_count }}
- Failed: {{ failed_count }}
- Pass Rate: {{ pass_rate_percent }}%

{{ failed_tests_detail }}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate S2O test report from pytest JUnit XML")
    parser.add_argument(
        "--junit-xml",
        default=os.getenv("JUNIT_XML", "reports/s2o_report.xml"),
        help="Path to JUnit XML from pytest",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("S2O_REPORT_OUTPUT", "reports/S2O_TEST_REPORT.md"),
        help="Output report path",
    )
    parser.add_argument(
        "--environment",
        default=os.getenv("ENVIRONMENT", "uat"),
        help="Environment name",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("BASE_URL", ""),
        help="Base URL used for tests",
    )
    args = parser.parse_args()

    try:
        generate_report(
            junit_xml_path=args.junit_xml,
            output_path=args.output,
            environment=args.environment,
            base_url=args.base_url,
        )
        print(f"Report generated: {args.output}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Run pytest with: pytest tests/s2o/ --junitxml=reports/s2o_report.xml", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

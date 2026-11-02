#!/usr/bin/env python3
"""Open evals runner for the Invoice Exception case study (contract: docs/EVALUATION.md).

Usage:
  python3 tools/run_evals.py --adapter "<command>" [--dataset dataset] [--cases case-001,case-010]
                             [--report-dir results/local] [--timeout 30] [--keep-state]

For every case the runner creates a fresh empty state directory and runs one adapter process per step:
  <command> --state-dir <dir>  < steps/step-NNN.json  > stdout
The output is validated against schemas/step-output.schema.json and compared with expected/step-NNN.json.
Exit code: 0 when every case passes, 1 otherwise, 2 on usage errors.
Requires: jsonschema>=4.18 (with referencing).
"""
import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match
from referencing import Registry, Resource

DECIMAL_LINE_FIELDS = (
    "calculated_net", "calculated_tax", "ordered", "received",
    "previously_invoiced", "available_to_invoice", "remaining_on_order",
)
EXACT_FIELDS = ("case_id", "step", "document_id", "context_version", "import_disposition",
                "original_document_id", "matched_order_id", "order_match_source", "decision")
STRICTNESS = {"clear": 0, "needs_review": 1, "needs_information": 2, "blocked": 3}


def load_validator(dataset):
    schemas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((dataset / "schemas").glob("*.schema.json"))]
    registry = Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas])
    output = next(s for s in schemas if s["$id"].endswith("/step-output.schema.json"))
    return Draft202012Validator(output, registry=registry)


def as_decimal(value):
    if value is None:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return value


def compare(expected, actual):
    """Returns a list of human-readable differences; empty means the step passed."""
    if "error" in expected:
        if "error" not in actual:
            return ["expected VALIDATION_ERROR, got a result"]
        return []
    if "error" in actual:
        return [f"unexpected VALIDATION_ERROR: {json.dumps(actual['error']['details'])[:300]}"]

    diffs = []
    for field in EXACT_FIELDS:
        if expected[field] != actual[field]:
            diffs.append(f"{field}: expected {expected[field]!r}, got {actual[field]!r}")

    exp_totals, act_totals = expected["totals"], actual["totals"]
    if (exp_totals is None) != (act_totals is None):
        diffs.append(f"totals: expected {exp_totals!r}, got {act_totals!r}")
    elif exp_totals is not None:
        for key, value in exp_totals.items():
            if as_decimal(value) != as_decimal(act_totals[key]):
                diffs.append(f"totals.{key}: expected {value}, got {act_totals[key]}")

    exp_lines = {l["document_line_id"]: l for l in expected["lines"]}
    act_lines = {}
    for line in actual["lines"]:
        if line["document_line_id"] in act_lines:
            diffs.append(f"lines: duplicate document_line_id {line['document_line_id']}")
        act_lines[line["document_line_id"]] = line
    for line_id in sorted(set(exp_lines) | set(act_lines)):
        exp, act = exp_lines.get(line_id), act_lines.get(line_id)
        if exp is None or act is None:
            diffs.append(f"lines: {line_id} {'unexpected' if exp is None else 'missing'}")
            continue
        for key in ("order_line_id", "match_source"):
            if exp[key] != act[key]:
                diffs.append(f"line {line_id}.{key}: expected {exp[key]!r}, got {act[key]!r}")
        for key in DECIMAL_LINE_FIELDS:
            if as_decimal(exp[key]) != as_decimal(act[key]):
                diffs.append(f"line {line_id}.{key}: expected {exp[key]}, got {act[key]}")

    def check_map(result):
        out = {}
        for c in result["checks"]:
            key = (c["code"], c["object_id"])
            if key in out:
                diffs.append(f"checks: duplicate {key[0]}/{key[1]}")
            out[key] = (c["status"], c["severity"], c["depends_on"])
        return out

    exp_checks, act_checks = check_map(expected), check_map(actual)
    for key in sorted(set(exp_checks) | set(act_checks)):
        name = f"{key[0]}/{key[1]}"
        if key not in act_checks:
            diffs.append(f"check {name}: missing")
        elif key not in exp_checks:
            diffs.append(f"check {name}: unexpected")
        elif exp_checks[key] != act_checks[key]:
            fmt = lambda t: f"status={t[0]} severity={t[1]} depends_on={t[2]}"
            diffs.append(f"check {name}: expected {fmt(exp_checks[key])}, got {fmt(act_checks[key])}")

    questions = lambda r: Counter((q["required_fact"], tuple(sorted(q["target_object_ids"]))) for q in r["questions"])
    if questions(expected) != questions(actual):
        diffs.append(f"questions: expected {sorted(questions(expected).elements())}, "
                     f"got {sorted(questions(actual).elements())}")
    return diffs


def schema_failure(validator, output):
    """Validates against the result or error branch directly, so the message points at the real field."""
    if not validator.is_valid(output):
        branch = "validation_error" if isinstance(output, dict) and "error" in output else "result"
        sub = validator.evolve(schema={"$ref": f"{validator.schema['$id']}#/$defs/{branch}"})
        errors = sorted(sub.iter_errors(output), key=lambda e: (len(e.absolute_path), list(map(str, e.absolute_path))))
        if not errors:
            return "output violates step-output schema"
        e = best_match(errors)
        return f"output violates step-output schema at /{'/'.join(map(str, e.absolute_path))}: {e.message[:200]}"
    return None


def outcome_label(result):
    if result is None:
        return None
    if "error" in result:
        return "validation_error"
    if result["import_disposition"] == "duplicate":
        return "duplicate"
    return result["decision"]


def run_step(command, state_dir, input_path, timeout):
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command + ["--state-dir", str(state_dir)],
            input=input_path.read_bytes(), capture_output=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s", "", time.monotonic() - started
    except OSError as e:
        return None, f"cannot start adapter: {e}", "", time.monotonic() - started
    elapsed = time.monotonic() - started
    stderr = proc.stderr.decode("utf-8", "replace")[-2000:]
    if proc.returncode not in (0, 2):
        return None, f"exit code {proc.returncode}", stderr, elapsed
    try:
        output = json.loads(proc.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, f"stdout is not one JSON document: {e}", stderr, elapsed
    if (proc.returncode == 2) != ("error" in output if isinstance(output, dict) else False):
        return None, f"exit code {proc.returncode} does not match output kind", stderr, elapsed
    return output, None, stderr, elapsed


def run_case(case_dir, command, validator, timeout, state_root, keep_state):
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    state_dir = Path(tempfile.mkdtemp(prefix=f"{case['case_id']}-", dir=state_root))
    steps, last_revision = [], None
    for step in case["steps"]:
        expected = json.loads((case_dir / step["expected"]).read_text(encoding="utf-8"))
        output, failure, stderr, elapsed = run_step(command, state_dir, case_dir / step["input"], timeout)
        diffs = []
        if failure is None:
            failure = schema_failure(validator, output)
        if failure is None:
            diffs = compare(expected, output)
            if "error" not in output:
                revision = output["input_revision"]
                if last_revision is not None and revision <= last_revision:
                    diffs.append(f"input_revision must increase: previous {last_revision}, got {revision}")
                last_revision = revision
        exp_label, act_label = outcome_label(expected), outcome_label(output) if failure is None else None
        steps.append({
            "step": step["step"],
            "passed": failure is None and not diffs,
            "adapter_failure": failure,
            "differences": diffs,
            "expected_outcome": exp_label,
            "actual_outcome": act_label,
            "critical_false_clear": act_label == "clear" and exp_label != "clear",
            "escalation": escalation(exp_label, act_label),
            "seconds": round(elapsed, 3),
            "stderr_tail": stderr if (failure or diffs) else "",
        })
    if not keep_state:
        shutil.rmtree(state_dir, ignore_errors=True)
    return {"case_id": case["case_id"], "passed": all(s["passed"] for s in steps), "steps": steps,
            "state_dir": str(state_dir) if keep_state else None}


def escalation(expected, actual):
    if expected in STRICTNESS and actual in STRICTNESS:
        if STRICTNESS[actual] > STRICTNESS[expected]:
            return "over"
        if STRICTNESS[actual] < STRICTNESS[expected]:
            return "under"
    return None


def summarize(cases):
    steps = [s for c in cases for s in c["steps"]]
    return {
        "cases_passed": sum(c["passed"] for c in cases),
        "cases_total": len(cases),
        "steps_passed": sum(s["passed"] for s in steps),
        "steps_total": len(steps),
        "critical_false_clear": sum(s["critical_false_clear"] for s in steps),
        "over_escalation": sum(s["escalation"] == "over" for s in steps),
        "under_escalation": sum(s["escalation"] == "under" for s in steps),
        "adapter_failures": sum(s["adapter_failure"] is not None for s in steps),
    }


def text_report(cases, summary):
    lines = []
    for case in cases:
        lines.append(f"{case['case_id']}  {'PASS' if case['passed'] else 'FAIL'}")
        for s in case["steps"]:
            if s["passed"]:
                continue
            tags = []
            if s["critical_false_clear"]:
                tags.append("CRITICAL: false clear")
            if s["escalation"]:
                tags.append(f"{s['escalation']}-escalation")
            head = f"  step {s['step']}: expected {s['expected_outcome']}, got {s['actual_outcome']}"
            lines.append(head + (f"  [{', '.join(tags)}]" if tags else ""))
            if s["adapter_failure"]:
                lines.append(f"    adapter failure: {s['adapter_failure']}")
            for d in s["differences"][:8]:
                lines.append(f"    - {d}")
            if len(s["differences"]) > 8:
                lines.append(f"    ... {len(s['differences']) - 8} more differences in the JSON report")
    lines.append("")
    lines.append(
        f"Cases {summary['cases_passed']}/{summary['cases_total']}, steps {summary['steps_passed']}/{summary['steps_total']}. "
        f"Critical false clear: {summary['critical_false_clear']}. "
        f"Over-escalation: {summary['over_escalation']}. Under-escalation: {summary['under_escalation']}. "
        f"Adapter failures: {summary['adapter_failures']}."
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--adapter", required=True, help="adapter command, e.g. \"python3 -m myapp.adapter\"")
    parser.add_argument("--dataset", type=Path, default=Path("dataset"))
    parser.add_argument("--cases", help="comma-separated case ids; default: all")
    parser.add_argument("--report-dir", type=Path, default=Path("results/local"))
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds per step")
    parser.add_argument("--keep-state", action="store_true", help="keep per-case state directories for debugging")
    args = parser.parse_args()

    command = shlex.split(args.adapter)
    if not command:
        parser.error("--adapter is empty")
    case_dirs = sorted(p for p in (args.dataset / "cases").glob("case-*") if (p / "case.json").exists())
    if args.cases:
        wanted = {c.strip() for c in args.cases.split(",") if c.strip()}
        unknown = wanted - {p.name for p in case_dirs}
        if unknown:
            parser.error(f"unknown cases: {', '.join(sorted(unknown))}")
        case_dirs = [p for p in case_dirs if p.name in wanted]
    if not case_dirs:
        parser.error(f"no cases found in {args.dataset}")

    validator = load_validator(args.dataset)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    state_root = args.report_dir / "state"
    state_root.mkdir(exist_ok=True)

    cases = [run_case(d, command, validator, args.timeout, state_root, args.keep_state) for d in case_dirs]
    summary = summarize(cases)
    report = {"schema_version": "1.0", "adapter": args.adapter, "dataset": str(args.dataset),
              "summary": summary, "cases": cases}
    (args.report_dir / "eval-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
    text = text_report(cases, summary)
    (args.report_dir / "eval-report.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"Reports: {args.report_dir / 'eval-report.json'}, {args.report_dir / 'eval-report.txt'}")
    return 0 if summary["cases_passed"] == summary["cases_total"] else 1


if __name__ == "__main__":
    sys.exit(main())

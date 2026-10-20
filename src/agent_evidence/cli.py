"""Command line interface for a trace audit."""
import argparse
import json
from pathlib import Path
import sys

from agent_evidence.core import InvalidTrace, audit_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit evidence declarations in agent execution traces.")
    parser.add_argument("dataset", type=Path, help="Path to a JSON file containing a runs array.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    parser.add_argument("--manifest", type=Path, help="Optional integrity manifest for local artifacts.")
    parser.add_argument("--artifact-root", type=Path, help="Directory holding the declared artifacts.")
    parser.add_argument("--junit", type=Path, help="Optional JUnit XML containing declared test results.")
    parser.add_argument("--study", type=Path, help="Optional independently adjudicated study dataset JSON.")
    args = parser.parse_args()
    try:
        data = json.loads(args.dataset.read_text(encoding="utf-8"))
        report = audit_dataset(data)
        if args.manifest:
            from agent_evidence.artifacts import verify_manifest

            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            artifact_root = args.artifact_root if args.artifact_root else args.manifest.parent
            report["artifact_integrity"] = verify_manifest(artifact_root, manifest)
        elif args.artifact_root:
            parser.error("--artifact-root requires --manifest")
        if args.junit:
            from agent_evidence.junit import summarize_junit
            report["junit_xml"] = summarize_junit(args.junit)
        if args.study:
            from agent_evidence.study import describe_study
            study_data = json.loads(args.study.read_text(encoding="utf-8"))
            report["study_descriptives"] = describe_study(study_data)
    except (OSError, ValueError, InvalidTrace) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 2
    formatted = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(formatted, encoding="utf-8")
    else:
        print(formatted, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

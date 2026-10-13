#!/usr/bin/env python3
"""Dependency-free checks for the profile README, assets, checklist, and workflows."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHECKLIST = ROOT / "PROFILE_IMPLEMENTATION_CHECKLIST.md"
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))

REQUIRED_TECH = [
    "C++", "Python", "C", "JavaScript", "TypeScript", "Java", "SQL", "HTML", "CSS",
    "PyTorch", "TensorFlow", "NumPy", "Pandas", "Scikit-learn", "OpenCV", "YOLO",
    "YOLOv8", "ByteTrack", "Hugging Face", "Transformers", "Large Language Models",
    "Generative AI", "prompt engineering", "Retrieval-Augmented Generation (RAG)",
    "embeddings", "vector databases", "agentic AI", "AI agents", "OpenAI API", "Gemini API",
    "Node.js", "Express.js", "React", "PostgreSQL", "MongoDB", "Redis", "Git", "GitHub",
    "Docker", "Linux", "Jupyter Notebook", "Visual Studio Code", "GitHub Actions",
    "AI deployment", "model inference", "model evaluation", "production-oriented AI systems",
    "computer vision pipelines", "data processing", "real-time detection pipelines",
]


class FragmentParser(HTMLParser):
    """HTMLParser catches malformed character references and parser exceptions."""


def report(ok: bool, message: str) -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {message}")
    return ok


def local_references(markdown: str) -> list[str]:
    refs: list[str] = []
    refs.extend(re.findall(r"\]\((\.{1,2}/[^)#\s]+)", markdown))
    refs.extend(re.findall(r"\bsrc=[\"'](\.{1,2}/[^\"']+)[\"']", markdown, re.I))
    return refs


def main() -> int:
    failures = 0
    warnings = 0
    if not report(README.is_file(), "README.md exists"):
        return 1
    markdown = README.read_text(encoding="utf-8")

    if not report(CHECKLIST.is_file(), "implementation checklist exists"):
        failures += 1
    if not report((ROOT / "PROFILE_MAINTENANCE.md").is_file(), "maintenance guide exists"):
        failures += 1
    if not report((ROOT / "assets" / "terminal-hero.svg").is_file(), "terminal hero asset exists"):
        failures += 1

    missing_tech = [name for name in REQUIRED_TECH if name.casefold() not in markdown.casefold()]
    if not report(not missing_tech, "full requested stack is represented"):
        failures += 1
        print("  Missing: " + ", ".join(missing_tech))

    refs = local_references(markdown)
    missing_refs = [ref for ref in refs if not (ROOT / ref).is_file()]
    if not report(not missing_refs, "local README file and asset references resolve"):
        failures += 1
        print("  Missing: " + ", ".join(missing_refs))

    start = markdown.count("<!-- OSS_START -->")
    end = markdown.count("<!-- OSS_END -->")
    if not report(start == 1 and end == 1 and markdown.index("<!-- OSS_START -->") < markdown.index("<!-- OSS_END -->"),
                  "open-source updater markers occur once and in order"):
        failures += 1

    headings = [re.sub(r"[`*_]", "", line.lstrip("#").strip()).casefold()
                for line in markdown.splitlines() if re.match(r"^#{1,6}\s", line)]
    duplicate_headings = sorted({h for h in headings if headings.count(h) > 1})
    if not report(not duplicate_headings, "README headings are not duplicated"):
        failures += 1
        print("  Duplicates: " + ", ".join(duplicate_headings))

    fence_count = sum(1 for line in markdown.splitlines() if line.startswith("```") or line.startswith("~~~"))
    if not report(fence_count % 2 == 0, "Markdown code fences are balanced"):
        failures += 1

    parser = FragmentParser(convert_charrefs=True)
    try:
        parser.feed(markdown)
        parser.close()
        html_ok = True
    except Exception as exc:  # HTMLParser raises for malformed references and encoding issues.
        html_ok = False
        print(f"  HTML parser: {exc}")
    if not report(html_ok, "embedded HTML fragments can be tokenized"):
        failures += 1

    svg_paths = sorted((ROOT / "assets").glob("*.svg"))
    svg_errors = []
    for svg in svg_paths:
        try:
            ET.parse(svg)
        except (ET.ParseError, OSError) as exc:
            svg_errors.append(f"{svg.relative_to(ROOT)}: {exc}")
    if not report(bool(svg_paths) and not svg_errors, "all repository SVG assets are well-formed XML"):
        failures += 1
        print("  " + "; ".join(svg_errors))

    if CHECKLIST.is_file():
        lines = CHECKLIST.read_text(encoding="utf-8").splitlines()
        rows = [re.match(r"^- \[([ x~!])\] (\d{3})\. .+$", line) for line in lines]
        parsed = [row.groups() for row in rows if row]
        expected = [f"{i:03d}" for i in range(1, 121)]
        ids = [item[1] for item in parsed]
        checklist_ok = ids == expected and len(parsed) == 120
        if not report(checklist_ok, "checklist contains each requirement 001–120 exactly once"):
            failures += 1
        counts = {status: sum(1 for item in parsed if item[0] == status) for status in "x~! "}
        if not report(sum(counts.values()) == 120, "checklist status counts total 120"):
            failures += 1
        print(f"  Checklist counts: verified={counts['x']}, partial={counts['~']}, blocked={counts['!']}, not implemented={counts[' ']}")

    pinned = re.compile(r"^\s*uses:\s+[^\s@]+@([0-9a-fA-F]{40})(?:\s+#.*)?\s*$", re.M)
    if not WORKFLOWS:
        failures += not report(False, "GitHub Actions workflows exist")
    for workflow in WORKFLOWS:
        content = workflow.read_text(encoding="utf-8")
        uses_lines = re.findall(r"^\s*uses:.*$", content, re.M)
        all_pinned = len(uses_lines) > 0 and len(pinned.findall(content)) == len(uses_lines)
        if not report(all_pinned, f"{workflow.relative_to(ROOT)} pins every action to a full SHA"):
            failures += 1
        if "permissions:" not in content or "write-all" in content:
            report(False, f"{workflow.relative_to(ROOT)} declares scoped permissions")
            failures += 1

    snake_path = ROOT / ".github" / "workflows" / "snake.yml"
    if snake_path.is_file():
        snake = snake_path.read_text(encoding="utf-8")
        snake_ok = all(value in snake for value in (
            "github_user_name: DevanshSinghBais", "publish_branch: output",
            "dist/github-snake.svg", "dist/github-snake-dark.svg",
            "if: github.ref == 'refs/heads/main'", "contents: write", "workflow_dispatch:",
        ))
        if not report(snake_ok, "snake workflow has the expected username, paths, branch, and guard"):
            failures += 1

    if shutil.which("actionlint"):
        result = subprocess.run(["actionlint", *map(str, WORKFLOWS)], cwd=ROOT, text=True, capture_output=True)
        if not report(result.returncode == 0, "actionlint validates workflow syntax"):
            failures += 1
            print(result.stdout + result.stderr)
    else:
        warnings += 1
        print("WARN actionlint is not installed; workflow YAML received structural review only")

    print(f"Validation result: {failures} failure(s), {warnings} warning(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

import json

import validate_skill as vs


def codes(findings, level=None):
    return {f.code for f in findings if level is None or f.level == level}


def test_repository_bundle_is_valid(root):
    findings = vs.validate(root)
    assert [f for f in findings if f.level == "error"] == []
    assert vs.main(["--root", str(root), "--strict"]) == 0


def test_frontmatter_parse_ok():
    meta, problem = vs.parse_frontmatter("---\nname: a-b\ndescription: hello: world\n---\nbody")
    assert problem is None
    assert meta == {"name": "a-b", "description": "hello: world"}


def test_frontmatter_missing():
    _, problem = vs.parse_frontmatter("# no frontmatter")
    assert problem


def test_frontmatter_unclosed():
    _, problem = vs.parse_frontmatter("---\nname: a\n")
    assert problem


def test_links_inside_code_fences_are_ignored():
    text = "[ok](a.md)\n```\n[x](missing.md)\n```\n[web](https://example.com)\n[anchor](#top)"
    assert vs.local_links(text) == ["a.md"]


def test_missing_description_is_error(make_bundle):
    bundle = make_bundle()
    skill = bundle / "SKILL.md"
    lines = [ln for ln in skill.read_text().splitlines() if not ln.startswith("description:")]
    skill.write_text("\n".join(lines) + "\n")
    assert "S005" in codes(vs.validate(bundle), "error")


def test_bad_name_is_error(make_bundle):
    bundle = make_bundle()
    skill = bundle / "SKILL.md"
    skill.write_text(
        skill.read_text().replace("name: activitypub-engineering", "name: Bad_Name", 1)
    )
    assert "S004" in codes(vs.validate(bundle), "error")


def test_long_description_is_error(make_bundle):
    bundle = make_bundle()
    skill = bundle / "SKILL.md"
    text = skill.read_text()
    start = text.index("description:")
    end = text.index("\n", start)
    skill.write_text(text[:start] + "description: " + "x" * 1100 + text[end:])
    assert "S006" in codes(vs.validate(bundle), "error")


def test_line_budget_is_enforced(make_bundle):
    bundle = make_bundle()
    skill = bundle / "SKILL.md"
    skill.write_text(skill.read_text() + "\nfiller\n" * (vs.MAX_SKILL_LINES + 5))
    assert "S007" in codes(vs.validate(bundle), "error")


def test_unrouted_reference_is_error(make_bundle):
    bundle = make_bundle()
    (bundle / "references" / "orphan.md").write_text("# Orphan\n")
    assert "S011" in codes(vs.validate(bundle), "error")


def test_broken_link_is_error(make_bundle):
    bundle = make_bundle()
    (bundle / "docs" / "SKILL_CONTRACT.md").write_text("# X\n\n[gone](missing.md)\n")
    assert "S020" in codes(vs.validate(bundle), "error")


def test_missing_required_file(make_bundle):
    bundle = make_bundle()
    (bundle / "CHANGELOG.md").unlink()
    assert "S001" in codes(vs.validate(bundle), "error")


def test_invalid_trigger_case(make_bundle):
    bundle = make_bundle()
    (bundle / "evals" / "trigger_cases.json").write_text(
        json.dumps([{"prompt": "x", "expect": "maybe"}])
    )
    assert "S032" in codes(vs.validate(bundle), "error")


def test_trigger_cases_cover_all_expectations(root):
    cases = json.loads((root / "evals" / "trigger_cases.json").read_text())
    assert {c["expect"] for c in cases} == {"activate", "not_activate", "handoff"}

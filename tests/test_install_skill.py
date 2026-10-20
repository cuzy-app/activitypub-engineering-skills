import install_skill as inst
import pytest


def test_dry_run_writes_nothing(root, tmp_path):
    target = inst.destination("claude", None, tmp_path)
    message = inst.install(root, target, force=False, dry_run=True)
    assert "would create" in message
    assert not target.exists()


def test_install_copies_knowledge_only_bundle(root, tmp_path):
    target = inst.destination("claude", None, tmp_path)
    inst.install(root, target, force=False, dry_run=False)
    assert (target / "SKILL.md").is_file()
    assert (target / "references" / "concepts.md").is_file()
    assert (target / "scripts" / "validate_activitypub.py").is_file()
    assert not (target / "scripts" / "install_skill.py").exists()
    assert not (target / "tests").exists()


def test_existing_install_requires_force(root, tmp_path):
    target = inst.destination("claude", None, tmp_path)
    inst.install(root, target, force=False, dry_run=False)
    with pytest.raises(FileExistsError):
        inst.install(root, target, force=False, dry_run=False)


def test_force_replaces_and_leaves_no_staging(root, tmp_path):
    target = inst.destination("claude", None, tmp_path)
    inst.install(root, target, force=False, dry_run=False)
    (target / "stale.txt").write_text("old")
    inst.install(root, target, force=True, dry_run=False)
    assert not (target / "stale.txt").exists()
    assert sorted(p.name for p in target.parent.iterdir()) == [inst.SKILL_NAME]


def test_failed_install_keeps_old_copy(root, tmp_path):
    target = inst.destination("claude", None, tmp_path)
    inst.install(root, target, force=False, dry_run=False)
    (target / "marker.txt").write_text("keep")
    broken = tmp_path / "broken-source"
    broken.mkdir()
    with pytest.raises(FileNotFoundError):
        inst.install(broken, target, force=True, dry_run=False)
    assert (target / "marker.txt").read_text() == "keep"


def test_project_scope_path(tmp_path):
    target = inst.destination("codex", tmp_path, None)
    assert target == tmp_path / ".codex" / "skills" / inst.SKILL_NAME


def test_cli_dry_run(root, tmp_path, capsys):
    code = inst.main(["--dest", str(tmp_path), "--dry-run", "--source", str(root)])
    assert code == 0
    assert "dry run" in capsys.readouterr().out
    assert not (tmp_path / inst.SKILL_NAME).exists()

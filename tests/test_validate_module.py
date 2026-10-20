import validate_module as vm


def codes(findings, level=None):
    return {f.code for f in findings if level is None or f.level == level}


def test_example_module_is_clean(root):
    findings = vm.validate(root / "examples" / "minimal-module")
    assert findings == []
    assert vm.main([str(root / "examples" / "minimal-module"), "--strict"]) == 0


def test_valid_generated_module_passes(make_module):
    assert codes(vm.validate(make_module()), "error") == set()


def test_missing_directory(tmp_path):
    assert codes(vm.validate(tmp_path / "nope")) == {"E000"}


def test_missing_manifest(make_module):
    module = make_module()
    (module / "module.json").unlink()
    assert "E001" in codes(vm.validate(module))


def test_invalid_json(make_module):
    module = make_module()
    (module / "module.json").write_text("{not json")
    assert "E002" in codes(vm.validate(module))


def test_missing_required_key(make_module):
    module = make_module({"description": None})
    assert "E003" in codes(vm.validate(module))


def test_uppercase_id_rejected(make_module):
    module = make_module({"id": "Demo"})
    assert "E004" in codes(vm.validate(module))


def test_bad_version(make_module):
    module = make_module({"version": "one"})
    assert "E005" in codes(vm.validate(module))


def test_missing_min_version(make_module):
    module = make_module({"humhub": {}})
    assert "E006" in codes(vm.validate(module))


def test_config_id_mismatch(make_module):
    module = make_module(
        config="<?php\nreturn ['id' => 'other', 'class' => 'X', 'namespace' => 'x'];\n"
    )
    assert "E013" in codes(vm.validate(module))


def test_config_missing_entries(make_module):
    module = make_module(config="<?php\nreturn [];\n")
    assert {"E012", "E014", "E015"} <= codes(vm.validate(module))


def test_missing_module_and_config_files(make_module):
    module = make_module()
    (module / "Module.php").unlink()
    (module / "config.php").unlink()
    assert {"E010", "E011"} <= codes(vm.validate(module))


def test_bad_migration_file_name(make_module):
    module = make_module(migrations={"create_table.php": "<?php\nclass create_table {}\n"})
    assert "E020" in codes(vm.validate(module))


def test_migration_class_must_match_file(make_module):
    module = make_module(migrations={"m260101_000000_a.php": "<?php\nclass m260101_000000_b {}\n"})
    assert "E022" in codes(vm.validate(module))


def test_migration_without_class(make_module):
    module = make_module(migrations={"m260101_000000_a.php": "<?php\n"})
    assert "E021" in codes(vm.validate(module))


def test_valid_migration_passes(make_module):
    module = make_module(migrations={"m260101_000000_a.php": "<?php\nclass m260101_000000_a {}\n"})
    assert codes(vm.validate(module), "error") == set()


def test_sql_interpolation_warns(make_module):
    module = make_module(
        extra_php={"Svc.php": '<?php\n$x = $db->createCommand("SELECT * FROM t WHERE id = $id");\n'}
    )
    assert "W010" in codes(vm.validate(module), "warning")


def test_where_interpolation_warns(make_module):
    module = make_module(extra_php={"Q.php": "<?php\n$q->andWhere(\"name = '$name'\");\n"})
    assert "W010" in codes(vm.validate(module), "warning")


def test_parameter_binding_does_not_warn(make_module):
    module = make_module(
        extra_php={
            "Svc.php": "<?php\n$db->createCommand('SELECT 1 WHERE id = :id', [':id' => $id]);\n"
        }
    )
    assert "W010" not in codes(vm.validate(module))


def test_wrong_composer_type_warns(make_module):
    module = make_module()
    (module / "composer.json").write_text('{"type": "library"}')
    assert "W030" in codes(vm.validate(module), "warning")


def test_strict_turns_warnings_into_failure(make_module):
    module = make_module()
    (module / "composer.json").write_text('{"type": "library"}')
    assert vm.main([str(module)]) == 0
    assert vm.main([str(module), "--strict"]) == 1


def test_errors_set_exit_status(make_module):
    module = make_module({"version": "x"})
    assert vm.main([str(module)]) == 1

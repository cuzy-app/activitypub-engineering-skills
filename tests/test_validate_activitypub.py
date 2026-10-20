import copy

import validate_activitypub as va
from conftest import ACTOR, PUBLIC


def codes(findings, level=None):
    return {f.code for f in findings if level is None or f.level == level}


def check(write_doc, doc):
    return codes(va.validate([write_doc(doc)]))


def test_example_documents_are_clean(root):
    findings = va.validate([root / "examples" / "documents"])
    assert findings == []
    assert va.main([str(root / "examples" / "documents"), "--strict"]) == 0


def test_valid_fixtures_pass(write_doc, person, create_note):
    assert check(write_doc, person) == set()
    assert check(write_doc, create_note) == set()


def test_missing_path():
    assert codes(va.validate([va.Path("/nonexistent/doc.json")])) == {"E000"}


def test_invalid_json(write_doc):
    assert check(write_doc, "{not json") == {"E001"}


def test_non_object(write_doc):
    assert check(write_doc, "[]") == {"E002"}


def test_missing_type_and_id(write_doc):
    assert {"E003"} <= check(write_doc, {"@context": va.AS_CONTEXT, "id": ACTOR})
    assert "E004" in check(write_doc, {"@context": va.AS_CONTEXT, "type": "Note"})


def test_relative_id_rejected(write_doc):
    assert "E005" in check(write_doc, {"@context": va.AS_CONTEXT, "id": "/n/1", "type": "Note"})


def test_http_id_warns(write_doc):
    doc = {"@context": va.AS_CONTEXT, "id": "http://a.example/n/1", "type": "Note"}
    assert "W003" in check(write_doc, doc)


def test_context_warnings(write_doc, create_note):
    doc = copy.deepcopy(create_note)
    del doc["@context"]
    assert "W001" in check(write_doc, doc)
    doc["@context"] = "https://example.com/other"
    assert "W002" in check(write_doc, doc)


def test_activity_without_actor(write_doc, create_note):
    del create_note["actor"]
    assert "E010" in check(write_doc, create_note)


def test_embedded_actor_warns(write_doc, create_note):
    create_note["actor"] = {"id": ACTOR, "type": "Person"}
    assert "W011" in check(write_doc, create_note)


def test_object_and_target_required(write_doc):
    follow = {"@context": va.AS_CONTEXT, "id": ACTOR + "/f/1", "type": "Follow", "actor": ACTOR}
    assert "E012" in check(write_doc, follow)
    add = dict(follow, type="Add", object=ACTOR + "/notes/1")
    assert "E013" in check(write_doc, add)


def test_activity_origin_must_match_actor(write_doc, create_note):
    create_note["id"] = "https://evil.example/activity/1"
    assert "E014" in check(write_doc, create_note)


def test_embedded_object_origin_must_match(write_doc, create_note):
    create_note["object"]["id"] = "https://b.example/notes/1"
    assert "E015" in check(write_doc, create_note)


def test_attributed_to_must_match_actor(write_doc, create_note):
    create_note["object"]["attributedTo"] = "https://a.example/users/mallory"
    assert "E016" in check(write_doc, create_note)


def test_bto_bcc_warn(write_doc, create_note):
    create_note["bcc"] = ["https://b.example/users/bob"]
    assert "W016" in check(write_doc, create_note)


def test_short_public_warns(write_doc, create_note):
    create_note["to"] = ["as:Public"]
    assert "W017" in check(write_doc, create_note)


def test_update_of_other_actor(write_doc, person):
    other = dict(person, id="https://a.example/users/bob")
    update = {
        "@context": va.AS_CONTEXT,
        "id": ACTOR + "#updates/1",
        "type": "Update",
        "actor": ACTOR,
        "object": other,
    }
    assert "E017" in check(write_doc, update)


def test_update_note_without_updated_warns(write_doc, create_note):
    create_note["type"] = "Update"
    assert "W020" in check(write_doc, create_note)
    create_note["object"]["updated"] = "2026-10-20T13:00:00Z"
    assert "W020" not in check(write_doc, create_note)


def test_undo_actor_must_match(write_doc):
    undo = {
        "@context": va.AS_CONTEXT,
        "id": ACTOR + "/undo/1",
        "type": "Undo",
        "actor": ACTOR,
        "object": {
            "id": "https://b.example/like/1",
            "type": "Like",
            "actor": "https://b.example/u",
        },
    }
    assert "E018" in check(write_doc, undo)


def test_accept_needs_follow_id(write_doc):
    accept = {
        "@context": va.AS_CONTEXT,
        "id": ACTOR + "/accept/1",
        "type": "Accept",
        "actor": ACTOR,
        "object": {"type": "Follow", "actor": "https://b.example/u", "object": ACTOR},
    }
    assert "E019" in check(write_doc, accept)
    accept["object"]["id"] = "https://b.example/follow/1"
    assert "E019" not in check(write_doc, accept)


def test_page_needs_name(write_doc):
    page = {"@context": va.AS_CONTEXT, "id": "https://l.example/post/1", "type": "Page"}
    assert "E021" in check(write_doc, page)


def test_unaddressed_mention_warns(write_doc, create_note):
    create_note["object"]["tag"] = [{"type": "Mention", "href": "https://b.example/users/bob"}]
    assert "W022" in check(write_doc, create_note)
    create_note["cc"].append("https://b.example/users/bob")
    assert "W022" not in check(write_doc, create_note)


def test_empty_array_warns(write_doc, create_note):
    create_note["object"]["tag"] = []
    assert "W023" in check(write_doc, create_note)


def test_actor_requirements(write_doc, person):
    broken = copy.deepcopy(person)
    del broken["inbox"], broken["preferredUsername"], broken["publicKey"], broken["followers"]
    assert {"E030", "E031", "E032", "W035"} <= check(write_doc, broken)


def test_public_key_owner_and_id(write_doc, person):
    person["publicKey"]["owner"] = "https://a.example/users/bob"
    person["publicKey"]["id"] = "https://keys.a.example/1"
    assert {"E033", "W034"} <= check(write_doc, person)


def test_inbox_on_other_origin(write_doc, person):
    person["inbox"] = "https://evil.example/inbox"
    assert "E037" in check(write_doc, person)


def test_bad_dates(write_doc, create_note):
    create_note["object"]["published"] = "20 Oct 2026"
    assert "E040" in check(write_doc, create_note)


def test_announced_activity_is_checked(write_doc, create_note):
    inner = copy.deepcopy(create_note)
    inner["object"]["type"] = "Page"
    announce = {
        "@context": va.AS_CONTEXT,
        "id": "https://l.example/announce/1",
        "type": "Announce",
        "actor": "https://l.example/c/x",
        "to": [PUBLIC],
        "object": inner,
    }
    assert "E021" in check(write_doc, announce)


def test_directory_is_scanned_recursively(tmp_path, create_note):
    import json

    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "x.json").write_text(json.dumps(create_note))
    (nested / "y.json").write_text("{bad")
    assert codes(va.validate([tmp_path])) == {"E001"}


def test_strict_and_exit_status(write_doc, create_note):
    create_note["to"] = ["Public"]
    path = write_doc(create_note)
    assert va.main([str(path)]) == 0
    assert va.main([str(path), "--strict"]) == 1
    create_note["actor"] = None
    del create_note["actor"]
    assert va.main([str(write_doc(create_note, "broken.json"))]) == 1


def test_helpers():
    assert va.as_list(None) == [] and va.as_list("a") == ["a"] and va.as_list([1]) == [1]
    assert va.id_of({"href": "https://x.example"}) == "https://x.example"
    assert va.origin("HTTPS://A.Example/x") == va.origin("https://a.example:443/y")
    assert va.origin("mailto:x@y") is None

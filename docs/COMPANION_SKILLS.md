# Companion skills: running with the HumHub skill

The `humhub-engineering` skill is developed in its own repository and installed next to
this one. Both can be active in the same session.

## Division of responsibility

| Topic | Owner |
| --- | --- |
| Actors, inbox and outbox, activities, WebFinger, HTTP signatures, FEPs | This skill |
| Where federation code lives in a module, config.php events, migrations, queue jobs, permissions, tests | HumHub skill |
| Mapping HumHub content and containers to ActivityPub objects and actors | Both: this skill defines the object shape ([platform mapping](../references/platform-mapping.md)), the HumHub skill defines the integration points |

## Trigger rules

- This skill's description excludes HumHub and Yii2 module structure so the two do not
  both claim the same request.
- A mixed request ("add federation to my module") should load this skill for protocol
  decisions and the HumHub skill for module structure.

## Conflict rule

If the two skills disagree, the protocol specification and the installed HumHub core win
over both skills. Report the disagreement to the user.

## Project-specific knowledge

A module that implements federation keeps its own facts (its invariants, data flows,
known gaps) in the module repository, for example in `CLAUDE.md` or `AGENTS.md` and a
developer document. Neither skill holds module-specific state.

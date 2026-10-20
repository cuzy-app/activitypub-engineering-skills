# Coding standards tooling

HumHub publishes a central `module-coding-standards` repository with shared
configuration for php-cs-fixer, PHPStan and Rector, plus GitHub workflows.

## Install in a module

```bash
composer config platform.php 8.2
composer config repositories.humhub-module-coding-standards vcs \
  https://github.com/humhub/module-coding-standards.git
composer require --dev humhub/module-coding-standards:dev-main
composer config scripts.rector \
  "vendor/bin/rector process --config=vendor/humhub/module-coding-standards/rector.php"
composer config scripts.fixer \
  "vendor/bin/php-cs-fixer fix --config=vendor/humhub/module-coding-standards/php-cs-fixer.php"
```

Commit `composer.lock`. Then run `composer fixer` and `composer rector` before each
commit, and PHPStan with the shared `phpstan.neon` where the module opts in.

## Workflows to copy

| Workflow | Purpose |
| --- | --- |
| php-cs-fixer | Formatting on commits to the main branches |
| rector-auto-pr | Weekly Rector run that opens a pull request |
| codeception-master / develop / next | Tests against those core branches |
| codeception-min-version | Tests against the minimum version in `module.json` |
| marketplace-upload | Uploads a release to the HumHub marketplace |

Verify the PHP platform version and workflow names against the repository's current
README; they change over time.

## Agent rules

- Run the formatter before reporting a PHP change as done.
- Do not disable a rule or add a PHPStan baseline entry to hide a real defect.
- Keep tool configuration in the shared repository; override locally only with a
  written reason.

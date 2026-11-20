# Security policy

## Scope

This policy covers the directory website, its catalog data format, contributor
validation, GitHub Actions and the script used to synchronize the public
Google Sheet. **It does not certify or govern the security of third-party
applications linked from the directory.** Report issues in those applications
to their original maintainers.

The actively maintained version of this directory is the latest `main`.
Other versions have no security-support commitment.

## Report a vulnerability privately

Use **Security → Advisories → Report a vulnerability** on this repository
when private vulnerability reporting is enabled. If that option is unavailable,
contact the maintainer privately through GitHub; do not disclose exploit
details, tokens, service-account JSON, or personal data in public issues or PRs.

Include a concise impact statement, affected files and safe reproduction
instructions. Avoid sharing live secrets, personal data or unnecessary
sensitive output. No automated response deadline is promised.

## Disclosure

The maintainer will review the report, coordinate an appropriate fix and
disclose it when safe. Please allow time for verification before publishing
exploit details. For ordinary corrections to catalog descriptions, use the
public issue form, not security reporting.

## Secrets

Credentials are stored only in GitHub Actions secrets. Contributors must
never add secrets, private reports, local configuration, log files or
third-party application assets to the repository.

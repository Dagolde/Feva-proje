# Branch Protection Rules — feva-mobile

This document describes the branch protection configuration applied to the `feva-mobile` repository under the IGSL GitHub organisation.

---

## `main` Branch

The `main` branch represents the production-ready state of the codebase. The following protections are enforced:

| Rule | Setting |
|------|---------|
| Require pull request before merging | ✅ Enabled |
| Required approving reviews | **2** |
| Dismiss stale reviews on new commits | ✅ Enabled |
| Require review from Code Owners (`CODEOWNERS`) | ✅ Enabled |
| Require status checks to pass before merging | ✅ Enabled |
| Required status checks | `flutter-ci / analyze`, `flutter-ci / test` |
| Require branches to be up to date before merging | ✅ Enabled |
| Restrict who can push to matching branches | `@igsl/feva-dev` (maintainers only) |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled |

---

## `develop` Branch

The `develop` branch is the integration branch for all feature work. The following protections are enforced:

| Rule | Setting |
|------|---------|
| Require pull request before merging | ✅ Enabled |
| Required approving reviews | **1** |
| Dismiss stale reviews on new commits | ✅ Enabled |
| Require review from Code Owners (`CODEOWNERS`) | ✅ Enabled |
| Require status checks to pass before merging | ✅ Enabled |
| Required status checks | `flutter-ci / analyze`, `flutter-ci / test` |
| Require branches to be up to date before merging | ✅ Enabled |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled |

---

## Rationale

- **No direct pushes to `main` or `develop`**: All changes must go through a reviewed pull request to maintain code quality and traceability.
- **CI checks required**: `flutter analyze` and `flutter test --coverage` must pass on every PR, ensuring no regressions are merged.
- **CODEOWNERS review**: The `@igsl/feva-dev` team must approve all changes, satisfying Requirement 20.1 (source code maintained within IGSL's GitHub organisation).
- **No force pushes**: Preserves the immutable commit history required for audit and accountability.

---

## Applying These Rules

Branch protection rules are configured via the GitHub repository settings UI or the GitHub API. To apply programmatically:

```bash
gh api repos/igsl/feva-mobile/branches/main/protection \
  --method PUT \
  --input branch-protection-main.json
```

Refer to the [GitHub Branch Protection API documentation](https://docs.github.com/en/rest/branches/branch-protection) for the full JSON schema.

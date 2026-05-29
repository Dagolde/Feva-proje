## Description

<!-- Provide a concise summary of the changes in this PR. -->

## Related Issue / Task

<!-- Link to the relevant task or issue, e.g. Closes #123 or Implements task 2.1 -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Refactor / code quality improvement
- [ ] Documentation update
- [ ] CI/CD or tooling change
- [ ] Database migration

## Checklist

- [ ] My code follows the project's style guidelines (`ruff check` passes)
- [ ] Type annotations are complete and `mypy` passes
- [ ] I have added or updated tests for the changed functionality
- [ ] All existing tests pass (`pytest --cov=app tests/`)
- [ ] Any new Alembic migration has been reviewed and is reversible
- [ ] No third-party services receive data without explicit Admin authorisation
- [ ] Sensitive data (secrets, keys, PII) is not hardcoded or committed
- [ ] I have updated relevant documentation (README, inline docstrings)

## Testing

<!-- Describe how you tested this change. Include relevant test commands or output. -->

```bash
ruff check .
mypy app/
pytest --cov=app tests/
```

## Database Migrations

<!-- If this PR includes Alembic migrations, describe the schema changes. -->

- [ ] No migrations in this PR
- [ ] Migration included — describe changes below:

## Screenshots / API Examples (if applicable)

<!-- Attach screenshots, curl examples, or OpenAPI snippets for API changes. -->

## Additional Notes

<!-- Any other context reviewers should know about. -->

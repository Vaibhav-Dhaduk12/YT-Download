# Contributing

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Set up development environment (see [DEVELOPMENT.md](DEVELOPMENT.md))
4. Make your changes
5. Run tests: `./scripts/test.sh`
6. Run linters: `./scripts/lint.sh`
7. Commit: `git commit -m "feat: add my feature"`
8. Push and open a Pull Request

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

## Adding a New Platform

1. Create `backend/app/core/<platform>.py` implementing `PlatformAdapter`
2. Register in `backend/app/core/factory.py`
3. Add URL patterns to `backend/app/services/validation_service.py`
4. Add tests in `backend/app/tests/`

## Code Style

- Python: Black + Ruff (line length 100)
- TypeScript: Angular style guide
- Run `pre-commit install` to enforce automatically

## Pull Request Checklist

- [ ] Tests pass (`./scripts/test.sh`)
- [ ] Linters pass (`./scripts/lint.sh`)
- [ ] Documentation updated if needed
- [ ] No secrets in code

# Justfile for mcp-feedback-enhanced-gw development
# 適用於 mcp-feedback-enhanced-gw 專案開發
# Cross-platform compatible with Windows, macOS, and Linux

# Cross-platform shell configuration
set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-cu"]

# Default recipe - show help
default:
    @just --list

# Show detailed help message
help:
    @echo "Available commands:"
    @echo ""
    @echo "Development Setup:"
    @echo "  dev-setup            Complete development setup"
    @echo "  install              Install the package"
    @echo "  install-dev          Install development dependencies"
    @echo "  install-hooks        Install pre-commit hooks"
    @echo ""
    @echo "Code Quality:"
    @echo "  lint                 Run linting with Ruff"
    @echo "  lint-fix             Run linting with auto-fix"
    @echo "  format               Format code with Ruff"
    @echo "  format-check         Check code formatting"
    @echo "  type-check           Run type checking with mypy"
    @echo "  check                Run all code quality checks"
    @echo "  check-fix            Run all checks with auto-fix"
    @echo "  quick-check          Quick check with auto-fix"
    @echo ""
    @echo "Pre-commit:"
    @echo "  pre-commit-run       Run pre-commit on staged files"
    @echo "  pre-commit-all       Run pre-commit on all files"
    @echo "  pre-commit-update    Update pre-commit hooks"
    @echo ""
    @echo "Testing:"
    @echo "  test                 Run tests"
    @echo "  test-cov             Run tests with coverage"
    @echo "  test-fast            Run tests without slow tests"
    @echo "  test-func            Run functional tests (standard)"
    @echo "  test-web             Run Web UI tests (continuous)"
    @echo "  test-desktop-func    Run desktop application functional tests"
    @echo "  test-all             Run all tests including desktop and functional tests"
    @echo ""
    @echo "Build & Release:"
    @echo "  build                Build the package"
    @echo "  build-check          Check the built package"
    @echo "  build-all            Build complete package with desktop app"
    @echo "  bump-patch           Bump patch version"
    @echo "  bump-minor           Bump minor version"
    @echo "  bump-major           Bump major version"
    @echo ""
    @echo "Desktop Application:"
    @echo "  check-rust           Check Rust development environment"
    @echo "  build-desktop        Build desktop application (debug)"
    @echo "  build-desktop-release Build desktop application (release)"
    @echo "  test-desktop         Test desktop application"
    @echo "  clean-desktop        Clean desktop build artifacts"
    @echo ""
    @echo "Maintenance:"
    @echo "  clean                Clean up cache and temporary files"
    @echo "  update-deps          Update dependencies"
    @echo "  ci                   Simulate CI pipeline locally"

# Install the package
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --dev

# Install pre-commit hooks
install-hooks:
    uv run pre-commit install
    @echo "✅ Pre-commit hooks installed successfully!"

# Run linting with Ruff
lint:
    uv run ruff check .

# Run linting with auto-fix
lint-fix:
    uv run ruff check . --fix

# Format code with Ruff
format:
    uv run ruff format .

# Check code formatting
format-check:
    uv run ruff format . --check

# Run type checking with mypy
type-check:
    uv run mypy

# Run all code quality checks
check: lint format-check type-check

# Run all checks with auto-fix
check-fix: lint-fix format type-check

# Quick check with auto-fix (recommended for development)
quick-check: lint-fix format type-check

# Run pre-commit on staged files
pre-commit-run:
    uv run pre-commit run

# Run pre-commit on all files
pre-commit-all:
    uv run pre-commit run --all-files

# Update pre-commit hooks
pre-commit-update:
    uv run pre-commit autoupdate

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=src/mcp_feedback_enhanced --cov-report=html --cov-report=term

# Run tests without slow tests
test-fast:
    uv run pytest -m "not slow"

# Run functional tests (standard)
test-func:
    uv run python -m mcp_feedback_enhanced test

# Run Web UI tests (continuous)
test-web:
    uvx --no-cache --with-editable . mcp-feedback-enhanced-gw test --web

# Run desktop application functional tests
test-desktop-func:
    uvx --no-cache --with-editable . mcp-feedback-enhanced-gw test --desktop

# Run all tests including desktop and functional tests
test-all: test test-func test-desktop
    @echo "✅ All tests completed!"

# Clean up cache and temporary files
clean:
    @echo "Cleaning up..."
    {{if os_family() == "windows" { "if (Test-Path .mypy_cache) { Remove-Item -Recurse -Force .mypy_cache }; if (Test-Path .ruff_cache) { Remove-Item -Recurse -Force .ruff_cache }; if (Test-Path .pytest_cache) { Remove-Item -Recurse -Force .pytest_cache }; if (Test-Path htmlcov) { Remove-Item -Recurse -Force htmlcov }; if (Test-Path dist) { Remove-Item -Recurse -Force dist }; if (Test-Path build) { Remove-Item -Recurse -Force build }; Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force; Get-ChildItem -Recurse -File -Filter *.pyc | Remove-Item -Force; Get-ChildItem -Recurse -File -Filter *.pyo | Remove-Item -Force" } else { "rm -rf .mypy_cache .ruff_cache .pytest_cache htmlcov dist build; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true; find . -name '*.pyc' -delete 2>/dev/null || true; find . -name '*.pyo' -delete 2>/dev/null || true; find . -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true" } }}
    @echo "✅ Cleanup completed!"

# Update dependencies
update-deps:
    uv sync --upgrade

# Build the package
build:
    uv build

# Check the built package
build-check:
    uv run twine check dist/*

# Bump patch version
bump-patch:
    uv run bump2version patch

# Bump minor version
bump-minor:
    uv run bump2version minor

# Bump major version
bump-major:
    uv run bump2version major

# Complete development setup
dev-setup: install-dev install-hooks
    @echo "🎉 Development environment setup complete!"
    @echo ""
    @echo "Next steps:"
    @echo "  1. Run 'just check' to verify everything works"
    @echo "  2. Start coding! Pre-commit hooks will run automatically"
    @echo "  3. Use 'just --list' to see all available commands"

# Simulate CI pipeline locally
ci: clean install-dev pre-commit-all test

# Check Rust development environment
check-rust:
    @echo "🔍 Checking Rust environment..."
    @rustc --version || (echo "❌ Rust not installed. Please visit https://rustup.rs/" && exit 1)
    @cargo --version || (echo "❌ Cargo not installed" && exit 1)
    @echo "✅ Rust environment check completed"

# Build desktop application (debug mode)
build-desktop:
    @echo "🔨 Building desktop application (debug)..."
    uv run python scripts/build_desktop.py

# Build desktop application (release mode)
build-desktop-release:
    @echo "🚀 Building desktop application (release)..."
    uv run python scripts/build_desktop.py --release

# Test desktop application
test-desktop: build-desktop
    @echo "🖥️ Testing desktop application..."
    uv run python -m mcp_feedback_enhanced test --desktop

# Clean desktop build artifacts
clean-desktop:
    @echo "🧹 Cleaning desktop build artifacts..."
    uv run python scripts/build_desktop.py --clean

# Build complete package with desktop app
build-all: clean build-desktop-release build
    @echo "🎉 Complete build finished!"

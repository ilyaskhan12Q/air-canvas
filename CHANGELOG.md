# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.0] — 2026-03-12

### Added
- Real-time hand tracking via MediaPipe Hands
- Index-finger air drawing with trail interpolation
- Five gesture commands: DRAW, PAUSE, ERASE, CLEAR, UNKNOWN
- Five visual effect modes: Neon Glow, Rainbow, Sparkle, Pastel, Classic
- CPU particle system with physics simulation
- Streamlit UI with live sidebar controls (colour, brush size, trail length)
- Background modes: Black, Dark Blue, Dark Green, Mirror Feed
- Hand skeleton overlay (toggleable)
- Live stats panel: FPS, stroke count, active effect
- Screenshot / canvas save functionality
- Full pytest test suite with ≥ 70% coverage target
- GitHub Actions CI (lint + test on 3 OS × 4 Python versions)
- Security scanning with Bandit
- `pyproject.toml` with Ruff, Black, mypy configuration
- MIT License
- CONTRIBUTING.md with guides for adding gestures and effects
- SECURITY.md with responsible-disclosure policy
- GitHub Issue templates (bug report, feature request)
- PR template with checklist

[Unreleased]: https://github.com/your-username/air-canvas/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/air-canvas/releases/tag/v1.0.0

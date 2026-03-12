# Contributing to Air Canvas 🎨

Thank you for taking the time to contribute! Whether you're fixing a bug, adding a gesture, or improving the docs — every contribution matters.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Adding a New Gesture](#adding-a-new-gesture)
- [Adding a New Effect](#adding-a-new-effect)

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).  
By participating you agree to uphold a respectful, welcoming environment.

---

## 🤝 How to Contribute

### Reporting Bugs
Use the **[Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)** template.  
Please include your OS, Python version, and a minimal reproduction.

### Suggesting Features
Use the **[Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)** template.  
We love ideas — gesture shortcuts, new effects, export formats, you name it.

### First-time Contributors
Look for issues labelled **`good first issue`** or **`help wanted`** — these are great starting points.

---

## 🛠️ Development Setup

```bash
# 1. Fork & clone
git clone https://github.com/ilyaskhan12Q/air-canvas.git
cd air-canvas

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install all dependencies (including dev tools)
pip install -r requirements-dev.txt

# 4. Verify setup
pytest                             # all tests should pass
streamlit run app.py               # app should launch
```

---

## 📁 Project Structure

```
air-canvas/
├── app.py                  # Streamlit UI entry point
├── src/
│   ├── hand_tracker.py     # MediaPipe wrapper
│   ├── canvas.py           # Drawing + compositing
│   ├── gesture.py          # Gesture classification
│   └── effects.py          # Particle system
├── tests/                  # pytest test suite
├── .github/                # CI workflows & issue templates
├── pyproject.toml          # Build config, tool settings
├── requirements.txt        # Runtime deps
└── requirements-dev.txt    # Dev/test deps
```

---

## 🎨 Coding Standards

We use:
- **[Black](https://black.readthedocs.io/)** for formatting (line length = 100)
- **[Ruff](https://docs.astral.sh/ruff/)** for linting
- **[mypy](https://mypy.readthedocs.io/)** for optional type checking

```bash
# Format
black src/ tests/ app.py

# Lint
ruff check src/ tests/ app.py

# Type check
mypy src/
```

All three must pass before a PR can be merged.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Single module
pytest tests/test_gesture.py -v
```

Please write tests for any new functionality. Target: **≥ 70% coverage** on `src/`.

---

## 💬 Commit Messages

Follow **[Conventional Commits](https://www.conventionalcommits.org/)**:

```
<type>(<scope>): <short summary>

Types: feat | fix | docs | style | refactor | test | chore | perf
```

**Examples:**
```
feat(gesture): add two-hand drawing support
fix(canvas): prevent trail bleed on window resize
docs(readme): add Raspberry Pi installation guide
test(effects): add particle boundary tests
```

---

## 🔀 Pull Request Process

1. **Branch** off `main`: `git checkout -b feat/my-feature`
2. **Make changes** — small, focused PRs are easier to review
3. **Add/update tests**
4. **Update `CHANGELOG.md`** under `[Unreleased]`
5. **Push** and open a PR against `main`
6. Fill in the **PR template** completely
7. At least **one approving review** is required before merge

---

## ✌️ Adding a New Gesture

1. Open `src/gesture.py`
2. Add your rule to `GestureRecognizer.recognize()`:
   ```python
   # Example: point all four fingers (no thumb) → COLOR_PICKER
   if not thumb and index and middle and ring and pinky:
       return "COLOR_PICKER"
   ```
3. Add a description to `gesture_description()`
4. Handle the new gesture code in `app.py`'s main loop
5. Document it in the **Gesture Guide** section of `README.md`
6. Add a test in `tests/test_gesture.py`

---

## ✨ Adding a New Effect

1. Open `src/canvas.py`
2. Add a new branch in `AirCanvas.draw_trail()`:
   ```python
   elif effect_mode == "My Effect":
       self._draw_my_effect(p1, p2, color, brush_size)
   ```
3. Implement `_draw_my_effect()` as a private method
4. Register the name in the `app.py` sidebar `selectbox`
5. Add a test in `tests/test_canvas.py` using `@pytest.mark.parametrize`

---

## 🙏 Thank You

Every contribution — however small — makes Air Canvas better.  
Don't hesitate to open a draft PR early if you want feedback on an approach!

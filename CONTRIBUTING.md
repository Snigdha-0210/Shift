# Contributing to SHIFT

Thank you for your interest in contributing to **SHIFT**! We welcome bug reports, feature suggestions, mechanics tuning, and pull requests from developers of all skill levels.

---

## 🛠️ How to Contribute

### 1. Reporting Bugs
- Search existing issues to check if your issue has already been reported.
- If not, open a new issue with:
  - Clear, descriptive title.
  - Steps to reproduce the bug.
  - Expected behavior vs. actual behavior.
  - Python and Pygame version details.

### 2. Suggesting Enhancements
- Open a feature request issue.
- Describe the feature in detail (e.g., power-up systems, particle effects, audio engine, procedural backgrounds).
- Explain why it adds value to the gameplay loop.

### 3. Submitting Pull Requests (PR)
1. **Fork the Repository** on GitHub.
2. **Clone your fork** locally:
   `ash
   git clone https://github.com/<your-username>/Shift.git
   cd Shift
   `
3. **Create a feature branch**:
   `ash
   git checkout -b feature/awesome-new-mechanic
   `
4. **Make your changes** following the code conventions below.
5. **Test thoroughly**:
   `ash
   python main.py
   `
6. **Commit with clean commit messages**:
   `ash
   git commit -m "feat: add particle trail effect on lane shift"
   `
7. **Push to your fork and submit a PR** against the main branch.

---

## 📐 Code Style & Conventions

- **Python standard**: PEP 8 compliance.
- **Delta-Time Driven**: All spatial translations, physics, and animations must be multiplied by dt to remain framerate-independent.
- **Fair Spawning**: Any new obstacle patterns must guarantee at least one reachable lane for the player.
- **Clear Documentation**: Keep docstrings and comments descriptive.

---

## 📄 License
By contributing to SHIFT, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

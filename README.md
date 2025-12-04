# 🐝 Equation Solver

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

A powerful, single-file web application for solving mathematical equations. Built with Flask and SymPy, designed to help students and knowledge workers solve equations quickly with support for implicit multiplication and multiple output formats.

**Live Demo**: https://zombimann.pythonanywhere.com/

## ✨ Features

- **Smart Parsing**: Handles implicit multiplication (`2x`, `sin(x)`, `5(x+1)`) automatically.
- **Dual Output Modes**: Toggle instantly between **Exact** (symbolic/surd) and **Approximate** (decimal) answers.
- **Natural Math Notation**: Write equations as you would on paper (e.g., `x² + 9x = 8`, `√x`, `sin(x)=0.5`).
- **Export Ready**: Copy solutions in one click as **LaTeX**, **Markdown**, **HTML**, or **Plain Text**.
- **Custom Variables**: Solve for `x`, `y`, `t`, `a`, or any single-letter variable.
- **Zero-Config Deployment**: contained entirely within a single `flask_app.py` file—no complex folder structures.
- **Secure**: Robust input sanitization, length limits, and restricted evaluation scope.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone [https://github.com/zombimann/equation-solver.git](https://github.com/zombimann/equation-solver.git)
cd equation-solver
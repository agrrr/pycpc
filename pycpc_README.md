# 🔐 pycpc — Python Implementation of Robust Codes & CpC Coding Scheme

**pycpc** is a Python 3 implementation of **robust error-correcting codes** and the **CpC (Code-per-Code) coding scheme**. This repository is a fork of [Euphoriaa/pycpc](https://github.com/Euphoriaa/pycpc), extended with additional experimentation via Jupyter notebooks.

> Licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

---

## 📖 Background

The **CpC coding scheme** is a robust coding technique designed to maintain integrity even under noisy or adversarial channel conditions. This project implements the scheme in pure Python, making it accessible for research, simulation, and educational use without requiring specialized hardware or proprietary tools.

---

## ✨ Features

- Pure Python 3 implementation — no specialized dependencies
- Modular `src/` package structure
- Jupyter notebook for interactive experimentation (`Untitled0.ipynb`)
- GPL-3.0 licensed — open for use and modification

---

## 📂 Project Structure

```
pycpc/
├── src/                # Core library: robust codes & CpC implementation
├── Untitled0.ipynb     # Jupyter notebook for experiments and demos
├── README.md           # This file
├── LICENSE             # GPL-3.0 license
├── .gitignore
└── debug.log
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

```bash
git clone https://github.com/agrrr/pycpc.git
cd pycpc
pip install -r requirements.txt   # if available
```

### Running the Code

```bash
cd src
python3 main.py
```

### Interactive Exploration

Launch Jupyter to explore the notebook:

```bash
jupyter notebook Untitled0.ipynb
```

---

## 📚 Concepts Covered

- **Robust codes** — error detection and correction under adversarial conditions
- **CpC (Code-per-Code) scheme** — encoding strategy for enhanced integrity
- Channel coding theory fundamentals
- Python-based simulation of coding schemes

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0**. See the [`LICENSE`](./LICENSE) file for details.

---

## 🙏 Acknowledgements

Forked from [Euphoriaa/pycpc](https://github.com/Euphoriaa/pycpc). Original implementation and concept by the upstream authors.

---

## 👤 Author (this fork)

**agrrr** — [github.com/agrrr](https://github.com/agrrr)

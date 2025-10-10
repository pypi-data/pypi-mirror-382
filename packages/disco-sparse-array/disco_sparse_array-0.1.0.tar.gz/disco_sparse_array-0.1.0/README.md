# 🧮 sparse-array

**Sparse vector and matrix classes with fast C++/NumPy-backed operations**  
for use in **Disco** simulation programs and other large-scale discrete event models.

[![PyPI](https://img.shields.io/pypi/v/sparse-array.svg)](https://pypi.org/project/sparse-array/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build](https://github.com/<your-org-or-user>/sparse-array/actions/workflows/build.yml/badge.svg)](https://github.com/<your-org-or-user>/sparse-array/actions)
[![Tests](https://github.com/<your-org-or-user>/sparse-array/actions/workflows/test.yml/badge.svg)](https://github.com/<your-org-or-user>/sparse-array/actions)

---

## Overview

`disco-sparse-array` provides compact **sparse vector** and **sparse matrix** types that operate efficiently on large, structured numerical data.  
The package is optimized for repeated arithmetic and transformation operations that occur during **Monte Carlo and discrete-event simulations**, as used in the **Disco** simulation framework.

It combines:
- Lightweight **Python classes** for usability.
- **C++/pybind11 kernels** for compute-intensive operations.
- **NumPy interoperability** for zero-copy exchange of data.

---

## ✨ Features

- Sparse **Vector** and **Matrix** classes with explicit indices and values.
- Fast arithmetic:
  - `a + b`, `a @ m`, and in-place variants.
- Change detection and subset validation (`diff`, `changes`).
- Conversion utilities:
  - Sparse → dense arrays (`to_dense`).
  - Dense → sparse (via index filtering).
- Consistent API and predictable semantics across all operations.
- MIT-licensed, pure Python/C++ — no external runtime dependencies beyond NumPy.

---

## 🚀 Installation

```bash
pip install disco-sparse-array

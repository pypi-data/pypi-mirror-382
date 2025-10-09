# 🌈 **spectralcubekit**

> ⚙️ *A modern toolkit for working with any and all flavors of spectral data cubes.*

---

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spectralcubekit)](https://pypi.org/project/spectralcubekit/)
[![PyPI - License](https://img.shields.io/pypi/l/spectralcubekit)](https://opensource.org/licenses/MIT)
[![PyPI - Version](https://img.shields.io/pypi/v/spectralcubekit)](https://pypi.org/project/spectralcubekit/)

---

## 🧠 What is `spectralcubekit`?

`spectralcubekit` is a lightweight, modular Python package designed to make analysis of **spectral data cubes** simple, flexible, and fun. Whether you're exploring planetary hyperspectral data, performing band analysis, or building your own spectral pipelines — this toolkit’s got you covered.

---

## 🧰 **Currently Available Modules**

| Module | Description |
|--------|--------------|
| 🧪 `band_parameters` | Provides parameters that describe **spectral band shapes** and sizes. |
| 📈 `linear_fitting`  | Fits lines to entire spectral cubes along the **spectral domain** (z-axis). |
| 🧩 `misc_utils`      | Miscellaneous utility functions for **spectral cube operations**. |

*And more modules coming soon! As a work through my Ph.D., I will add all the utility functions I write for hyperspectral data processing here!*

---

## 🚀 **Quick Start**

```bash
pip install spectralcubekit
```

```python
import spectralcubekit as sck

fit_result = sck.fit_linear_cube(cube)
sck.save_fit(fit_result, "path/to/save.fits")
```

## 🔗 Links

- **GitHub**: [https://github.com/z-vig/spectralcubekit.git](https://github.com/z-vig/spectralcubekit.git)
- **Docs**: (coming soon!)

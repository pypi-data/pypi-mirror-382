# artpack

Python port of the R package [artpack](https://CRAN.R-project.org/package=artpack), bringing generative art color palettes to the Python ecosystem.

## About

artpack provides curated color palettes designed for generative art and data visualization. This is a work-in-progress port of the original R package.

## Installation

```bash
pip install artpack-py
```

## Quick Start

```python
from artpack import art_pals

# Get 5 colors from the ocean palette
colors = art_pals("ocean", n=5)
print(colors)
# ['#12012E', '#144267', '#15698C', '#0695AA', '#156275']

# Reverse the palette
colors_rev = art_pals("ocean", n=5, direction = "reverse")

# Randomize color order
colors_random = art_pals("rainbow", n = 10, randomize = True)
```

## Available Palettes

`"arctic"`, `"beach"`, `"bw"`, `"brood"`, `"cosmos"`, `"explorer"`, `"gemstones"`, `"grays"`, `"icecream"`, `"imagination"`, `"majestic"`, `"nature"`, `"neon"`, `"ocean"`, `"plants"`, `"rainbow"`, `"sunnyside"`, `"super"`

## Development Status

🚧 **Work in Progress** - Currently porting core functionality from the R version. More features coming soon!

**Currently implemented:**
- ✅ Color palette generation (`art_pals()`)
- ✅ 100% test coverage
- ✅ CI/CD with GitHub Actions

**Roadmap:**
- Additional color palette tools (Functions that help with color-related tasks.)
- Asset creation (Functions that help with making data for generative art.)
- Geometric testing tools (Functions that help with geometric/spatial analysis for generative art.)
- Grouping tools (Functions that help with grouping generative art data.)
- Sequencing tools (Functions that help with numeric sequencing.)
- Transformation tools (Functions that help with transforming existing generative art data.)

## Links

- **Python Package (PyPI):** [artpack-py](https://pypi.org/project/artpack-py/)
- **Original R Package (CRAN):** [artpack](https://CRAN.R-project.org/package=artpack)
- **GitHub Repository:** [github.com/Meghansaha/artpack-py](https://github.com/Meghansaha/artpack-py)

## License

MIT License

Copyright (c) 2025 Meghan Harris

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author

Meghan Harris ([@meghansaha](https://github.com/Meghansaha))
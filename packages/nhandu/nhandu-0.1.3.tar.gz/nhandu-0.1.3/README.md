
# Nhandu 

> *Nhandu* (/ɲãndu/, approximately "NYAN-doo") means "spider" in many Tupi-Guarani languages, a fitting name for a tool that weaves together code and documentation, much like Knuth's original vision of literate programming.

**Literate programming for Python: Write executable documents in plain `.py` files.**

Nhandu transforms ordinary Python files with markdown comments into beautiful, reproducible reports. It's lighter than Jupyter, simpler than Quarto, and perfectly git-friendly.

## Why Nhandu?

Contemporary literate programming in Python faces a documentation dilemma:

- **Jupyter notebooks** are powerful but use JSON format (git diffs are messy), require a browser/server, and mix code with metadata
- **Quarto** is feature-rich but complex, with many configuration options and a learning curve
- **Pweave** has not been maintained for many years and is incompatible with currently supported Python versions.
- **Traditional scripts** lack integrated documentation and visualization

Nhandu offers a different solution:

- Write literate programs in **normal `.py` files**: no special format, just comments
- **Perfect git diffs**: plain text, not JSON, no timestamps, no hashes
- **No server or browser** required—just run the command
- **Zero configuration needed**: smart defaults get you started immediately
- **Python-native**: designed specifically for the Python ecosystem

Nhandu also supports traditional `.md` files with code blocks if you prefer that style.

## Quick Start

### Your First Literate Program

Create a file `analysis.py`:

```python
#' # My First Analysis
#'
#' This is a literate Python program. Lines starting with `#'` are markdown.
#' Everything else is regular Python code.

import numpy as np

# Generate some data
data = np.random.normal(0, 1, 1000)

#' ## Results
#'
#' Let's compute some statistics:

print(f"Mean: {data.mean():.3f}")
print(f"Std Dev: {data.std():.3f}")

#' The data looks normally distributed, as expected.
```

### Generate Your Report

```bash
nhandu analysis.py
```

This creates `analysis.html` with your code, output, and nicely formatted documentation, from a plain Python script.

## Features

### Smart Output Capture

Nhandu automatically captures:

- **Print statements** and stdout
- **Matplotlib plots** (no `plt.show()` needed!)
- **Expression results** (like Jupyter cells)
- **Rich objects** (DataFrames render as tables in HTML)

### Syntax Highlighting

Server-side syntax highlighting with 50+ themes via Pygments. Popular themes include: `github-dark` (default), `monokai`, `dracula`, `one-dark`, `vs`, and `solarized-light`.

### Multiple Output Formats

Markdown output can be converted to PDF, Word, LaTeX, and more using [pandoc](https://pandoc.org/) or similar tools. Native HTML support is implemented out-of-the-box.

### Configuration (Optional)

Power users can customize their reports via YAML frontmatter:

```python
#' ---
#' title: My Scientific Report
#' output: html
#' code_theme: dracula
#' plot_dpi: 150
#' ---
#'
#' # Introduction
#' ...
```

It is also possible to use a configuration file (`nhandu.yaml`) or CLI arguments.

## How It Works

### Literate Python Format (`.py` files)

Nhandu treats Python files specially when they contain markdown comments:

```python
#' # This is a markdown heading
#'
#' Any line starting with #' is treated as **markdown**.
#' You can use all standard markdown features.

# This is a regular Python comment
x = 42  # Regular code continues to work normally

#' Back to documentation. Variables persist across blocks:

print(f"x = {x}")
```

**Hidden code blocks** let you run setup code without cluttering your report:

```python
#| hide
import pandas as pd
import matplotlib.pyplot as plt
# Configuration code here—runs but doesn't appear in output
#|

#' Now let's analyze our data:
# This code WILL appear in the output
data = pd.read_csv("data.csv")
```

### Traditional Markdown Format (`.md` files)

You can also use standard markdown files with code blocks:

````markdown
# My Analysis

Here's some Python code:

```python
import numpy as np
x = np.linspace(0, 10, 100)
print(f"Generated {len(x)} points")
```

The output will appear in your rendered document. In case of HTML output, any figures are embedded in the file, so that you have a single file to distribute.

````

### Execution Model

- **Shared namespace**: All code blocks share the same Python environment
- **Sequential execution**: Blocks run in document order
- **Output capture**: stdout, plots, and expression results are all captured
- **Rich formatting**: Automatic handling of matplotlib figures, pandas DataFrames, and more

### Inline Code Evaluation

You can embed Python expressions directly within markdown text using inline code syntax:

- **`<%= expression %>`** - Evaluates the expression and displays the result
- **`<% statement %>`** - Executes code without displaying output

This works in both `.py` literate files and traditional `.md` files:

```python
#' # Sales Report
#'
#' <% import datetime %>
#' Report generated on <%= datetime.date.today() %>.

total_sales = 45000
target = 50000

#' We achieved <%= total_sales %> in sales.
#' That's <%= (total_sales/target)*100 %>% of our target.
#'
#' <% status = "on track" if total_sales >= target * 0.9 else "behind" %>
#' Status: We are <%= status %>.
```

Inline code shares the same namespace as regular code blocks, so you can reference variables, import modules, and perform calculations seamlessly within your documentation.

## Examples

Check out the [`examples/`](https://github.com/tresoldi/nhandu/tree/main/examples/) directory for complete demonstrations:

- **[01_hello_world.py](https://github.com/tresoldi/nhandu/tree/main/examples/01_hello_world.py)** - Basic syntax and concepts [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/01_hello_world.py.html)]
- **[02_data_analysis.py](https://github.com/tresoldi/nhandu/tree/main/examples/02_data_analysis.py)** - Working with data using standard library [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/02_data_analysis.py.html)]
- **[03_plotting.py](https://github.com/tresoldi/nhandu/tree/main/examples/03_plotting.py)** - Creating visualizations with matplotlib [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/03_plotting.py.html)]
- **[04_scientific_computation.py](https://github.com/tresoldi/nhandu/tree/main/examples/04_scientific_computation.py)** - Numerical computing with NumPy [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/04_scientific_computation.py.html)]
- **[05_advanced_report.py](https://github.com/tresoldi/nhandu/tree/main/examples/05_advanced_report.py)** - Complex report with pandas and multiple visualizations [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/05_advanced_report.py.html)]
- **[06_inline_code.py](https://github.com/tresoldi/nhandu/tree/main/examples/06_inline_code.py)** - Inline code evaluation with `<%= %>` syntax [[OUTPUT](https://htmlpreview.github.io/?https://github.com/tresoldi/nhandu/blob/main/examples/06_inline_code.py.html)]

## Installation & Usage

### Install from PyPI

```bash
pip install nhandu
```

### Install from Source

```bash
git clone https://github.com/tresoldi/nhandu.git
cd nhandu
pip install -e .
```

### Basic Usage

```bash
nhandu document.py                       # Process literate Python file → document.html
nhandu document.md                       # Process markdown file → document.html
nhandu document.py -o report.html        # Specify output file
nhandu document.py --format md           # Output as markdown
nhandu document.py --code-theme monokai  # Custom syntax theme
nhandu document.py --verbose             # Show processing details
```

### CLI Options

```
nhandu [OPTIONS] INPUT

Options:
  -o, --output PATH           Output file path
  --format {html,md}          Output format (default: html)
  --config PATH               Configuration file (YAML)
  --working-dir PATH          Working directory for code execution
  --timeout SECONDS           Execution timeout
  --code-theme THEME          Syntax highlighting theme
  --verbose, -v               Enable verbose output
  --version                   Show version
  --help                      Show help message
```

### Roadmap

Current priorities:

- [ ] Native PDF output support
- [ ] Custom HTML templates (Jinja2)
- [ ] Watch mode for live development
- [ ] Rich display for more object types (NumPy arrays, scikit-learn models)
- [ ] Caching system for faster re-renders

See [issues](https://github.com/tresoldi/nhandu/issues) for more details and to suggest features.

## Project Information

### Citation and Acknowledgements

If you use Nhandu in your research, please cite:

```bibtex
@software{tresoldi2025nhandu,
  author = {Tresoldi, Tiago},
  title = {Nhandu: Literate Programming for Python},
  year = {2025},
  publisher = {Department of Linguistics and Philology, Uppsala University},
  address = {Uppsala, Sweden},
  url = {https://github.com/tresoldi/nhandu},
  orcid = {0000-0002-2863-1467}
}
```

The earliest stages of development took place within the context of
the [Cultural Evolution of Texts](https://github.com/evotext/) project, with funding from the
[Riksbankens Jubileumsfond](https://www.rj.se/) (grant agreement ID:
[MXM19-1087:1](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

### License

MIT License - see [LICENSE](LICENSE) file for details.

### Acknowledgments

Nhandu is inspired by:
- Donald Knuth's original [literate programming](https://en.wikipedia.org/wiki/Literate_programming) vision
- [knitr](https://yihui.org/knitr/) and R Markdown's approach to reproducible research
- [Jupyter](https://jupyter.org/)'s interactive computing paradigm
- [Quarto](https://quarto.org/)'s modern scientific publishing tools
- [Pweave](http://mpastell.com/pweave/)'s Python implementation (though no longer maintained)

Special thanks to the scientific Python community for building the ecosystem that makes tools like this possible.

# Setup

## Instruction

**Requirements**

    Python > 3.8

**Installation**

Install the theme

```sh
python -m pip install sphinx
python -m pip install sphinx-theme-mochi
```

Create a new project

```sh
sphinx-quickstart .
```

Edit conf.py to change the theme
```py
# conf.py
html_theme = 'sphinx_theme_mochi'
```

Add this theme to the list of extensions.

```py
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'myst_parser',
    'sphinx_theme_mochi', ###
]
```

## Recommended Tools

### build automation

sphinx-autobuild watches local files and rebuilds the document when changed.

```sh
python -m pip install sphinx-autobuild
```

Run, then open the browser to preview (defaults to localhost:8000)

```sh
sphinx-autobuild -E <source> <build/html>
# -E: fresh build (no-cache). 
```

The `-E` option forces sphinx to rebuild all pages per change. This slows down the build, but keeps the sidebar contents consistent across the pages.




### markdown

Add a markdown parser extension for markdown syntax support. 
[MyST-parser](https://www.sphinx-doc.org/en/master/usage/markdown.html) is a parser designed for Sphinx (and Docutils). 


```sh
python -m pip install myst_parser
```

```py
extensions = [
    'myst_parser',
]
```

### mathjax

Sphinx has math equation support for both html/non-html. For html output, sphinx can use image-renderer or mathjax-renderer for math rendering.

To use mathjax renderer, add the mathjax extension to the extensions list, and set `mathjax_path` to the script. See [Official docs](https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax) for details.

```py
#conf.py
mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
```

Download the javascript for local distribution. For offline environment, you might need to use `file://` URL.

```py
pip install sphinx-mathjax-offline
```

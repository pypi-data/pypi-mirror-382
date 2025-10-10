
# Usage

Sphinx-theme-mochi is a static theme with a python script bundled. 

## Foldable navtree

The content of sidebar navigation is generated from the sphinx's toctree. Use `toctree::` directive to structure your files.

```rst
..  toctree::
    :maxdepth: 1
    :titlesonly:

    page1.md
    page2.md
    page3.md
```

A document usually contain one or more subsections. Sphinx internally builds a toctree (a tree-structured information), and if the document has a toctree directive, sphinx will scan those documents as well. Nested toctree will be merged to the parent. The final toctree will show up in the left sidebar navigation. 

Typical options for the navtrees are: `numbered`, `titlesonly` and `caption`. For more details, check this page: [](./usage_nav.md)











```{toctree}
:hidden:

usage_nav.md
usage_myst.md
```

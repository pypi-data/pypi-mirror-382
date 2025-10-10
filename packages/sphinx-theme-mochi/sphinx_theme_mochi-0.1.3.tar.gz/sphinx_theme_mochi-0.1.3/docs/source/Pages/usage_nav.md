
# Usage - NavTree

```rst
..  toctree::
    :caption: Index
    :maxdepth: 1
    :titlesonly:
    :numbered:

    page1.md
    page2.md
    page3.md
```

## Directives

`.. toctree::` directive inserts a table-of-contents (toc) at that location. Sphinx organizes and structures the page hierarchy by building a "toctree". The theme's sidebar navtree is generated from this toctree, so it is strong advised to understand this directive.

Sphinx manages all pages in a hierarchical structure. Each page has multiple level of headings, and the toctree directive organizes multiple documents by placing another document beneath the current level. By repeating this process, sphinx will manage all pages in a single "toctree". 

A toctree directive can be used multiple times. It can be also nested. Sphinx merges all those information to a single global toctree. 

Directive options will change the behavior and its output, but not the sidebar navtree generation. This may be unclear and confusing at first.

**caption (Text)**

Set a title of the toctree. The title is printed above the toc, for both page and the sidebar. The title of the nested toctree will be ignored in the sidebar. 

**numbered**

Add chapter numbers to each section name. 

**titlesonly**

For each subdocuments, only the top level header is included in the toctree.

Set this flag if you prefer simpler navtree. All subsections will be ignored. Do not set this flag if you want a complete list of headers in the toctree.

The nested toctrees inside the subsections are still discovered and merged to the parent. This may result to an inconsistent state.

**maxdepth (N)**

Limits the toctree depth inserted at that location. 

This value has no effect on the sidebar navtree. Check theme variable `mochi_navtree_maxdepth` for that purpose.

**hidden**

Hide the TOC at that location (no rendering). 

This option has no effect on the sidebar navtree. 

**etc**

See [official documentation](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree) for more. 


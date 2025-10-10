""" a simple, plain, solid sphinx theme """
__version__ = "0.1.3"

from os import path
from bs4 import BeautifulSoup as bs, Tag
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import TocTree
from functools import lru_cache
from typing import Dict, Any

Ctx = Dict[str, Any]

lru_cache(maxsize=None)

def _inspect(item):
    """ set breakpoint here and inspect any item passed from jinja"""
    _ = item
    pass

def _get_theme_var_bool(context: Ctx, key: str, fallback: bool = False) -> bool:
    try:
        value: str = context[key]

        if type(value) != str:
            return fallback
        
        value = value.strip().lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value == '1':
            return True
        elif value == '0':
            return False
        else:
            return fallback
    except:
        return fallback


def _get_theme_var_int(context: Ctx, key: str, fallback: int = 0) -> int:
    try:
        value: str = context[key]

        if type(value) != str:
            return fallback
        
        return int(value)
    except:
        return fallback



def _get_navigation_expand_image(soup: bs) -> Tag:
    retval = soup.new_tag("i", attrs={"class": "icon"})

    svg_element = soup.new_tag("svg")
    svg_use_element = soup.new_tag("use", href="#svg-arrow-right")
    svg_element.append(svg_use_element)

    retval.append(svg_element)
    return retval

def _create_sidebar_toc(toctree_html: str) -> str:
    """
    add custom styles to toctree_html so it can be stylized. 
    this function also appends label tag to provide open/collapse button
    """
    if not toctree_html:
        return toctree_html

    soup = bs(toctree_html, "html.parser")

    toctree_checkbox_count = 0
    last_element_with_current = None
    for element in soup.find_all("li", recursive=True):
        #
        classes = element.get("class", [])
        if "current" in classes:
            last_element_with_current = element

        # Nothing more to do, unless this has "children"
        if not element.find("ul"):
            continue

        # Add a class to indicate that this has children.
        element["class"] = classes + ["has-children"]

        # add a checkbox.
        toctree_checkbox_count += 1
        checkbox_name = f"toctree-checkbox-{toctree_checkbox_count}"

        # Add the "label" for the checkbox which will get filled.
        label = soup.new_tag(
            "label",
            attrs={
                "for": checkbox_name,
            },
        )
        label.append(_get_navigation_expand_image(soup))

        element.insert(1, label)

        # Add a checkbox used to store expanded/collapsed state.
        checkbox = soup.new_tag(
            "input",
            attrs={
                "type": "checkbox",
                "class": ["toctree-checkbox"],
                "id": checkbox_name,
                "name": checkbox_name,
                "role": "switch",
            },
        )
        # if this has a "current" class, be expanded by default (by checking the checkbox)
        if "current" in classes:
            checkbox.attrs["checked"] = ""

        element.insert(1, checkbox)

    if last_element_with_current is not None:
        last_element_with_current["class"].append("current-page")

    return str(soup)

def _get_full_toctree(context: Ctx) -> str:
    """Use sphinx-provided API to get a full-depth navtree in html string"""

    if "toctree" in context:
        fn_toctree = context["toctree"]

        titles_only = _get_theme_var_bool(context, 'theme_mochi_navtree_titlesonly', False)
        maxdepth = _get_theme_var_int(context, 'theme_mochi_navtree_maxdepth', -1)

        toctree_html = fn_toctree(
            collapse=False,
            titles_only=titles_only,
            maxdepth=maxdepth,
            includehidden=True
        )
    else:
        toctree_html = ""

    return toctree_html

def _should_hide_page_toc(context: Ctx, *, builder: StandaloneHTMLBuilder, docname: str) -> bool:
    """return boolean flag to disable page-toc if condition is not met"""
    file_meta = context.get("meta", None) or {}
    if "hide-toc" in file_meta:
        return True
    elif "toc" not in context:
        return True
    elif not context["toc"]:
        return True
    
    toctree = TocTree(builder.env).get_toc_for(docname, builder)
    try:
        self_toctree = toctree[0][1]
    except IndexError:
        val = True
    else:
        # There's only the page's own toctree in there.
        val = len(self_toctree) == 1 and self_toctree[0].tagname == "toctree"
    return val
    



def on_html_page_context(app: Sphinx, pagename: str, templatename: str, context: Ctx, doctree) -> None:
    # expose to the template engine
    context["_inspect"] = _inspect
    context["sidebar_toc"] = _create_sidebar_toc(_get_full_toctree(context))
    context["hide_page_toc"] = _should_hide_page_toc(context, builder=app.builder, docname=pagename)

def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_html_theme("sphinx_theme_mochi", path.abspath(path.dirname(__file__)))
    app.connect('html-page-context', on_html_page_context)

    return {}
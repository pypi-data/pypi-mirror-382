import json
import os
import string
from html import escape
from os import path
from xml.dom import minidom

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset_file


class svgio(nodes.General, nodes.Element):

    def __init__(self, abs_path: str, page: int):
        super().__init__()

        self.svg_file_path = abs_path
        self.page = page


def visit_svgio_node(self, node: svgio):
    self.body.append(self.starttag(node, "div"))

    svg_parsed = minidom.parse(node.svg_file_path)

    svg_tag = svg_parsed.getElementsByTagName("svg")

    xml_content = svg_tag[0].getAttribute("content")

    tmpl = string.Template(
        '<div class="mxgraph"'
        ' style="max-width:100%;border:1px solid transparent;"'
        ' data-mxgraph="$data">'
        "</div>"
    )

    json_data = {}
    json_data["xml"] = xml_content

    json_data["page"] = node.page
    json_data["nav"] = True
    json_data["toolbar"] = "pages layers tags"
    json_data["highlight"] = "#0000ff"

    mxgraph = tmpl.substitute(data=escape(json.dumps(json_data)))
    self.body.append(mxgraph)


def depart_svgio_node(self, node):
    self.body.append("</div>\n")


class SvgioDirective(SphinxDirective):

    option_spec = {
        "name": directives.unchanged,
        "page": directives.positive_int,
        "caption": directives.unchanged,
    }

    required_arguments = 1
    optional_arguments = 0

    def _validate_file(self, rel_filename: str, filename: str):

        if not os.path.isfile(filename):
            raise self.error(f"File {rel_filename} does not exist.")

        if not rel_filename.endswith(".drawio.svg"):
            raise self.error(
                'Only ".drawio.svg" '
                "file extension is valid for this directive."
            )

    def _add_caption(self, node: svgio):

        caption = self.options.get("caption")

        if caption is None:
            return node

        parsed = nodes.Element()
        self.state.nested_parse(
            ViewList([caption], source=""), self.content_offset, parsed
        )
        caption_node = nodes.caption(
            parsed[0].rawsource, "", *parsed[0].children
        )
        caption_node.source = parsed[0].source
        caption_node.line = parsed[0].line

        node += caption_node

        return node

    def run(self):

        rel_filename, filename = self.env.relfn2path(self.arguments[0])

        self._validate_file(rel_filename, filename)

        self.env.note_dependency(filename)

        node = svgio(
            filename,
            self.options["page"] - 1 if "page" in self.options else 0,
        )

        self.add_name(node)

        return [self._add_caption(node)]


def add_js(app: Sphinx):

    abs_js_path = path.join(
        app.builder.srcdir, app.config.drawio_js_offline_path
    )

    if os.path.isfile(abs_js_path) and abs_js_path.endswith(".js"):
        app.add_js_file(path.basename(abs_js_path), loading_method="defer")
    else:
        CRED = '\033[91m'
        CEND = '\033[0m'
        print(CRED + f"Bad drawio js path: {abs_js_path}" + CEND)


def build_finished(app: Sphinx, _exception):

    if app.config.drawio_js_offline_path:
        copy_asset_file(
            path.join(app.builder.srcdir, app.config.drawio_js_offline_path),
            path.join(app.builder.outdir, '_static'),
            app.builder)


def init_numfig_format(app, config):

    numfig_format = {"scheme": "Схема %s"}

    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def setup_extension(app: Sphinx):

    app.add_config_value("drawio_js_offline_path", "", "html")
    app.connect("config-inited", init_numfig_format)
    app.connect("builder-inited", add_js)
    app.connect('build-finished', build_finished)

    app.add_enumerable_node(
        svgio,
        figtype="scheme",
        html=(visit_svgio_node, depart_svgio_node),
    )
    app.add_directive("svgio", SvgioDirective)

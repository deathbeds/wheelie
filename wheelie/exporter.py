
# coding: utf-8

import nbconvert, black, traitlets, pathlib


class BlackExporter(nbconvert.exporters.python.PythonExporter):
    width = traitlets.Integer(default_value=100)

    def from_notebook_node(self, nb, resources=None, **kw):
        nb, resources = super().from_notebook_node(nb, resources=resources, **kw)
        return black.format_str(nb, self.width), resources


BlackExporter.exclude_input_prompt.default_value = True


if __name__ == "__main__":
    pathlib.Path("exporter.py").write_text(BlackExporter().from_filename("exporter.ipynb")[0])

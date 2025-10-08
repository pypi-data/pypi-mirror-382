# Sphinx SVG.IO Package

This is a simple extension for embedding draw.io diagramms into sphinx docs.

### Usage


In conf.py:
```python
extensions = ["sphinx_svgio"]

drawio_js_offline_path = "path/to/viewer-static.min.js" # relative to conf.py or absolute
```

In rst:

```rst
.. svgio:: path/to/scheme.drawio.svg
    :page: 1
    :name: some name
    :caption: some caption
```

With `page` option you can choose an initial page of complex draw.io scheme.

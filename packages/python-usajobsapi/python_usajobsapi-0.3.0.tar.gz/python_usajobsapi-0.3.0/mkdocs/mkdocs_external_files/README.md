# mkdocs-external-files

A lightweight [MkDocs](https://www.mkdocs.org/) plugin that allows you to directly include files outside your `docs_dir` into the site build.

## Features

- Pull individual files or glob patterns from anywhere outside your `docs_dir`.
- Resolve relative paths against the MkDocs configuration directory.
- Create real source `File` objects at build time.
- Automatically watch added sources during [live reload](https://www.mkdocs.org/user-guide/configuration/#live-reloading) (`mkdocs serve`).

## Installation

```bash
pip install mkdocs-external-files
# or with uv
uv pip install mkdocs-external-files
```

## Usage

- `src` accepts absolute paths or paths relative to the MkDocs config file.
- Glob patterns (`*`, `?`, `[]`) require `dest` to end with `/` to indicate a directory target.
- `dest` accepts relative paths to the `docs_dir`; during a build they are created in `site_dir`.

### Configuration

Enable the plugin and list the external sources inside `mkdocs.yml`:

```yaml
plugins:
  - search
  - external-files:
      files:
        - src: ../README.md
          dest: extras/README.md
        - src: ../assets/**
          dest: extras/assets/
```

### Behavior

- `mkdocs serve`: Sources are streamed directly; nothing is copied into `docs_dir`, but live reload will watch the resolved absolute paths.
- `mkdocs build`: Virtual files are materialized into `site_dir`, so deployments that publish only the build output still include the added sources.
- Missing sources will result in a `FileNotFoundError` exception.

## Troubleshooting

If you are using [`mkdocs-gen-files`](https://github.com/oprypin/mkdocs-gen-files) then you _must_ place `mkdocs-external-files` after `mkdocs-gen-files` in your plugin settings.

```yaml
plugins:
  - search
  - gen-files:
      scripts:
        - gen_ref_pages.py
  - external-files:
      files:
        - src: ../README.md
          dest: extras/README.md
```

## Contributing

Contributions are welcome! To get started:

1. Fork the repository and create a new branch.
2. Create a virtual environment and install development dependencies.
3. Run the test suite with `pytest` and ensure all tests pass.
4. Submit a pull request describing your changes.

Please open an issue first for major changes to discuss your proposal.

## License

Distributed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.

# Version_builder

**A lightweight tool for managing Git tags and versioning in CI/CD pipelines.**


### Why?
-  Easy to use  
- Works with Git tags  
- Simple CLI interface  
- Designed for CI/CD integration  
- Logging support  
- Fully testable

### Usage

```bash
version_builder -b patch -tf pyproject.toml
```

```bash
usage: version_builder [-h] [-v] [-s] [-b {major,minor,patch}] [-tf TOML_FILE] [-vf VERSION_FILE]

options:
  -h, --help            show this help message and exit
  -v, --builder-version
                        Show builder version (default: False)
  -s, --show            Show last tag (default: False)
  -b {major,minor,patch}, --bump {major,minor,patch}
                        Bump version (default: patch) (default: None)
  -tf TOML_FILE, --toml-file TOML_FILE
                        Path to the toml file (default: not set) (default: None)
  -vf VERSION_FILE, --version-file VERSION_FILE
                        Path to the version file (default: not set) (default: None)

```

### Installation

```bash
pip install version_builder
```

### License

MIT License — feel free to use it in any project! 🎉

### Author

Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)


### Gitverse

[https://gitverse.ru/dkurchigin/version_builder](https://gitverse.ru/dkurchigin/version_builder)

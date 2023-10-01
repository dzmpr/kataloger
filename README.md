## Cataloger


[![Python version](https://img.shields.io/badge/python-3.11-blue.svg)](https://pypi.python.org/pypi/kataloger)
[![Tests](https://github.com/dzmpr/kataloger/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/dzmpr/kataloger/actions/workflows/run-tests.yml)
[![Latest version](https://img.shields.io/pypi/v/kataloger.svg?style=flat&label=Latest&color=%234B78E6&logo=&logoColor=white)](https://pypi.python.org/pypi/kataloger)

Cataloger can help update your project dependencies with ease! All you need is point to `libs.versions.toml` file and supply it with repositories that you use in project.

### How to use?
#### CLI mode
Cataloger offers handy CLI mode which you can use locally or on CI:

```commandline
pip install kataloger
kataloger -p /ProjectDir/libs.versions.toml -rp /ProjectDir/default.repositories.toml
```

Or you can omit paths to version catalog and repositories if they are located in current working directory:

```commandline
pip install kataloger
cd /ProjectDir
kataloger
```

#### CLI options

`-p [path]` or `--path [path]` — specifies path to gradle version catalog file. If no path provided kataloger try to find version catalog with default name `libs.versions.toml` in current working directory.  
`-rp [path]` or `--repositories-path [path]` — specifies path to .toml file with repositories credentials where updates will be looked for. If no path provided kataloger try to find repositories file with default name `default.repositories.toml` in current working directory.  
`-v` or `--verbose` — if specified print more info to console.  
`-u` or `--suggest-unstable` — if specified suggest artifact update from stable version to unstable.  
`-f` or `--fail-on-updates` — if specified return non-zero exit code when at least one update found. Can be useful on CI.  

#### Integrate cataloger to your python script
Cataloger has convenient API (I did my best), so you can install it from pip and use in any script.

### Roadmap

- [ ] Support check multiple catalogs
- [ ] Support all notations in version catalog
- [ ] Support advanced update configuration
- [ ] Support Python <3.11

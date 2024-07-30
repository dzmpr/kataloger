## Kataloger

[![Python version](https://img.shields.io/badge/python-3.8-blue.svg)](https://pypi.python.org/pypi/kataloger)
[![Latest version](https://img.shields.io/pypi/v/kataloger.svg?style=flat&label=Latest&color=%234B78E6&logo=&logoColor=white)](https://pypi.python.org/pypi/kataloger)
[![Downloads](https://static.pepy.tech/badge/kataloger/month)](https://pepy.tech/project/kataloger)
[![Tests](https://github.com/dzmpr/kataloger/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/dzmpr/kataloger/actions/workflows/run-tests.yml)

Kataloger can help update your project dependencies with ease! All you need is point to `libs.versions.toml` file and supply it with repositories that you use in project.

### Features
- Better than Android Studio built-in tool :)
- Gradle-free
- Can be used on CI
- Flexible and open-source

### How to use?
Kataloger offers handy CLI which you can use locally or on CI.

You can pass path to version catalog using `-p` parameter and path to configuration with `-c` parameter:
```commandline
kataloger -p ~/ProjectDir/libs.versions.toml -c ~/ProjectDir/default.configuration.toml
```
Repositories, where artifact updates will be searched for, should be specified in configuration file separately for libraries and plugins as shown below:
```toml
# ...
[libraries]
library_repository = "https://repository.link/library"

[plugins]
plugin_repository = "https://repository.link/plugin"
```
> Tip: You can use [default](./src/kataloger/default.configuration.toml) configuration file as template.

Paths to catalogs also can be specified in configuration file:
```toml
# ...
[catalogs]
androix_catalog = "./androidx.versions.toml"
kotlin_catalog = "./kotlin.versions.toml"
```
> Important: Relative paths are resolved to the root directory of configuration.

And then you need specify only path to configuration:

```commandline
kataloger -c ~/ProjectDir/project.configuration.toml
```

Or you can omit all parameters if configuration file or catalogs are located in current working directory. In this mode kataloger trying to find all catalogs (files with `.versions.toml` extension) and configuration in `default.configuration.toml` file in current directory:

```commandline
cd ~/ProjectDir
kataloger
```

If configuration file not provided and can't be found in current working directory kataloger will use [default](./src/kataloger/default.configuration.toml) configuration with next repositories: Maven Central, Google Maven and Gradle Plugin Portal.

```commandline
kataloger -p ~/ProjectDir/libs.versions.toml
```

#### CLI options

`-p [path]` or `--path [path]` — specifies path to gradle version catalog file. You can pass more than one version catalog path. If no path provided kataloger try to find version catalogs (files with extension `.versions.toml`) in current working directory.  
`-c [path]` or `--configuration [path]` — specifies path to .toml file with repositories credentials where updates will be looked for. If no path provided kataloger try to find default repositories file with name `default.configuration.toml` in current working directory. If repositories can't be found in current directory kataloger use predefined set of repositories (Maven Central, Google and Gradle Plugin Portal).  
`-v` or `--verbose` — if specified print more info to console.  
`-u` or `--suggest-unstable` — if specified suggest artifact update from stable version to unstable.  
`-f` or `--fail-on-updates` — if specified return non-zero exit code when at least one update found. Can be useful on CI.  

### Installation

Kataloger available in Python Package Index (PyPI). You can install kataloger using pip (requires python 3.8 and greater):
```commandline
pip install kataloger
```

### Use kataloger in python scripts
Kataloger has convenient API (I did my best), so you can write custom logic on top. More info about it can be found [here](./src/kataloger/update_resolver).

### License

```text
Copyright 2023 Dzmitry Pryskoka

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

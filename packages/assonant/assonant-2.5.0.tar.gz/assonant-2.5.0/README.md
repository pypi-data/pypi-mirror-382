<h1 align="center">
    Welcome to Assonant 🎶 𝄇
</h1>
<p align="center">
    <em>A beamline-agnostic event processing engine for data collection and organization</em>
</p>
<p align="center">
<a href="https://gitlab.cnpem.br/GCD/data-management/assonant#readme" target="_blank">
    <img alt="Version" src="https://img.shields.io/badge/version-2.5.0-blue.svg?cacheSeconds=2592000"/>
</a>
<a href="https://gitlab.cnpem.br/GCD/data-science/data-management/assonant/commits/dev" target="_blank">
    <img alt="Maintenance" src="https://img.shields.io/badge/Developing%3F-yes-green.svg"/>
</a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/badge/pyversions-3.8|3.9|3.10|3.11-green" alt="Supported Python versions">
</a>
</p>

---

## Description

A Beamline-agnostic event processing engine for data collection and organization (Assonant).

This package provides to beamline groups from the [Brazilian Synchrotron Light Laboratory (LNLS)](https://lnls.cnpem.br/) a python API to send metadata, produced during an experiment, to a data management system, responsible to mantain and organize the metadata produced at [Sirius](https://lnls.cnpem.br/sirius-en/).

The Assonant package is composed by public and private modules. Private modules are used by Assonant developers to implemented features that is furtherly exposed through public modules to abstract from final user how to handle specific platforms behaviors. In other words, if you are a beamline developer, don't care about what is inside any private module. Public modules are designed for being used by beamline developers in order to allow easy usage of Assonant resources. To differ private and public modules, private modules names are preceded by a '_':

- **🔒 Private Modules 🔒**

    -   **[_kafka](/assonant/_kafka/)**

        Assonant tools for dealing with anything related to [Kafka](https://kafka.apache.org/).

    -   **[_nexus](/assonant/_nexus/)**

        Assonant tools for dealing with anything related to [NeXus format](https://github.com/nexpy/nexusformat).

- **🔓 Public Modules 🔓**

    -   **[data_classes](/assonant/data_classes/)**

        A group of data classes that defines data schemas to be used all over Assonant modules in order
        to standardize data acquisiton, transference, manipulation and storage.

    -   **[file_writer](/assonant/file_writer/)**

        Assonant tools for writing data from within Assonant Data Classes into specific file format

    -   **[data_logger](/assonant/data_logger/)**

        Assonant tools for logging collect data.

    -   **[data_retriever](/assonant/data_retriever/)**

        Assonant tools for retrieving data from different sources.

    -   **[data_sender](/assonant/data_sender/)**

        Assonant tools for dealing with Assonant Data Classes transference over different types
        of communication method (e.g: Kafka topics).

 

## Code development standards

1. When importing anything from within a module to use internally on that module use relative paths.

2. When importing anything from a module, do not use an absolute path, instead use what is being made public by the module.

3. Classes, methods and settings that will be usable from outside the module, should be exposed on __\_\_init\_\_.py__ files

4. Private methods, files and modules should always have their name preceded by '_'.

### Users

Assonant is currently published at the public PyPi server meaning it can be simply installed using pip. It has also been modularized to allow installing the specific dependecies for its features. that said, depending on your use case you will run different command lines:  


* To install **Assonant DataLogger module** dependencies, run the following command line:

```bash
python -m pip install assonant[data-logger]
```

* To install Assonant to access the naming standards defined in it, run the following command line:

```bash
python -m pip install assonant[naming-standards]
```

* To install Assonant to access the path builder submodule, run the following command line:

```bash
python -m pip install assonant[path-builder]
```

* To install all Assonant dependecies, run the following command line:
```bash

python -m pip install assonant[full]
```

### Developers

1. First of all, If you want to prepare a development environment, clone the repository into your local machine:

2. Secondly install assonant by executing pip install . inside the cloned repository
```bash
python -m pip install -e .[dev]
```

3. After that install the pre-commit modules.
duf
```bash
pre-commit install --install-hooks -t pre-commit -t commit-msg
```

## Deploy

1. Firstly, remember to update the version value in this README file badge, and on the pyproject.toml file.

2. Secondly, you will need to build your package:

```bash
python -m build
```

3. After that you need to send the new version to the Global PyPi version by executing the following command line. Exchange the <package_version> place holder by the current version that will be deployed:


```bash
twine upload --repository pypi dist/assonant-<package_version>* --verbose
```

**Note**: *To deploy a new version you will need a PyPi token which only the project maintainers have. That said, if you are a project maintainer and don't have access to it, ask your leader for it.*

---

## Mantainers

-   👤 **Allan Pinto**
-   👤 **Paulo B. Mausbach**

<!-- ---

## 🤝 Contributing

---

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://gitlab.cnpem.br/GCDdata-management/assonant/issues). You can also take a look at the [contributing guide](https://gitlab.cnpem.br/GCD/data-management/assonant/blob/master/CONTRIBUTING.md) -->

---

## Credits

-   **[Apache Kafka](https://github.com/apache/kafka)**
-   **[Confluent's Kafka Python Client](https://github.com/confluentinc/confluent-kafka-python)**
-   **[Dockerfile for Apache Kafka](https://github.com/wurstmeister/kafka-docker)**
-   **[JSON schema for NeXus files](https://github.com/ess-dmsc/nexus-json)**
-   **[NeXus Data Format](https://www.nexusformat.org/)**
-   **[Nexusformat (python package)](https://github.com/nexpy/nexusformat)**
-   **[Pydantic](https://github.com/pydantic/pydantic)**

---

## License

_TODO: Define a License_

---

<!-- This project is [MIT](https://gitlab.cnpem.br/GCD/data-management/assonant/blob/master/LICENSE) licensed. -->

<img align="centre" alt="overlapping arrows" height="92" src="icons/mabel.svg" />

## mabel is a Data Engineering platform designed to run in serverless environments.

**mabel** just runs when you need it, scaling to zero, making it efficient and ideal for deployments to platforms like Kubernetes, GCP Cloud Run, AWS Fargate and Knative.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/mabel-dev/mabel/blob/master/LICENSE)
[![Status](https://img.shields.io/badge/status-beta-yellowgreen)](https://github.com/mabel-dev/mabel)
[![Regression Suite](https://github.com/mabel-dev/mabel/actions/workflows/regression_suite.yaml/badge.svg?style=flat-square)](https://github.com/mabel-dev/mabel/actions/workflows/regression_suite.yaml)
[![codecov](https://codecov.io/gh/mabel-dev/mabel/branch/main/graph/badge.svg?token=CYD6E4PPKR&style=flat-square)](https://codecov.io/gh/mabl-dev/mabel)
[![Static Analysis](https://github.com/mabel-dev/mabel/actions/workflows/static_analysis.yml/badge.svg?style=flat-square)](https://github.com/mabel-dev/mabel/actions/workflows/static_analysis.yml)
[![PyPI Latest Release](https://img.shields.io/pypi/v/mabel.svg)](https://pypi.org/project/mabel/)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=joocer_mabel&metric=sqale_rating&style=flat-square)](https://sonarcloud.io/dashboard?id=joocer_mabel)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=joocer_mabel&metric=security_rating&style=flat-square)](https://sonarcloud.io/dashboard?id=joocer_mabel)
[![mabel](https://snyk.io/advisor/python/mabel/badge.svg?style=flat-square)](https://snyk.io/advisor/python/mabel)
[![Downloads](https://pepy.tech/badge/mabel?style=flat-square)](https://pepy.tech/project/mabel)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![commit_freq](https://img.shields.io/github/commit-activity/m/mabel-dev/mabel)](https://github.com/mabel-dev/mabel/commits)
[![last_commit](https://img.shields.io/github/last-commit/mabel-dev/mabel)](https://github.com/mabel-dev/mabel/commits)
[![PyPI Latest Release](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://pypi.org/project/mabel/)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmabel-dev%2Fmabel.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmabel-dev%2Fmabel?ref=badge_shield)


- **Documentation** [GitHub Wiki](https://github.com/mabel-dev/mabel/wiki)  
- **Bug Reports** [GitHub Issues](https://github.com/mabel-dev/mabel/issues/new/choose)  
- **Feature Requests** [GitHub Issues](https://github.com/mabel-dev/mabel/issues/new/choose)  
- **Source Code**  [GitHub](https://github.com/mabel-dev/mabel)  
- **Discussions** [GitHub Discussions](https://github.com/mabel-dev/mabel/discussions)

## Focus on What Matters

We've built **mabel** to enable Data Analysts to write complex data engineering tasks quickly and easily, so they could get on with doing what they do best.

~~~python
from mabel import Reader

data = Reader(dataset="test_data")
print(data.count())
~~~

## Key Features

-  On-the-fly compression
-  Low-memory requirements, even with terabytes of data
-  Indexing and partitioning of data for fast reads 
-  Cursors for tracking reading position between processes 
-  Partial SQL DQL (Data Query Language) support 
-  Schema and [data_expectations](https://github.com/joocer/data_expectations) validation

## Installation

From PyPI (recommended)
~~~
pip install --upgrade mabel
~~~
From GitHub
~~~
pip install --upgrade git+https://github.com/mabel-dev/mabel
~~~


## Guides

[How to Read Data](https://github.com/mabel-dev/mabel/wiki/how_to_read_a_dataset)

## Dependencies

-  **[orjson](https://github.com/ijl/orjson)** for JSON (de)serialization
-  **[orso](https://github.com/mabel-dev/orso)** for data Schemas
-  **[zstandard](https://github.com/indygreg/python-zstandard)** for real-time on disk compression
-  **[LZ4](https://github.com/python-lz4/python-lz4)** for real-time in memory compression

There are a number of optional dependencies which are usually only required for specific features and functionality. These are listed in [tests/requirements.txt](https://github.com/mabel-dev/mabel/blob/main/tests/requirements.txt).

## Integrations

mabel comes with adapters for the following data services:

|   | Service |
|-- |-- |
| <img align="centre" alt="GCP Storage" height="48" src="icons/gcs-logo.png" /> | Google Cloud Storage |
| <img align="centre" alt="MinIo" height="48" src="icons/minio-logo.png" /> | MinIO |
| <img align="centre" alt="AWS S3" height="48" src="icons/s3-logo.png" /> | AWS S3 | 
| <img align="centre" alt="Azure" height="48" src="icons/azure.svg" /> | Azure Blob Storage |
| <img align="centre" alt="Local" height="48" src="icons/local-storage.png" /> | Local Storage |

Mabel is extensible with adapters for other data services as required.

## Deployment and Execution

mabel supports running on a range of platforms, including:

|   | Platform |
|-- |-- |
| <img align="centre" alt="Docker" height="48" src="icons/docker-logo.png" /> | Docker
| <img align="centre" alt="Kubernetes" height="48" src="icons/kubernetes-logo.svg" /> | Kubernetes
| <img align="centre" alt="Windows" height="48" src="icons/windows-logo.png" /> | Windows (<img align="centre" alt="Notice" height="12" src="icons/note.svg" />1)
| <img align="centre" alt="Linux" height="48" src="icons/linux-logo.jpg" /> | Linux (<img align="centre" alt="Notice" height="12" src="icons/note.svg" />2)
| <img align="centre" alt="Linux" height="48" src="icons/mac-os.png" /> | Mac (<img align="centre" alt="Notice" height="12" src="icons/note.svg" />3)

<img align="centre" alt="Notice" height="12" src="icons/note.svg" />1 - Some non-core features are not available on Windows.  
<img align="centre" alt="Notice" height="12" src="icons/note.svg" />2 - Tested on Debian (WSL) and Ubuntu.   
<img align="centre" alt="Notice" height="12" src="icons/note.svg" />3 - Tested on Apple Silicon Macs.

## How Can I Contribute?

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

If you have a suggestion for an improvement or a bug, [raise a ticket](https://github.com/mabel-dev/mabel/issues/new/choose) or start a [discussion](https://github.com/mabel-dev/mabel/discussions).

Want to help build mabel? See the [contribution guidance](https://github.com/mabel-dev/mabel/blob/main/.github/CONTRIBUTING.md).

## License

[Apache 2.0](LICENSE)


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fmabel-dev%2Fmabel.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fmabel-dev%2Fmabel?ref=badge_large)
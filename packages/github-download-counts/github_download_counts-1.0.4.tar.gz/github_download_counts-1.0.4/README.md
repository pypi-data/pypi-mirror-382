# github-download-counts

[![Latest Version](https://img.shields.io/pypi/v/github-download-counts)](https://pypi.python.org/pypi/github-download-counts/)

## Usage

```
usage: github_download_counts.py <arguments>

Display download statistics from GitHub repositories

* Access to the GitHub API is done using your personal access token (PAT).
  See https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
  for information about PATs.

options:
  --verbose, -v         Increase verbosity (e.g., -v, -vv, etc.)
  -t <str>, --token <str>
                        GitHub API token
  --token-file <str>    GitHub API token (read from filename)
  -r [REPOS ...], --repo [REPOS ...]
                        One or more GitHub repository/repositories (e.g., org/repo)
  --date-from <str>     Human readable date expression for beginning of search time frame (default: Jan 1 1970)
  --date-to <str>       Human readable date expression for ending of search time frame (default: now)
  --release [RELEASEREGEXES ...]
                        List of regular expressions against which to match releases (e.g., ^v24\.10)
  -a [ASSETREGEXES ...], --asset [ASSETREGEXES ...]
                        List of regular expressions against which to match release assets (e.g., ^\w+.+\.iso\.01$, ^foobar_.*\.tar\.gz$
  -i [IMAGEREGEXES ...], --image [IMAGEREGEXES ...]
                        List of regular expressions against which to match container images (e.g., ^foobar/barbaz$)
  --image-tag [IMAGETAGREGEXES ...]
                        List of regular expressions against which to match container image tags (e.g., ^24\.10)

```

## Installation

Using `pip`, to install the latest [release from PyPI](https://pypi.org/project/github-download-counts/):

```
python3 -m pip install -U github-download-counts
```

Or to install directly from GitHub:

```
python3 -m pip install -U 'git+https://github.com/mmguero/github-download-counts'
```

## Prerequisites

[github-download-counts](./src/github_download_counts/github_download_counts.py) requires:

* Python 3
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [dateparser](https://pypi.org/project/dateparser/)
* [github3.py](https://pypi.org/project/github3.py/)
* [mmguero](https://pypi.org/project/mmguero/)

## Contributing

If you'd like to help improve github-download-counts, pull requests will be welcomed!

## Authors

* **Seth Grover** - [mmguero](https://github.com/mmguero)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

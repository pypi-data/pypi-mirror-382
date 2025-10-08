# jaggimage-viewer
I was so used to my 25+ years old version of ACDSee to quickly see my files, i just made my own image viewer with Python and Qt.

![Screenshot. Jaguar picture by Charles J. Sharp on Wikipedia](media/screenshot.jpg)

## Installation

### From PyPI

This assumes you have either `Python` and `pip`, or `uv` installed.

With `pip`:

```shell
pip install jaggimage-viewer
```

With `uv`:

```shell
uv tool install jaggimage-viewer
```

### From sources

1. Have `uv` installed: https://docs.astral.sh/uv/#installation
1. Clone the repository:

    ```shell
    git clone https://github.com/clxjaguar/jaggimage-viewer.git
    ```

1. Run the installation:

    ```shell
    cd jaggimage-viewer
    uv build
    uv tool install .
    ```

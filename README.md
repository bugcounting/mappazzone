# Mappazzone!

*Mappazzone!* is a simple geolocalization board game, where players
have to place cities on a grid in a way that is consistent with their
geographical coordinates.


## Release bundles

The easiest way to install *Mappazzone!* is by using one of the
[release bundles](releases/latest) generated with PyInstaller.

## Installation

Building and installing the project should be possible on any system
that runs Python. In this section, we give concrete instructions for
GNU/Linux systems. Adjust for your system as needed.

### Dependencies

Besides Python, the app requires a number of libraries that are
platform-specific:
[Tk/TKinter](https://docs.python.org/3/library/tkinter.html),
[IDLE](https://docs.python.org/3/library/idle.html), and
[Pillow](https://pillow.readthedocs.io/en/stable/).

Here is how to install them in Debian/Ubuntu Linux distributions:

```bash
sudo apt install python3-tk idle3 python3-pil python3-pil.imagetk
```

Then, check that you have the building tools installed and up to date:

```bash
python3 -m pip install --upgrade pip setuptools wheel build hatch
```

### Virtual environment

Let's create a virtual environment `mpz` to easily install the project
and its dependencies.

```bash
python3 -m venv mappazzone
source mappazzone/bin/activate
```

### Building the project

If `$MAPPAZZONE` is the path to this repo's local copy, build the
project with:

```bash
cd "$MAPPAZZONE"
python3 -m build
```

This creates a directory `dist` under `$MAPPAZZONE` with the `.whl`
and `tar.gz` distribution packages.

### Installing the project

1. Build the project.

```bash
python3 -m pip install "$MAPPAZZONE"
```

This will install all dependencies, as well as a command `mappazzone`
that starts the game.

2. If you want to run the tests as well, build target `dev` and do an
   "editable" install with option `-e`:

```bash
python3 -m pip install -e "$MAPPAZZONE"'[dev]'
# Run the tests
cd "$MAPPAZZONE/tests"
pytest
```

3. You can also run directly the `mappazzone` main command:

```bash
cd "$MAPPAZZONE"
python3 -m src.mappazzone.mappazzone
```

### Build PyInstaller bundles

You can also create a bundle with
[PyInstaller](https://www.pyinstaller.org/) in your system.

1. Install the project in a virtual environment as described above, so
   that all dependencies are available locally.
   
2. Install the latest version of PyInstaller through `pip`.

```bash
python3 -m pip install --upgrade pyinstaller
```

3. Run PyInstaller.

```bash
cd "$MAPPAZZONE"
pyinstaller mappazzone.spec
```

This creates a self-contained directory `mappazzone` under
`$MAPPAZZONE/dist` with all dependencies (including a Python
interpreter). Run the script `mappazzone` in this bundle to run the
game.

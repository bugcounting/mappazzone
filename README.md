# Mappazzone!

*Mappazzone!* is a simple geolocalization board game, where players
have to place cities on a grid in a way that is consistent with their
geographical coordinates.

## Release bundles

The easiest way to install *Mappazzone!* is by using one of the
[release bundles](/../../releases/latest) generated with PyInstaller.

1. Download and unpack the archive bundle for your operating system.

2. Launch the executable `mappazzone` (or `mappazzone.exe`) in the
   unpacked directory.

`mappazzone` tries to determine the system's language, and uses it for
its UI. This detection does not always works, in which case it falls
back to English. Alternatively, you can specify your language using
the `--language` command-line option. Currently, there is only support
for English (`EN`) and Italian (`IT`).

### Running in Windows

Unfortunately, there are a few complications in Windows, where Windows
Defender [flags the Pyinstaller executable as a
trojan](https://stackoverflow.com/questions/44377666/pyinstaller-exe-throws-windows-defender-no-publisher)
:-(.

A workaround for that is [adding a security
exception](https://stackoverflow.com/a/54734084):

1. Go to `Start > Settings > Update & Security > Windows Security >
   Virus & threat protection`.
   
2. Select `Manage settings`. Under `Exclusions` select `Add or remove
   exclusions`.
   
3. Select `Add an exclusion > Folder`, and select the whole folder
   that you unpacked from the bundle.
   
Now, you should be able to run `mappazzone.exe` without issues.
However, if you try to add a shortcut to `mappazzone.exe` from a
location that is outside the folder with the exception, the shortcut
will still be blocked by Defender. Thus, either put the shortcut
within the same excluded folder, or add an exception for the shortcut
file.

Finally, if you want to pass command line options to `mappazzone.exe`,
you should edit the `Target` field of the shortcut (`Right click >
Properties > Shortcut tab`). Put the full path to `mappazzone.exe`
between double quotation marks, and then add the command-line options
outside the quotation marks. For example:
`"C:\Users\...\mappazzone\mappazzone.exe" --language IT`.

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
sudo apt install python3-venv python3-tk idle3 python3-pil python3-pil.imagetk
```

Alternatively, install
[Miniconda](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html),
create an environment `mpz`, and then install the dependencies within
it. This works on every system where you can install Anaconda, and
does not mess with your system's main libraries.

```bash
conda create --name mpz
conda activate mpz
conda install python=3.10 pillow  # Dropping =3.10 should also work
# On Linux, add support for freetype fonts, which look nicer.
# The installer may ask you to downgrade, which is OK.
conda install -c conda-forge tk=*=xft_*
```

### Virtual environment

Let's create a virtual environment `mpz` to easily install the project
and its dependencies.

```bash
python3 -m venv mpz
# Linux/macOS
source mpz/bin/activate
# Windows
mpz\Scripts\activate.bat
```

Finally, install the building tools in the virtual environment:

```bash
python3 -m pip install --upgrade pip setuptools wheel build hatch
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
(or `mappazzone.exe`) that starts the game.

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

## Debugging

Unless it is explicitly disabled with the `--nolog` command-line
option, `mappazzone` writes a log of operations in the current user
`$USER`'s log directory. This is
`/home/$USER/.local/state/mappazzone/log/` in Linux,
`C:\Users\$USER\AppData\Local\mappazzone\mappazzone\Logs\` in Windows,
and `/Users/$USER/Library/Logs/mappazzone/` in macOS.

`mappazzone` saves several log files, one per run. The latest log file
is always named `mappazzone.log`. If you find a bug, report it with
the corresponding log file.

To change to `$DIR` the location where log files are saved, use the
`--logdir $DIR` command-line option.

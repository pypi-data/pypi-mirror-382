[![DOI](https://zenodo.org/badge/549013816.svg)](https://zenodo.org/doi/10.5281/zenodo.7189660)

# Dorn

Dorn is a GUI for generating individualised close contact restrictions for nuclear medicine patients, particularly radionuclide therapy patients.

## Executable provided with release

Each release on GitHub includes a zip file.  The zip file contains an executable file `Dorn.exe` that can be used to run the Dorn program on Windows 10 and 11 systems without needing to install Python and Dorn's other dependencies.

## Installation

Dorn can be installed as a Python package if you have Python version 3.9 or higher.  In the directory containing the `pyproject.toml` file:

    python -m pip install .

Then run the command `dorn` to start the GUI.

## glowgreen package

Dorn uses the Python package [glowgreen](https://github.com/SAMI-Medical-Physics/glowgreen) for calculating radiation dose from contact patterns and restriction periods.

## Building your own standalone executable

In the directory containing the `pyproject.toml` file:

    python -m pip install . .[windows] .[freeze]
    cxfreeze build

This generates a directory called something like `build/exe.win-amd64-3.11` containing a file `Dorn.exe`.  You can copy the `exe.win-amd64-3.11` directory to another computer (of the same architecture) and run Dorn from the Dorn.exe file.

## Creating the icon file

The icon file `icofile.ico` was generated from `shovel.png` in Python.
Something like:

    python -m pip install Pillow

Then

    from PIL import Image
    filename = 'shovel.png'
    img = Image.open(filename)
    icon_sizes = [(16,16), (32, 32), (48, 48), (64,64)]
    img.save('new_icofile.ico', sizes=icon_sizes)

## Source
https://github.com/SAMI-Medical-Physics/dorn

## Bug tracker
https://github.com/SAMI-Medical-Physics/dorn/issues

## Author
Jake Forster (jake.forster@sa.gov.au)

## Copyright
Dorn is copyright (C) 2022-2025 South Australia Medical Imaging.

## License
MIT License.  See LICENSE file.

## Citation
See CITATION.cff file.

## Acknowledgments
The Dorn icon was designed by Kevin Hickson.

---------------------------------------

## Development

### Program overview

- Patient data is stored in an ordered dictionary.  Program reads/writes patient data to XML file.

- Program settings are stored in another ordered dictionary, which reads/writes to `settings.xml` in the user's configuration directory.  On Windows this is `C:\Users\<USER>\AppData\Local\Dorn\Dorn\settings.xml`.  For backward compatibility, if there is a `settings.xml` in the current working directory, that file will be used instead.

- Some settings cannot be edited via the GUI, such as the therapy options and the radionuclide data.
The user may add at most 1 additional therapy options with measured clearance data and 1 additional therapy option with generic clearance via the command line interface (see below).

- A command-line interface is provided that offers additional flexibility.  To see the command line options, enter:

        dorn -h

    or with the executable:

        Dorn.exe -h

### Ideas for new features

- For therapy options that use generic clearance, allow the user to provide an initial dose rate measurement to determine the clearance function parameter: initial dose rate at 1 m.
- Add more dose rate measurement time points and a scroll bar.
- Add curve fit model representing no excretion at night.  The difficulty will be adding the support in `glowgreen`.
- Add a name field for the detector.
- Attempt to propagate uncertainty from the contact pattern onto the calculated restriction period or dose.
- Allow the user to edit/add contact patterns.

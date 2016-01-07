# sffmsexport

## What it is

**sffmsexport** is a script to convert latex projects using the
[sffms](http://www.mcdemarco.net/sffms/) package to rtf files.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

### Requirements

**sffmsexport** runs on Linux (tested in Archlinux only with python 3.5).

### Installation

After cloning this repository, run:

    $ sudo python setup.py install

To uninstall, run:

    $ sudo pip uninstall sffmsexport

### Usage

    $ sffmsexport -h
    usage: sffmsexport [-h] [-i FILE] [-o OUTPUT]

    sffmsexport.

    optional arguments:
      -h, --help            show this help message and exit
      -i FILE, --input FILE
                            Main tex file.
      -o OUTPUT, --output OUTPUT
                            Output file, if necessary.





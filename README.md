# sffms_to_rtf

## What it is

**sffms_to_rtf** is a script to convert latex projects using the
[sffms](http://www.mcdemarco.net/sffms/) package to rtf files.

Inspired by [sffms2rtf](https://github.com/ZungBang/sffms2rtf).

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

### Requirements

**sffms_to_rtf** runs on Linux (tested in Archlinux only with python 3.5).

### Installation

After cloning this repository, run:

    $ sudo python setup.py install

To uninstall, run:

    $ sudo pip uninstall sffms_to_rtf

### Usage

    $ sffms_to_rtf -h
    usage: sffms_to_rtf [-h] [-i FILE] [-o OUTPUT]

    sffmsexport.

    optional arguments:
      -h, --help            show this help message and exit
      -i FILE, --input FILE
                            Main tex file.

The converted rtf file is generated in the same directory as the source.





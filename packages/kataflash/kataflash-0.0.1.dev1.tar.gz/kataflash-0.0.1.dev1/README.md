# Kataflash

## Synopsis
Kataflash is a repackaging of the flashtool included in [Katapult](https://github.com/Arksine/katapult).

This is intended for power-users to leverage devices with katapult already installed w/o needing to clone the entire repo.

## Status
Work in progres: Pre-alpha.

## Installation

### With pip

It is reccomended to do this in a virtual environment (THIS IS BROKEN DON'T USE)
```
pip install git+https://github.com/laikulo/kataflash.git
```

### With pipx automatic environment management
```
pipx install git+https://github.com/laiuklo/kataflash.git
```

## Usage
Kataflash provides two commands:

### `kataflash`
This is kataflash's main entrypoint. It provides a few quality-of-life improvements over the basic flashtool.

__NOT YET IMPLEMENTED__

### `kataflashtool`
This is a transparent wrapper around the vendored flashtool.py, it see [Upstream Docs](https://github.com/Arksine/katapult?tab=readme-ov-file#flash-tool-usage) for usage information.

## Building
The vendored script is not part of this repo, and is downloaded by the `Makefile`.

At this early stage of development, it is nessacary to download and package this before building an sdist or wheel



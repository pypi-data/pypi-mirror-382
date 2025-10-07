# Welcome to AstroParse!

## About

Having trouble reading data tables into Python using conventional methods like
Pandas or Astropy? AstroParse is the right package for you! It is a simple,
customizable tool that allows you to parse text data from sources with 
non-standard formats. This package originally targeted astronomical data 
that often come in irregular text forms that are not easy to read by both 
humans and Python.

## Getting Started

Install AstroParse to your Python environment:

```pip install astroparse```

To parse an individual file:

```from astroparse import parse_file```

To access the flexible `Reader` class:

```from astroparse import Reader```

The `Reader` allows users to parse multiple files at once. The method 
`Reader.read_lists` is best for parsing multiple files of similar formats 
and structure; the method `Reader.read_dicts` is best for parsing multiple 
files of different formats or structures. All methods use the same or 
similar interface to `parse_file`. See more **documentation here**:
https://astroparse.readthedocs.io/en/latest/.

## Next Steps

Check out the examples in `/examples`!


# DMItoGIF
A python program to allow creation of GIFs and PNGs directly from DMI files for BYOND.

Currently does NOT support frames with decimal delays.
Any decimal delays will be rounded to the nearest number, or 1 if below 1.
This is because PIL doesn't support gifs with changing fps.
To get around this, delays are just copied image frames over and over.

Some of the methods here are somewhat hacky and may break in the future, or depending on your PIL installation.

## Use
Download dmitogif.py, and run the file in a terminal.
Select your .dmi file.
use /list or type in your icon state.
If the icon_state has multiple directions, pick between front facing or all directions.
Choose an image size multiplier.
The output file (gif or png) will be created in the same directory as the dmitogif.py file.

## Dependencies
Python Image Library (PIL)

# pyrandomart
Python library to produce randomart text from a bytes object

This module contains a function to turn a bytes object into a randomart
string.
see: [http://www.dirk-loss.de/sshvis/drunken_bishop.pdf](http://www.dirk-loss.de/sshvis/drunken_bishop.pdf)
for a description of randomart

## Installation
Try either:

```shell
pip install pyrandomart
```
or directly from github
```shell
pip install git+https://github.com/aaronm6/pyrandomart.git
```

## Usage
The only function in this package that is useful to import is the last one, '`randomart`'. So the recommended usage is:
```shell
>>> from pyrandomart import randomart
```
`randomart`'s call signature and explantion of inputs:
```shell
randomart(bStr, header='RSA 4096', footer='SHA256', dims=(9, 17), box='clean')
```
- `bStr`: Bytes object with the hash to be turned into randomart
- `header`: Str object to be displayed at the header of the randomart box
- `footer`: Str object to be displayed at the footer of the randomart box
- `dims`: List or tuple object with dimensions of the randomart box (rows, columns). Dims must be odd ints.
- `box`: Describes the characters that make up the border of the randomart box.  Input value can be 'clean' or 'simple', or a custom dict object can be provided.

For example, to turn a bytes object consisting of byte values 30 through 60 into randomart and print:
```shell
>>> bobj = bytes(range(30,60))
>>> print(randomart(bobj, header='30-60', footer='no hash'))
┏━━━━━[30-60]━━━━━┓
┃@===+o.          ┃
┃XO.*+...         ┃
┃= o o . .        ┃
┃Xo     . .       ┃
┃+Oo     S .      ┃
┃BE.    . o .     ┃
┃=o.     . .      ┃
┃o.               ┃
┃.o.              ┃
┗━━━━[no hash]━━━━┛
```

### Notes
- The randomart here corresponds to the bytes given in bytes-object bStr.  However, often a cryptographic hash is given in the base64 representation of the bytes (e.g. when generating an ssh key).  In this case, one can simply import the standard library 'base64' and decode the base64 hash to bytes using `base64.b64decode(..)` and then pass the result to this randomart function.
- The number of columns should be large enough to accommodate the header and footer provided.  However, this is not explicitly checked, because it's your life. The function will still work if not, but it may look funky.
 


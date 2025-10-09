# MIT License
# 
# Copyright (c) 2025 Aaron M.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
This module contains a function to turn a bytes object into a randomart
string.
see: http://www.dirk-loss.de/sshvis/drunken_bishop.pdf
for a description of randomart

Basically the only function in this file that is useful to import is 
the last one, 'randomart'. So the recommended usage is:
from pyrandomart import randomart
"""

__all__ = ['randomart']

# There is a character code for how many times a particular square has been hit
_valChars = ' .o+=*BOX@%&#/^'

def _get8bits(num):
    """
    Turn a number into an length-8 bit string of 0s and 1s
    """
    # num is an int
    bString = bin(num)[2:]
    bOut = '0'*(8-len(bString)) + bString
    return bOut

def _group2bits(bitString):
    """
    Turn a string of 0s and 1s, group into pairs of two characters and 
    return a list with these pairs
    """
    assert len(bitString)%2 == 0, \
        "The length of the bitstring must be an even number"
    iterList = [iter(bitString)]*2
    bitPairList = [''.join(item) for item in zip(*iterList)]
    return bitPairList

def _bytes2bitpairs(bStr):
    """
    Takes a bytes object and returns a list of bit pairs. Bytes are 
    read left-to-right, but within a byte, bitpairs are read 
    right-to-left
    """
    list_of_bit_pairs = [_group2bits(_get8bits(item)) for item in bStr]
    pair_list = [item for 
        sublist in list_of_bit_pairs for 
        item in sublist[-1::-1]]
    return pair_list

def _gen_xy_positions(bit_pair_string, dims=(9, 17)):
    """
    Takes a list of bit pairs and returns a list of positions in the 
    path.
    """
    pairPositions = [(dims[1]//2, dims[0]//2)] #
    for pair in bit_pair_string:
        dx = -1 if pair[-1] == '0' else 1
        dy = -1 if pair[0] == '0' else 1
        newX = pairPositions[-1][0] + dx
        newX = max(0, newX)
        newX = min(dims[1]-1, newX) #
        newY = pairPositions[-1][1] + dy
        newY = max(0, newY)
        newY = min(dims[0]-1, newY) #
        pairPositions.append((newX, newY))
    return pairPositions

def _coord_pair_to_position(cpair, dims=(9, 17)):
    """
    cpair should be a length-2 tuple with (x, y) coordinates.
    This ordered pair gets converted to a single number.  If the rows 
    and 17 columns are broken up row-by-row and appended, then the 
    position number is the index of the spot along this single array.
    """
    pos = cpair[1]*dims[1] + cpair[0] #
    return pos

_bc = {} # "bc" = "box characters", i.e. the characters that make up the border of the box
_bc['clean'] = {
    'tl': chr(0x250f),
    'tr': chr(0x2513),
    'bl': chr(0x2517),
    'br': chr(0x251b),
    'hline': chr(0x2501),
    'vline': chr(0x2503)}
_bc['simple'] = {
    'tl': '+',
    'tr': '+',
    'bl': '+',
    'br': '+',
    'hline': '-',
    'vline': '|'}

def _gen_header_footer_line(label, poz=None, dims=None, box=None):
    pre_space = (dims[1]-min(dims[1]-2,len(label))-2)//2 #
    post_space = (dims[1]-min(dims[1]-2,len(label))-2) - pre_space #
    if poz == 'header':
        lcor = box['tl']
        rcor = box['tr']
    elif poz == 'footer':
        lcor = box['bl']
        rcor = box['br']
    else:
        raise ValueError("Cannot interpret kwarg 'poz'")
    line_text = lcor + box['hline']*pre_space + '[' + label[:(dims[1]-2)] + ']' + \
        box['hline']*post_space + rcor
    return line_text

def randomart(bStr, header='RSA 4096', footer='SHA256', dims=(9, 17), box='clean'):
    """
    This function takes a bytes object ('bStr') and generates the 
    corresponding random art string.
    
    Inputs:
        bStr: Bytes object with the hash to be turned into randomart
      header: Str object to be displayed at the header of the randomart box
      footer: Str object to be displayed at the footer of the randomart box
        dims: List or tuple object with dimensions of the randomart box.  
              Dims must be odd ints.  dims = (rows, columns)
         box: str or dict which describes what characters will form the border
              of the randomart box.  If a str, then it must be 'clean' or 
              'simple'.  If a dict, it must have these keys defined:
                'tl': top-left character
                'tr': top-right character
                'bl': bottom-left character
                'br': bottom-right character
                'hline': horizontal line character, i.e. top a and bottom of box
                'vline': vertical line character, i.e. left and right of box
    Output:
     randomart_text: Str object with randomart text corresponding to input bStr
     
    Notes:
      * The number of columns should be large enough to accommodate the header
        and footer provided.  However, this is not explicitly checked, because
        it's your life. The function will still work if not, but it may look 
        funky.
    
      * The randomart here corresponds to the bytes given in bytes-object bStr.
        However, often a cryptographic hash is given in the base64 
        representation of the bytes (e.g. when generating an ssh key).  In this 
        case, one can simply import the standard library 'base64' and decode 
        the base64 hash to bytes using
            base64.b64decode(..)
        and then pass the result to this randomart function.
    """
    if not isinstance(bStr, bytes):
        raise TypeError("Positional input 'bStr' must be a bytes object")
    if not isinstance(header, str):
        raise TypeError("Keyword argument 'header' must be a string object")
    if not isinstance(footer, str):
        raise TypeError("Keyword argument 'footer' must be a string object")
    if not isinstance(dims, (list, tuple)):
        raise TypeError("Keyword argument 'dims' must be a list or tuple")
    if not len(dims) >= 2:
        raise TypeError("Keyword argument 'dims' must have at least two elements")
    if not all([isinstance(item, int) for item in dims]):
        raise TypeError("Elements in keyword argument 'dims' must be of type int")
    if not (dims[0] % 2) == 1:
        raise ValueError("Number of rows must be odd")
    if not (dims[1] % 2) == 1:
        raise ValueError("Number of columns must be odd")
    if not isinstance(box, (str, dict)):
        raise TypeError("Keyword argument 'box' must be a str or dict object")
    bc = None
    if isinstance(box,str):
        if box.lower() not in ('clean','simple'):
            raise ValueError("Keyword argument 'box' must be 'clean' or 'simple' if it's a string")
        bc = _bc[box]
    if isinstance(box,dict):
        if not all([item in box for item in _bc['clean']]):
            raise ValueError("box as a dict must have keys: 'tl', 'tr', 'bl', 'br', 'hline', 'vline'")
        if not all([isinstance(box[item], str) and len(box[item])==1 for item in box]):
            raise ValueError("box dict values must be single-character strings")
        bc = box
    bitPairs = _bytes2bitpairs(bStr)
    xyPosList = _gen_xy_positions(bitPairs, dims=dims)
    posnumList = [_coord_pair_to_position(pair, dims=dims) for 
        pair in xyPosList]
    boardPosList = [0]*dims[0]*dims[1]
    for pos in posnumList:
        boardPosList[pos] += 1
    boardPosList = [min(pos,len(_valChars)-1) for 
        pos in boardPosList] # truncate the list
    boardCharList = [_valChars[pos] for pos in boardPosList]
    startPos = dims[1]*(dims[0]//2) + (dims[1]//2) #
    boardCharList[startPos] = 'S'
    boardCharList[posnumList[-1]] = 'E'
    boardCharStr = ''.join(boardCharList)
    #vline = chr(0x2503)
    # split up the str in chunks of dims[1] (i.e. into rows)
    iterList = [iter(boardCharStr)]*dims[1] #
    boardCharStrChunks = [''.join(item) for item in zip(*iterList)]
    #dispCharChunks = [_bc[box]['vline'] + item + _bc[box]['vline'] for item in boardCharStrChunks]
    dispCharChunks = [bc['vline'] + item + bc['vline'] for item in boardCharStrChunks]
    headerText = _gen_header_footer_line(header, poz='header', dims=dims, box=bc)
    footerText = _gen_header_footer_line(footer, poz='footer', dims=dims, box=bc)
    dispCharChunks = [headerText] + dispCharChunks + [footerText]
    displayText = '\n'.join(dispCharChunks)
    return displayText





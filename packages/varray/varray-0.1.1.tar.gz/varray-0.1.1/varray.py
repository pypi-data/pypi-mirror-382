# BSD 3-Clause License; see https://github.com/aaronm6/varray/blob/main/LICENSE
"""
varray (variable array): A light-weight array type with numpy ndarrays as the backend, 
which supports 2d arrays with rows of variable length.

Why, when awkward (awk) arrays exist?  awk arrays are efficient and versatile and should be
used when one's use case aligns with their capabilities.  However, I found myself avoiding
them in my own work for two reasons:
    1: awk arrays are IMMUTABLE, and hence read-only.  This means they're great to read from,
       but what if you actually want to use them to store data in a script?  For example, 
       you want to fill rows in a loop?  This used to be possible in earlier versions of awk, 
       but has since been removed.  This is my main motivation for creating varray: awk arrays' 
       immutability makes them unusable for the vast majority of my own use cases.
    2: awk is a large package that involves c++ code and all of its plethora of functionality
       might not always be needed.  Hence the desire for a light-weight alternative that
       involves python code only.

The focus here is on efficient and light-weight implementation of limited capabilities, 
rather than a breadth of many capabilities.  For example, numpy arrays and ak arrays support 
efficient slicing, where a slice of an array produces a new "view" to the underlying data, 
but does not copy the data.  So too does varray work with array "views".  Data are only 
copied when required.

In addition to creating a varray with the class constructor, one can create a varray with 
one of the numpy-inspired creation functions: empty, ones, and zeros (and 'empty_like', 
etc.), which allocated the space, and then fill in the values later.

Contents:

varray : variable-array class. See its docstring for instantiation syntax
empty
empty_like
ones
ones_like
zeros
zeros_like
version
version_tuple
"""

import numpy as np
import operator
import re

version = __version__ = '0.1.1'
version_tuple = __version_tuple__ = tuple([int(item) for item in __version__.split('.')])

__all__ = ['varray','empty','empty_like','zeros','zeros_like','ones','ones_like']

_linewidth = np.get_printoptions()['linewidth']

_binops = ('add','and','mul','pow','sub','truediv','floordiv','eq','lt','gt','le','ge','mod','or','xor')
_unops = ('abs','neg','pos')
_rowops_reduce = ('all','any','argmax','argmin','max','mean','min','prod','std','sum','var')
_rowops_accumulate = ('cumprod','cumsum')

_ufindrows = np.frompyfunc(lambda x,y: x-1 if y==0 else y, 2,1)

class varray:
    """
    Create a varray.
    
    Instantiation Parameters
    ------------------------
    nested_array : list of arrays (optional, positional argument)
        A list (or tuple) of lists or arrays, that can be converted into a varray object.
        For example, [[1,2],[3,4,5],[6]] or [array([1,2]), array([3,4,5]), array([6])]
    darray : None or 1d array or list or tuple (optional, keyword argument)
        The array that holds all the data values of the varray.
    sarray : None or 1d array of ints (or list or tuple) (optional, keyword argument)
        The array of row lengths; this would be the second dimension in a regular 2d array
    dtype : data-type (optional, keyword argument)
        The data type of the elements of darray.  Default is np.float64
    empty_cols : str (optional, keyword argument)
        When a column of the jagged 2d array is chosen, not all rows will have enough values
        to fulfill this column index.  For example, va[:,3] calls for the fourth column. But
        not all rows may have four columns.  When this happens, one must decide what to do 
        for those rows which cannot supply the requested column.  Str values 'remove' (default)
        and 'fill' are allowed.
        'remove' : take out those rows, and the resulting array will be shorter than the
                   original number of rows.
        'fill'   : place a 'np.nan' in those entries where a row could not specify the
                  requested column.  THIS CAN BE CHANGED LATER ON WITH THE 'empty_cols' 
                  ATTRIBUTE.
    row_slice : ndarray or slice object (optional, keyword argument)
        Should not be provided by the user; this exists to all non-duplication of the data
        array when slicing a varray object, and is only provided internally by class
        methods.
    csarray : ndarray (optional, keyword argument)
        Should not be provided by the user; same reason as for row_slice

    Class methods and attributes
    ----------------------------
    shape : property (tuple)
        A tuple containing the length of each row
    dtype : property (type)
        The dtype of the data contained in the varray
    nbytes : property (int)
        The number of bytes used by this varray; contains the nbytes of the darray, the sarray
        and a third array called `csarray`.
    empty_cols : property (str)
        Describes what to do when slicing a column and a particular row does not have that
        particular column.  Allowed values: `'remove'` (default) and `'fill'`.  If `'fill'`,
        then the missing entries are filled in with `np.nan`.
    flatten() : method
        Returns the data in a 1d numpy array.
    copy() : method
        Returns a copy of the current varray (using `ndarray.copy` under the hood).
    serialize_as_numpy_arrays(array_name='va') : method
        Serializes the data and shape arrays into a dict object containing two numpy arrays, so
        that they can be saved to disk.
    
    Examples
    --------
    Example 1:
    >>> import varray as va
    >>> nested_list = [[1,2,3],[4,5],[6,7,8,9],[10,11,12]]
    >>> my_varray = va.varray(nested_list)
    >>> my_varray
    varray([[1. 2. 3.],
        [4. 5.],
        [6. 7. 8. 9.],
        [10. 11. 12.]])
    >>> my_varray.shape
    (4, (3, 2, 4, 3))
    
    Example 2:
    >>> my_varray = np.empty((3,2,4,3))
    >>> my_varray[0,:] = np.r_[1,2,3]
    >>> my_varray[1,:] = np.r_[4,5]
    >>> my_varray[2,:] = np.r_[6,7,8,9]
    >>> my_varray[3,:] = np.r_[10,11,12]
    >>> my_varray
    varray([[1. 2. 3.],
            [4. 5.],
            [6. 7. 8. 9.],
            [10. 11. 12.]])
    <slicing, access>
    >>> my_varray[2] #grab the third row
    array([6., 7., 8., 9.])
    >>> my_varray[:,0] # grab the first element from each row
    array([ 1.,  4.,  6., 10.])
    >>> my_varray[:,2] # grab the third element from each row 
    array([ 3.,  8., 12.])
    <rows with less than three elements have been omitted
    >>> my_varray.empty_cols = 'fill'
    >>> my_varray[:,2] # grab the third element from each row 
    array([ 3., nan,  8., 12.])
    <note that the row without 3 elements has been filled with a np.nan>
    
    Example 3:
    >>> flat_data_array = np.r_[1:13]
    >>> flat_shape_array = np.r_[3,2,4,3]
    >>> my_varray = va.varray(darray=flat_data_array, sarray=flat_shape_array)
    
    """
    def __init__(
        self, 
        *args, 
        darray=None, 
        sarray=None, 
        dtype=np.float64, 
        empty_cols='remove',
        row_slice=None,
        csarray=None):
        if empty_cols not in ('remove','fill'):
            raise ValueError("keyword 'empty_cols' must be 'remove' or 'fill'")
        self._empty_cols = empty_cols
        if isinstance(darray, np.ndarray) or darray is None:
            self._darray = darray
        else:
            self._darray = np.array(darray)
        if isinstance(sarray, np.ndarray) or sarray is None:
            self._sarray = sarray
        else:
            self._sarray = np.array(sarray)
        self._dtype = dtype
        if (len(args) > 0) and isinstance(args[0],(list,tuple)):
            self._sarray = np.array([len(item) for item in args[0]])
            self._darray = np.array([item for sublist in args[0] for item in sublist], dtype=dtype)
        if isinstance(self._sarray, np.ndarray):
            if csarray is None:
                self._csarray = (np.r_[0, self._sarray[:-1]]).cumsum()
            elif isinstance(csarray, np.ndarray):
                self._csarray = csarray
            else:
                raise TypeError("csarray must be None or a numpy array")
            if self._darray is None:
                self._darray = np.empty(self._sarray.sum(), dtype=self._dtype)
        else:
            self._csarray = None
        if isinstance(self._darray,np.ndarray) and (dtype != self._darray.dtype):
            self._darray = self._darray.astype(dtype)
        if row_slice is not None:
            if not isinstance(row_slice, (slice, np.ndarray)):
                raise TypeError("row_slice must be None or a slice object")
            self._sarray = self._sarray[row_slice]
            self._csarray = self._csarray[row_slice]
    def __getitem__(self, item):
        if isinstance(item, (int, np.integer)):
            idx_start = self._csarray[item]
            idx_stop = idx_start + self._sarray[item]
            return self._darray[idx_start:idx_stop]
        elif isinstance(item, (slice, np.ndarray)):
            return varray(darray=self._darray, sarray=self._sarray, csarray=self._csarray, row_slice=item)
        elif isinstance(item, tuple):
            if len(item) > 2:
                raise IndexError("No more than two indices can be given")
            if isinstance(item[0],(int,np.integer)):
                return self.__getitem__(item[0])[item[1]]
            if isinstance(item[1],(int,np.integer)):
                cut_rows = self._sarray > item[1]
                if self._empty_cols == 'remove':
                    return self._darray[(self._csarray[cut_rows] + item[1])[item[0]]]
                else:
                    if isinstance(self._dtype(),(int, np.integer)):
                        fill_value = np.iinfo(self._dtype).min
                    elif self._darray.dtype == bool:
                        fill_value = False
                    else:
                        fill_value = np.nan
                    out_ar = np.empty_like(self._sarray, dtype=self.dtype)
                    out_ar[cut_rows] = self._darray[self._csarray[cut_rows] + item[1]]
                    out_ar[~cut_rows] = fill_value
                    return out_ar[item[0]]
            else:
                raise NotImplementedError("This getitem not implemented yet")
        else:
            raise SyntaxError("index or slice not recognized")
        return None
    def __setitem__(self, item, val):
        if isinstance(item, (int, np.integer)):
            self[item][:] = val
        elif isinstance(item, tuple):
            if len(item) < 2:
                raise ValueError("If giving comma-separated values, must give 2")
            if not isinstance(item[0], (int, np.integer)):
                raise ValueError("Must give an integer for the row number")
            self[item[0]][item[1]] = val
    @property
    def shape(self):
        return tuple(self._sarray)
    @property
    def dtype(self):
        return self._dtype
    @property
    def nbytes(self):
        return self._darray.nbytes + self._sarray.nbytes + self._csarray.nbytes
    @property
    def size(self):
        return len(self._darray)
    @property
    def empty_cols(self):
        return self._empty_cols
    @empty_cols.setter
    def empty_cols(self, val):
        if val in ('remove','fill'):
            self._empty_cols = val
        else:
            raise TypeError("Attribute 'empty_cols' must be 'remove' or 'fill'")
    def astype(self, dt):
        return varray(darray=self._darray, sarray=self._sarray, dtype=dt)
    def __len__(self):
        return len(self._sarray)
    def __repr__(self):
        max_lines = 20
        numlines = min(len(self), max_lines)
        outstr = 'varray(['
        pad_space = len(outstr)
        for k in range(numlines):
            pre_space = 0 if k==0 else pad_space
            entry_str = re.sub(r'(?<=\[)\s+','',str(self[k,:]))
            entry_str = re.sub(r'\s+',', ',entry_str)
            if (pad_space + len(entry_str)) > _linewidth:
                line_str = ' '*pre_space + f'{entry_str:0.{_linewidth-pad_space-3}s}' + '...'
            else:
                line_str = ' '*pre_space + f'{entry_str}'
            termstr = '' if k==(len(self)-1) else ',\n'
            line_str += termstr
            outstr += line_str
        if len(self) > max_lines:
            outstr += '...\n'
        else:
            outstr += '])'
        return outstr
    def __str__(self):
        return f"varray with {len(self)} rows"
    def _check_dims(self, other):
        if isinstance(other, varray):
            if len(other) != len(self):
                raise ValueError("Cannot add two varrays unless they have the same shape")
            if not (other._sarray == self._sarray).all():
                raise ValueError("Cannot add two varrays unless they have the same shape")
    def _binary_op(self, other, op_name):
        self._check_dims(other)
        dt = bool if op_name in ('eq','gt','ge','lt','le') else self.dtype
        if isinstance(other, varray):
            other_comp = other._darray
        else:
            other_comp = other
        return varray(darray=getattr(operator,op_name)(self._darray,other_comp),sarray=self._sarray, dtype=dt)
    def _rbinary_op(self, other, op_name):
        self._check_dims(other)
        dt = bool if op_name in ('eq','gt','ge','lt','le') else self.dtype
        return varray(darray=getattr(operator,op_name)(other,self._darray),sarray=self._sarray, dtype=dt)
    def _unary_op(self, op_name):
        dt = self.dtype
        return varray(darray=getattr(operator,op_name)(self._darray), sarray=self._sarray, dtype=dt)
    def _row_op_reduce(self, op_name, axis=None):
        dt = bool if op_name in ('all','any') else self.dtype
        if axis is None:
            return getattr(self._darray, op_name)()
        elif axis==0:
            raise NotImplementedError("No column-wise operations... yet")
        elif axis in (1, -1):
            return np.array([getattr(item, op_name)() for item in self])
        return None
    def _row_op_accumulate(self, op_name, axis=None):
        dt = self.dtype
        if axis is None:
            return getattr(self._darray, op_name)
        elif axis==0:
            raise NotImplementedError("No column-wise operations... yet")
        elif axis in (1, -1):
            new_va = self.__copy__()
            for idx in range(len(self)):
                new_va[idx] = getattr(self[idx], op_name)()
            return new_va
    def flatten(self):
        return self._reduce_array()
    def _reduce_darray(self):
        """
        If a varray was produced by slicing another varray, self._darray will still point
        to the _darray of the parent varray.  This avoids duplication of data, but there
        are times when _darray must be reduced to just the data of the current view.
        This function does that.
        """
        tag_array = np.zeros_like(self._darray, dtype=int)
        tag_array[self._csarray] = self._sarray
        tag_array = _ufindrows.accumulate(tag_array)
        cut_used_rows = tag_array > 0
        return self._darray[cut_used_rows]
    def __copy__(self):
        return varray(darray=self._reduce_darray(), sarray=self._sarray.copy(), dtype=self.dtype)
    def copy(self):
        return self.__copy__()
    def reshape(self, shape):
        """
        Keep the same data but provide a new shape array (i.e. length of each row), the same as
        the sarray keyword at instantiation.  The returned object will be a new view on the 
        same data array, if possible (as is the behavior of numpy's reshape routine).
        """
        if not isinstance(shape, np.ndarray):
            shape = np.array(shape)
        if shape.ndim != 1:
            raise ValueError("Provided shape array must be a 1d numpy array")
        if shape.sum != len(self._darray):
            raise ValueError("The sum of the new shape array must the equal to the length " + \
                "of the existing data array")
        return varray(darray=self._darray, sarray=shape, dtype=self.dtype)
    def serialize_as_numpy_arrays(self, array_name='va'):
        """
        Since varrays are simply wrappers of a pair of numpy arrays, we can just use numpy's savez
        and savez_compressed if we want to save them.  But, like numpy arrays, the array itself
        is just a view to an underlying region of memory.  That view may or may not pull elements
        that are contiguous in memory, and the view may not take all elements of the memory region,
        if e.g. one array is produced by slicing another array.  One therefore needs to produce
        a copy of the array where the data *are* contiguous, so that one is only saving the data
        that one wants.  Here too, we must produce a varray whose underlying data and shape arrays
        are reduced.
        Input:
            array_name : the label that one wants the two arrays to be saved as.  
            
        Output:
            A dict object with two keys: 
                <array_name>_d (1d numpy array containing the varray data)
                <array_name>_s (1d numpy array containing the varray row lengths)
        The dict object can then be given to e.g. np.savez_compressed:
        >>> myvarray = varray(...)
        >>> va_serialized = myvarray.serialize_as_numpy_arrays(array_name='myvarray')
        >>> np.savez_compressed('filename.npz', **va_serialized)
        
        One can save more than one array and more than one varray:
        >>> np.savez_compressed('filename.npz', ndarray_1=ndarray_1, **va1_serialized, **va2_serialized)
        
        To then load these:
        >>> d = np.load('filename.npz')
        >>> myvarray = varray(darray=d['myarray_d'], sarray=d['myarray_s'])
        """
        return {f'{array_name}_d':self._reduce_darray(), f'{array_name}_s':self._sarray.copy()}
    
    def __array__(self, dtype=float, copy=False):
        return self._darray
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method=='__call__':
            return varray(darray=ufunc.__call__(self._darray), sarray=self._sarray)
        else:
            print(f"'{method}' was requested as a method")
            return NotImplemented

# Binary-operation definitions all follow the same framework, so we define these in a loop
for op_name in _binops:
    def method(self, other, op=op_name):
        return self._binary_op(other, op)
    setattr(varray, f'__{op_name}__', method)

# Because binary operations aren't commutative when var types are switched: i.e. __sub__ and __rsub__
# e.g. if va is a varray, va-2 is handled by __sub__ but that won't work for 2-va, for which
# on needs __rsub__
for op_name in _binops:
    def method(self, other, op=op_name):
        return self._rbinary_op(other, op)
    setattr(varray, f'__r{op_name}__', method)

for op_name in _unops:
    def method(self, op=op_name):
        return self._unary_op(op)
    setattr(varray, f'__{op_name}__', method)

# Similar for row-wise operations
for op_name in _rowops_reduce:
    def method(self, op=op_name, axis=None):
        return self._row_op_reduce(op, axis=axis)
    setattr(varray, op_name, method)

for op_name in _rowops_accumulate:
    def method(self, op=op_name, axis=None):
        return self._row_op_accumulate(op, axis=axis)
    setattr(varray, op_name, method)

# varray creation routines, analogous to numpy arrays

def empty(sarray, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.empty
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new empty array of the specified shape and dtype.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if sarray.ndim != 1:
        raise ValueError("Specified shape array (sarray) must be 1d")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.empty(np.array(sarray).sum(), dtype=dtype)
    return varray(darray=darray, sarray=np.array(sarray), dtype=dtype)

def empty_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj
    """
    dt = v_obj.dtype if dtype is None else dtype
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not isinstance(dt, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.empty_like(v_obj._darray, dtype=dt)
    return varray(darray=darray, sarray=v_obj._sarray, dtype=dt)

def ones(sarray, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.ones
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new array of the specified shape and dtype initialized with ones.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if sarray.ndim != 1:
        raise ValueError("Specified shape array (sarray) must be 1d")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.ones(np.array(sarray).sum(), dtype=dtype)
    return varray(darray=darray, sarray=np.array(sarray), dtype=dtype)

def ones_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided initialized
    with numpy.ones
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj initialized with 
        ones.
    """
    dt = v_obj.dtype if dtype is None else dtype
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not isinstance(dt, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.ones_like(v_obj._darray, dtype=dt)
    return varray(darray=darray, sarray=v_obj._sarray, dtype=dt)

def zeros(sarray, dtype=np.float64):
    """
    Create a new varray with the specified shape and dtype.  The data array is
    initialized via numpy.zeros
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new array of the specified shape and dtype initialized with zeros.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if sarray.ndim != 1:
        raise ValueError("Specified shape array (sarray) must be 1d")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.zeros(np.array(sarray).sum(), dtype=dtype)
    return varray(darray=darray, sarray=np.array(sarray), dtype=dtype)

def zeros_like(v_obj, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided initialized
    with numpy.zeros
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj initialized with 
        zeros.
    """
    dt = v_obj.dtype if dtype is None else dtype
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not isinstance(dt, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.zeros_like(v_obj._darray, dtype=dt)
    return varray(darray=darray, sarray=v_obj._sarray, dtype=dt)

def full(sarray, fill_value, dtype=np.float64):
    """
    Create a new varray with the specified shape, fill value and dtype.  The data 
    array is initialized via numpy.full
    
    Parameters
    ----------
    sarray : 1d numpy array of dtype int
        The array of row lengths
    fill_value : scalar
        Fill value
    dtype : data type, optional
        The data type of the data values contained in the varray.
    
    Returns
    -------
    new_varray : varray
        A new array of the specified shape and dtype initialized with the specified
        fill value.
    """
    if not isinstance(sarray, np.ndarray):
        sarray = np.array(sarray)
    if sarray.ndim != 1:
        raise ValueError("Specified shape array (sarray) must be 1d")
    if not np.isscalar(fill_value):
        raise TypeError("fill_value must be a scalar.")
    if not isinstance(dtype, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.full(np.full(np.array(sarray).sum(), fill_value, dtype=dtype))
    return varray(darray=darray, sarray=np.array(sarray), dtype=dtype)

def full_like(v_obj, fill_value, dtype=None):
    """
    Create a new varray with the same shape as the prototype provided initialized
    with a scalar value provided.
    
    Parameters
    ----------
    v_obj : varray
        A prototype varray object.  The new object that is created will have the
        same size and dtype (unless otherwise specified) as v_obj.
    fill_value : scalar
        Fill value
    dtype : data type, optional
    
    Returns
    -------
    new_varray : varray
        A new empty array of the same shape as the provided v_obj initialized with 
        the provided fill value.
    """
    dt = v_obj.dtype if dtype is None else dtype
    if not isinstance(v_obj, varray):
        raise TypeError("Provided object must be a varray")
    if not np.isscalar(fill_value):
        raise TypeError("fill_value must be a scalar.")
    if not isinstance(dt, type):
        raise TypeError("Specified dtype must be a type instance")
    darray = np.full_like(v_obj._darray, fill_value, dtype=dt)
    return varray(darray=darray, sarray=v_obj._sarray, dtype=dt)














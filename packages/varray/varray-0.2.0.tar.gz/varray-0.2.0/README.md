# varray
A 2d numpy-like array that supports variable-length rows

## Installation
```
pip install varray
```
or try
```
pip install git+https://github.com/aaronm6/varray.git
```

## Description
Sometimes one needs to store data in a list of sublists.  If all the sublists are the same size and their contents the same data type, then a 2d numpy array is a very useful and efficient way to store the data; data operations are vectorized and optimized with compiled machine code.  However, if the condition that each sublist contains the same number of elements is not met, numpy is not much help.  

Here, varray (for "variable array") provides a numpy-like array type that supports 2d arrays with variable-length rows.  It is "numpy-like" in that it behaves in much the same way that numpy arrays do, operations are vectorized, slicing produces "views" instead of duplicating data, etc.  Most vectorized operations that work on numpy arrays also seamlessly work on varrays (e.g. `np.exp`, `np.sin`, etc., also binary operations).

**Why reinvent the wheel, when [awkward](https://awkward-array.org/doc/main/) (awk) arrays exist?**  Awk arrays do all this, are efficient and versatile and should be used when one's use case aligns with their capabilities.  However, I found myself avoiding them in my own work for two reasons:

1. awk arrays are IMMUTABLE, and hence read-only.  This means they're great to read from, but what if you actually want to use them to store data in a script?  For example, you cannot allocate the awk-array's memory and then fill rows with a loop.  This used to be possible in earlier versions of awk, but has since been removed.  This is my main motivation for creating varray: awk arrays' immutability makes them unusable for the vast majority of my own use cases.
2. awk is a large package that involves compiled c++ code and its plethora of functionalities might not always be needed.  Hence the desire for a light-weight alternative that is written in pure python.

## Usage
A varray object essentially wraps two numpy arrays: a `darray` ("data array") and an `sarray` ("shape array").  The `darray` stores all the data values in a contiguous 1d array.  The `sarray` is an array of ints which describe the length of each row of the array.  If the varray could be described by the nested list,
```
[[2,2],[3,3,3],[4,4,4,4]]
```
then `darray` would be 
```
[2,2,3,3,3,4,4,4,4]
```
and the `sarray` would be
```
[2,3,4]
```
We can actually create a varray with that nested list:
```python
>>> import varray as va
>>> nested_data = [[2,2], [3,3,3], [4,4,4,4]]
>>> va1 = va.varray(nested_data, dtype=float)
>>> va1
varray([[2., 2.],
        [3., 3., 3.],
        [4., 4., 4., 4.]])
```
We can perform some basic slicing.  For example, picking off the first column (i.e. first element of each row) is the same slicing as in a 2d numpy array:
```python
>>> va1[:,0]
array([2., 3., 4.])
```
Note that the sliced object is a numpy array when possible.  We can pick off the third column in the same way:
```python
>>> va1[:,2]
array([3., 4.])
```
Note that the first row does not have three elements, so it has been omitted from the returned numpy array.  We can change that behavior by changing the `empty_cols` attribute from `remove` to `fill`, and then empty columns will be filled in with `np.nan`:
```python
>>> va1.empty_cols
'remove'
>>> va1.empty_cols = 'fill'
>>> va1[:,2]
array([nan,  3.,  4.])
```

We can sum over rows:
```python
>>> va1.sum(axis=1)
array([ 4., 9., 16.])
```
or also do a cumulative sum:
```python
>>> va1.cumsum(axis=1)
varray([[2., 4.],
        [3., 6., 9.],
        [4., 8., 12., 16.]])
```
These operations (sum, cumsum, and similar) can be performed without specifying the axis; in that case, the operation is performed over the 1d `darray`.  Column-wise operations are not permitted.

We can slice the array, removing the last row
```python
>>> va2 = va1[:-1]
>>> va2
varray([[2., 2.],
        [3., 3., 3.]])
```
and here we can verify that this is a new view to the same data, without duplication of the data:
```python
>>> va2._darray is va1._darray
True
```
(here we have used the `_darray` attribute, which the user should not access).
We can concatenate two or more varrays using `va.vstack`:
```python
>>> va.vstack([va1, va2])
varray([[2., 2.],
        [3., 3., 3.],
        [4., 4., 4., 4.],
        [2., 2.],
        [3., 3., 3.]])
```
We can perform numpy-like operations on a varray, for example powering and raising:
```python
>>> va1**2
varray([[4., 4.],
        [9., 9., 9.],
        [16., 16., 16., 16.]])
>>> 2**va1
varray([[4., 4.],
        [8., 8., 8.],
        [16., 16., 16., 16.]])
```
and exponentiating:
```python
>>> np.exp(va1)
varray([[7.3890561, 7.3890561],
        [20.08553692, 20.08553692, 20.08553692],
        [54.59815003, 54.59815003, 54.59815003, 54.59815003]])
```
Two varrays can be added, subtracted, multiplied, divided, etc., with the behavior intended to be the same as those operations would have on 2d numpy arrays.

**A note about broadcasting**

We are limited in how we can broadcast shapes like in numpy.  In the example above with `va1**2`, we see that the only broadcasting allowed is with a scalar and a varray.  Otherwise, binary operations must be on two varrays with the same shape.

We can create an empty varray and then fill in the rows.  Suppose we have serveral iterations of a process that produces a Poisson-random number of entries, and each entry gets a uniform random number:
```python
>>> import numpy as np
>>> import varray as va
>>> import scipy.stats as st
>>> 
>>> num_iterations = 10
>>> num_entries = st.poisson.rvs(2.3, size=num_iterations)
>>> num_entries
array([2, 3, 2, 3, 4, 1, 3, 0, 1, 3])
>>> entry_times = va.empty(num_entries, dtype=float)
>>> entry_times
varray([[0., 0.],
        [0., 0., 0.],
        [0., 0.],
        [0., 0., 0.],
        [0., 0., 0., 0.],
        [0.],
        [0., 0., 0.],
        [],
        [0.],
        [0., 0., 0.]])
>>> for k in range(num_iterations):
...     entry_times[k,:] = st.uniform.rvs(scale=10., size=num_entries[k])
... 
>>> entry_times
varray([[9.30866133, 0.87799696],
        [1.94942634, 6.75727647, 7.03525249],
        [0.50324541, 6.46413786],
        [8.21324675, 5.11158945, 0.26563948],
        [4.43066161, 2.06960192, 9.81743012, 3.11660339],
        [8.41385994],
        [5.99932338, 8.85480271, 5.06270341],
        [],
        [0.95650628],
        [7.63540707, 8.70081797, 0.15594892]])
```
(side note: as you can see, rows with zero entries are supported)

## Saving to file
Since varrays essentially just wrap two arrays (a `darray` and an `sarray`), one can save these in any way that one prefers, e.g. numpy `npy` or `npz` format, or hdf5 format, etc.  These two arrays are stored as internal variables `_darray` and `_sarray` in the varray object, though I really recommend **against** accessing these attributes directly.  When one creates a varray by slicing another varray, for example, the `darray` of the sliced varray is identical to that of its parent varray.  Likewise with numpy arrays, they are really "views" to an underlying data array, and a sliced array might contain elements that are not complete and/or not contiguous in memory.  So one needs to "serialize" the underlying data before saving, to extract only the information that is needed for that particular object.  varray provides a member function `serialize_as_numpy_arrays` to do this, which returns a `dict` object with two keys: one with key suffix `_d` (for the data array) and another with the key suffix `_s` (for the shape array).  So in the example above, with the varray called `entry_times`, one could serialize the data and save to an `npz` file like so:
```python
>>> entry_times_serialized = entry_times.serialize_as_numpy_arrays(array_name='entry_times')
>>> entry_times_serialized.keys()
dict_keys(['entry_times_d', 'entry_times_s'])
>>> entry_times_serialized
{'entry_times_d': array([9.30866133, 0.87799696, 1.94942634, 6.75727647, 7.03525249,
       0.50324541, 6.46413786, 8.21324675, 5.11158945, 0.26563948,
       4.43066161, 2.06960192, 9.81743012, 3.11660339, 8.41385994,
       5.99932338, 8.85480271, 5.06270341, 0.95650628, 7.63540707,
       8.70081797, 0.15594892]), 'entry_times_s': array([2, 3, 2, 3, 4, 1, 3, 0, 1, 3])}
>>> np.savez_compressed(filename.npz, **entry_times_serialized)
```
To then later load this from file,
```python
>>> import numpy as np, varray as va
>>> with np.load('filename.npz') as f:
...     entry_times = va.varray(darray=f['entry_times_d'], sarray=f['entry_times_s'])
... 
>>> entry_times
varray([[9.30866133, 0.87799696],
        [1.94942634, 6.75727647, 7.03525249],
        [0.50324541, 6.46413786],
        [8.21324675, 5.11158945, 0.26563948],
        [4.43066161, 2.06960192, 9.81743012, 3.11660339],
        [8.41385994],
        [5.99932338, 8.85480271, 5.06270341],
        [],
        [0.95650628],
        [7.63540707, 8.70081797, 0.15594892]])
```



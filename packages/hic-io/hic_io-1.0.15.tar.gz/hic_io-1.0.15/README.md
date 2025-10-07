## Installation

```
pip install hic-io
```

Requires numpy and pybind11.

## Usage

### Read signal

```python
reader = hic_io.Reader(path)
values = reader.read_signal(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` Chromosomes ids, starts and ends of the 2 locations.
- `bin_size` Input bin size or -1 to use the smallest. Must be available in the file. Smallest by default.
- `bin_count` Max output bin count. Takes precedence over `bin_size` if specified by selecting the smallest bin size so that output width and height are not larger that `bin_count`. Not specified by default.
- `full_bin` Extend locations ends to overlapping bins if true. Not by default.
- `def_value` Default value to use when no data overlap a bin. 0 by default.
- `mode` Either "observed" or "oe" (observed/expected). "observed" by default.
- `normalization` Either "none" or any normalization available in the file, such as "kr", "vc" or "vc_sqrt". "none" by default.
- `unit` Either "bp" or "frag". "bp" by default.
- `triangle` Skip symmetrical data if true. Not by default.
- `max_distance` Max contact size in bp to report. All if -1. All by default.

Outputs a numpy float32 array of shape (location 1 span//bin_size, location 2 span//bin_size).

### Read sparse signal

```python
reader = hic_io.Reader(path)
values = reader.read_sparse_signal(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `bin_size` `bin_count` `bin_count` `full_bin` `mode` `normalization` `unit` `triangle` `max_distance` Identical to `read_signal` method.

Returns a COO sparse matrix as a dict with keys:
- `values` Values as a numpy float32 array.
- `row` Values rows indices as a numpy int32 array.
- `col` Values columns indices as a numpy int32 array.
- `shape` Shape of the dense array as a tuple.

Convert in python using `scipy.sparse.csr_array((x["values"], (x["row"], x["col"])), shape=x["shape"])`.

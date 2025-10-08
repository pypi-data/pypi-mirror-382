# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from libc.math cimport isnan
cimport cython
from cpython cimport array
cimport numpy as cnp

cnp.import_array()


cdef int _gt(double x, double y):
    return x > y


cdef int _lt(double x, double y):
    return x < y


@cython.boundscheck(False)
@cython.wraparound(False)
def cython_indices_with_sorted_rows(double[:] x, double[:] y, long[:] rows, int maxy):
    """Cython implementation of the pareto front.

    x, y arguments align with front_indices as in pure python. Same for maxy. However,
    for lack of non-python argsort, we pass in the rows that corresponding to the sorted
    x instead of passing maxx.
    """
    cdef Py_ssize_t size = x.size

    # Use python std array support to store row indices for the pareto front
    cdef array.array result_template = array.array("l", [])

    # Allocate enough space for all rows, if necessary
    cdef array.array result = array.clone(result_template, size, zero=False)
    # View but idk if we need this?
    cdef long[:] result_view = result

    # Row for the start of the pareto front
    cdef int current = 0
    cdef long temp_row
    cdef Py_ssize_t i

    for i in range(size):
        temp_row = rows[i]
        if not (isnan(x[temp_row]) or isnan(y[temp_row])):
            # First real valued entry along the pareto front
            result_view[0] = temp_row
            current = i
            break
    else:
        array.resize(result, 0)
        return result

    # Head points to the next index to add data
    cdef int head = 1
    cdef double current_y = y[rows[current]]
    cdef double current_x = x[rows[current]]
    cdef double new_y, new_x

    check_dominated = _gt if maxy else _lt

    for i in range(current + 1, size):
        temp_row = rows[i]
        new_y = y[temp_row]
        new_x = x[temp_row]
        if isnan(new_x) or isnan(new_y):
            continue
        if check_dominated(new_y, current_y):
            if new_x == current_x:
                head = head - 1
            result_view[head] = temp_row
            current_x = new_x
            current_y = new_y
            head = head + 1

    # Trim off space for rows we don't need along the pareto front
    cdef long tail = min(head, size)
    array.resize(result, tail)
    return result

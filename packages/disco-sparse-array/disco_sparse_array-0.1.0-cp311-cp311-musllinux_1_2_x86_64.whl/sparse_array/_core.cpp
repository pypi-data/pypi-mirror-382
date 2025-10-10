#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// Helpers: compare (row, col) pairs that are lexicographically sorted
static inline bool lt_pair(unsigned int r1, unsigned int c1,
                           unsigned int r2, unsigned int c2) {
    return (r1 < r2) || (r1 == r2 && c1 < c2);
}

// _add_inplace: add values_b into values_a where indices match
void _add_inplace(py::array_t<unsigned int, py::array::c_style | py::array::forcecast> indices_a,
                    py::array_t<double,        py::array::c_style | py::array::forcecast> values_a,
                    py::array_t<unsigned int,  py::array::c_style | py::array::forcecast> indices_b,
                    py::array_t<double,        py::array::c_style | py::array::forcecast> values_b) {
    auto ia = indices_a.unchecked<1>();
    auto va = values_a.mutable_unchecked<1>();
    auto ib = indices_b.unchecked<1>();
    auto vb = values_b.unchecked<1>();

    const py::ssize_t na = ia.shape(0);
    const py::ssize_t nb = ib.shape(0);

    py::gil_scoped_release release;

    py::ssize_t j = 0;
    for (py::ssize_t i = 0; i < na; ++i) {
        while (j < nb && ib(j) < ia(i)) ++j;              // advance b
        if (j < nb && ib(j) == ia(i)) va(i) += vb(j++);
    }
    if (j != nb) throw std::runtime_error(
        "Indices of b are not strictly increasing or not a subset of a.");
}

// _add_inplace_2d: same but for (row, col)
void _add_inplace_2d(py::array_t<unsigned int> rows_a,
                       py::array_t<unsigned int> cols_a,
                       py::array_t<double>       vals_a,
                       py::array_t<unsigned int> rows_b,
                       py::array_t<unsigned int> cols_b,
                       py::array_t<double>       vals_b) {
    auto ra = rows_a.unchecked<1>();
    auto ca = cols_a.unchecked<1>();
    auto va = vals_a.mutable_unchecked<1>();
    auto rb = rows_b.unchecked<1>();
    auto cb = cols_b.unchecked<1>();
    auto vb = vals_b.unchecked<1>();

    const py::ssize_t na = ra.shape(0);
    const py::ssize_t nb = rb.shape(0);

    py::gil_scoped_release release;

    py::ssize_t j = 0;
    for (py::ssize_t i = 0; i < na; ++i) {
        while (j < nb && lt_pair(rb(j), cb(j), ra(i), ca(i))) ++j;
        if (j < nb && rb(j) == ra(i) && cb(j) == ca(i)) va(i) += vb(j++);
    }
    if (j != nb) throw std::runtime_error(
        "Indices (row,col) of b not strictly increasing or not subset of a.");
}

// _intersect_indices: union-like merge, optionally strict for 'self' emission
py::ssize_t _intersect_indices(py::array_t<unsigned int> result_indices,
                                 py::array_t<double>       result_values,
                                 py::array_t<unsigned int> self_indices,
                                 py::array_t<double>       self_values,
                                 py::array_t<unsigned int> other_indices,
                                 bool strict) {
    auto ri = result_indices.mutable_unchecked<1>();
    auto rv = result_values.mutable_unchecked<1>();
    auto si = self_indices.unchecked<1>();
    auto sv = self_values.unchecked<1>();
    auto oi = other_indices.unchecked<1>();

    const py::ssize_t m = si.shape(0);
    const py::ssize_t n = oi.shape(0);

    py::gil_scoped_release release;

    py::ssize_t i = 0, j = 0, k = 0;
    for (; i < m; ++i) {
        while (j < n && oi(j) < si(i)) { ri(k) = oi(j); rv(k) = 0.0; ++j; ++k; }
        if (!strict || (j < n && oi(j) == si(i))) { ri(k) = si(i); rv(k) = sv(i); ++k; }
        if (j < n && oi(j) == si(i)) ++j;
    }
    while (j < n) { ri(k) = oi(j); rv(k) = 0.0; ++j; ++k; }
    return k;
}

// _intersect_indices_2d: same idea for (row,col)
py::ssize_t _intersect_indices_2d(py::array_t<unsigned int> result_rows,
                                    py::array_t<unsigned int> result_cols,
                                    py::array_t<double>       result_values,
                                    py::array_t<unsigned int> self_rows,
                                    py::array_t<unsigned int> self_cols,
                                    py::array_t<double>       self_values,
                                    py::array_t<unsigned int> other_rows,
                                    py::array_t<unsigned int> other_cols,
                                    bool strict) {
    auto rr = result_rows.mutable_unchecked<1>();
    auto rc = result_cols.mutable_unchecked<1>();
    auto rv = result_values.mutable_unchecked<1>();
    auto sr = self_rows.unchecked<1>();
    auto sc = self_cols.unchecked<1>();
    auto sv = self_values.unchecked<1>();
    auto orr = other_rows.unchecked<1>();
    auto oc = other_cols.unchecked<1>();

    const py::ssize_t m = sr.shape(0);
    const py::ssize_t n = orr.shape(0);

    py::gil_scoped_release release;

    py::ssize_t i = 0, j = 0, k = 0;
    for (; i < m; ++i) {
        while (j < n && lt_pair(orr(j), oc(j), sr(i), sc(i))) {
            rr(k) = orr(j); rc(k) = oc(j); rv(k) = 0.0; ++j; ++k;
        }
        bool match = (j < n && orr(j) == sr(i) && oc(j) == sc(i));
        if (!strict || match) { rr(k) = sr(i); rc(k) = sc(i); rv(k) = sv(i); ++k; }
        if (match) ++j;
    }
    while (j < n) { rr(k) = orr(j); rc(k) = oc(j); rv(k) = 0.0; ++j; ++k; }
    return k;
}

// result_indices must be sorted ascending (columns to accumulate into).
// m_rows must be non-decreasing; within each row, m_cols strictly increasing.
// v_indices must be strictly increasing (rows present in v).
py::ssize_t _dotproduct_vm(py::array_t<unsigned int> result_indices,
                             py::array_t<double>       result_values,
                             py::array_t<unsigned int> v_indices,
                             py::array_t<double>       v_values,
                             py::array_t<unsigned int> m_rows,
                             py::array_t<unsigned int> m_cols,
                             py::array_t<double>       m_vals) {
    auto ri = result_indices.unchecked<1>();
    auto rv = result_values.mutable_unchecked<1>();
    auto vi = v_indices.unchecked<1>();
    auto vv = v_values.unchecked<1>();
    auto mr = m_rows.unchecked<1>();
    auto mc = m_cols.unchecked<1>();
    auto mv = m_vals.unchecked<1>();

    const py::ssize_t R = ri.shape(0);
    const py::ssize_t V = vi.shape(0);
    const py::ssize_t M = mr.shape(0);

    // Zero the output first.
    for (py::ssize_t t = 0; t < R; ++t) rv(t) = 0.0;

    py::ssize_t i = 0; // indexes result
    py::ssize_t j = 0; // indexes v

    py::gil_scoped_release release;

    for (py::ssize_t k = 0; k < M; ++k) {
        // --- reset result pointer for next row & enforce order constraints ---
        if (k != 0) {
            if (mr(k) > mr(k - 1)) {
                if (mc(k) < mc(k - 1)) {
                    i = 0; // new row where columns started lower than previous row -> reset i
                }
            } else if (mr(k) == mr(k - 1) && mc(k) <= mc(k - 1)) {
                throw py::value_error("Column of m must be strictly increasing for same row.");
            } else if (mr(k) < mr(k - 1)) {
                throw py::value_error("Rows of m must be increasing.");
            }
        }

        // --- progress pointer in v (to row >= current matrix row) ---
        while (j < V - 1 && vi(j) < mr(k)) {
            ++j;
            if (vi(j) <= vi(j - 1)) {
                throw py::value_error("Indices of v must be strictly increasing.");
            }
        }
        if (j >= V) {
            throw py::value_error("Pointer j of v exceeded size of v.");
        }

        if (vi(j) == mr(k)) {
            // --- progress pointer in result until reaching current matrix column ---
            // (Assumes result_indices sorted ascending; may run i forward across rows,
            // but we reset i when a new row's columns "wrap".)
            while (ri(i) < mc(k)) {
                ++i;
                if (i >= R) {
                    throw py::value_error("Pointer i of result exceeded size of result_indices.");
                }
            }
            // accumulate
            rv(i) += vv(j) * mv(k);
        }
    }

    return R;
}

// - other_indices must be a subset of self_indices
// - both index arrays strictly increasing (checked as we advance)
// - emit entries where |other_values[j] - self_values[i]| > precision
// - optionally update self_values[i] = other_values[j]
// - return k (number of emitted changes)
py::ssize_t _changes(py::array_t<unsigned int> result_indices,
                       py::array_t<double>       result_values,
                       py::array_t<unsigned int> self_indices,
                       py::array_t<double>       self_values,
                       py::array_t<unsigned int> other_indices,
                       py::array_t<double>       other_values,
                       bool update = false,
                       double precision = 1e-6) {
    auto ri = result_indices.mutable_unchecked<1>();
    auto rv = result_values.mutable_unchecked<1>();
    auto si = self_indices.unchecked<1>();
    auto sv = self_values.mutable_unchecked<1>();
    auto oi = other_indices.unchecked<1>();
    auto ov = other_values.unchecked<1>();

    const py::ssize_t m = si.shape(0);  // self size (indexed by i)
    const py::ssize_t n = oi.shape(0);  // other size (indexed by j)

    if (m == 0 || n == 0) return 0;

    py::ssize_t i = 0;
    py::ssize_t k = 0;

    py::gil_scoped_release release;

    for (py::ssize_t j = 0; j < n; ++j) {
        // other strictly increasing?
        if (j != 0 && oi(j) <= oi(j - 1)) {
            throw py::value_error("Indices of other are not strictly increasing.");
        }

        // advance i while self[i] < other[j], but leave room (i < m-1)
        while (i < m - 1 && si(i) < oi(j)) {
            ++i;
            // self strictly increasing?
            if (si(i) <= si(i - 1)) {
                throw py::value_error("Indices of self are not strictly increasing.");
            }
        }

        // enforce subset: current other[j] must equal some self[i]
        if (si(i) != oi(j)) {
            throw py::value_error("Indices of other must be subset of self.");
        } else {
            const double diff = ov(j) - sv(i);
            if (diff > precision || diff < -precision) {
                ri(k) = si(i);
                rv(k) = ov(j);         // store other value (not the diff)
                if (update) sv(i) = ov(j);
                ++k;
            }
        }
    }

    return k;
}


// to_dense (vector): result[indices[k]] = values[k]
void _to_dense_vector(py::array_t<double>       result_values,
                        py::array_t<unsigned int> indices,
                        py::array_t<double>       values) {
    auto rv = result_values.mutable_unchecked<1>();
    auto ix = indices.unchecked<1>();
    auto vv = values.unchecked<1>();
    const py::ssize_t n = ix.shape(0);
    py::gil_scoped_release release;
    for (py::ssize_t k = 0; k < n; ++k) rv(ix(k)) = vv(k);
}

// to_dense (matrix): result[rows[r], cols[r]] = values[r]
void _to_dense_matrix(py::array_t<double>       result_values, // 2D
                        py::array_t<unsigned int> rows,
                        py::array_t<unsigned int> cols,
                        py::array_t<double>       values) {
    auto rv = result_values.mutable_unchecked<2>();
    auto r  = rows.unchecked<1>();
    auto c  = cols.unchecked<1>();
    auto v  = values.unchecked<1>();
    const py::ssize_t n = r.shape(0);
    py::gil_scoped_release release;
    for (py::ssize_t k = 0; k < n; ++k) rv(r(k), c(k)) = v(k);
}

// isin: result[i] = indices[i] in test_indices
void _isin(py::array_t<uint8_t>        result,
             py::array_t<unsigned int>   indices,
             py::array_t<unsigned int>   test_indices) {
    auto out  = result.mutable_unchecked<1>();
    auto ix   = indices.unchecked<1>();
    auto test = test_indices.unchecked<1>();
    const py::ssize_t n = test.shape(0);
    py::ssize_t j = 0;
    py::gil_scoped_release release;

    for (py::ssize_t i = 0; i < ix.shape(0); ++i) {
        while (j < n && test(j) < ix(i)) ++j;
        out(i) = (j < n && test(j) == ix(i)) ? 1 : 0;
    }
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 port of sparse compute kernels";

    m.def("_add_inplace", &_add_inplace,
          py::arg("indices_a"), py::arg("values_a"),
          py::arg("indices_b"), py::arg("values_b"));

    m.def("_add_inplace_2d", &_add_inplace_2d,
          py::arg("rows_a"), py::arg("cols_a"), py::arg("vals_a"),
          py::arg("rows_b"), py::arg("cols_b"), py::arg("vals_b"));

    m.def("_intersect_indices", &_intersect_indices,
          py::arg("result_indices"),
          py::arg("result_values"),
          py::arg("self_indices"),
          py::arg("self_values"),
          py::arg("other_indices"),
          py::arg("strict") = false);   // <-- named + default

    m.def("_intersect_indices_2d", &_intersect_indices_2d,
          py::arg("result_rows"),
          py::arg("result_cols"),
          py::arg("result_values"),
          py::arg("self_rows"),
          py::arg("self_cols"),
          py::arg("self_values"),
          py::arg("other_rows"),
          py::arg("other_cols"),
          py::arg("strict") = false);   // <-- named + default

    m.def("_dotproduct_vm", &_dotproduct_vm,
          py::arg("result_indices"), py::arg("result_values"),
          py::arg("v_indices"), py::arg("v_values"),
          py::arg("m_rows"), py::arg("m_cols"), py::arg("m_vals"));

    m.def("_changes", &_changes,
          py::arg("result_indices"), py::arg("result_values"),
          py::arg("self_indices"), py::arg("self_values"),
          py::arg("other_indices"), py::arg("other_values"),
          py::arg("update") = false, py::arg("precision") = 1e-6);

    m.def("_to_dense_vector", &_to_dense_vector,
          py::arg("result_values"), py::arg("indices"), py::arg("values"));

    m.def("_to_dense_matrix", &_to_dense_matrix,
          py::arg("result_values"), py::arg("rows"), py::arg("cols"), py::arg("values"));

    m.def("_isin", &_isin,
          py::arg("result"), py::arg("indices"), py::arg("test_indices"));
}

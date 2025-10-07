#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <cctype>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "reading/straw.cpp"

namespace py = pybind11;


struct Loc {
    std::string chr_id;
    int64_t start;
    int64_t end;
    int64_t binned_start;
    int64_t binned_end;
};

std::string lowercase(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), ::tolower);
    return value;
}

std::string uppercase(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), ::toupper);
    return value;
}


class PyReader {
    std::unique_ptr<HiCFile> hic_file;

public:
    std::vector<int32_t> bin_sizes;
    std::unordered_map<std::string, chromosome> chr_map;
    py::dict chr_sizes;

    PyReader(const std::string &path) {
        hic_file = std::make_unique<HiCFile>(path);

        bin_sizes = hic_file->getResolutions();
        std::sort(bin_sizes.begin(), bin_sizes.end());

        for (const auto &chr_entry : hic_file->getChromosomes()) {
            chr_map[chr_entry.name] = chr_entry;
            if (chr_entry.name == "All") continue;
            chr_sizes[py::str(chr_entry.name)] = chr_entry.length;
        }
    }

    chromosome parse_chr(const std::string &chr_id) {
        std::string chr_key = chr_id;
        auto it = chr_map.find(chr_key);
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(lowercase(chr_key));
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(uppercase(chr_key));
        if (it != chr_map.end()) return it->second;
        if (lowercase(chr_id.substr(0, 3)) == "chr") {
            chr_key = chr_id.substr(3);
        } else {
            chr_key = ("chr" + chr_id);
        }
        it = chr_map.find(chr_key);
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(lowercase(chr_key));
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(uppercase(chr_key));
        if (it != chr_map.end()) return it->second;
        std::string available;
        for (const auto& entry : chr_map) {
            if (!available.empty()) available += ", ";
            available += entry.first;
        }
        throw std::runtime_error("chr" + chr_key + " not in hic (" + available + ")");
    }

    std::string py_parse_chr(const std::string &chr_id) {
        return parse_chr(chr_id).name;
    }

    Loc parse_loc(
        const std::string &chr_id,
        int64_t start,
        int64_t end,
        int32_t bin_size,
        bool full_bin = false
    ) {
        Loc loc;
        loc.chr_id = parse_chr(chr_id).name;
        if (start > end) {
            throw std::runtime_error("loc " + chr_id + ":" + std::to_string(start) + "-" + std::to_string(end) + " invalid");
        }
        loc.start = start;
        loc.end = end;
        if (full_bin) {
            loc.binned_start = start >= 0
                ? (start / bin_size) * bin_size
                : -(((-start + bin_size - 1) / bin_size) * bin_size);
            loc.binned_end = end >= 0
                ? ((end + bin_size - 1) / bin_size) * bin_size
                : -((-end / bin_size) * bin_size);
        } else {
            loc.binned_start = (start / bin_size) * bin_size;
            loc.binned_end = (end / bin_size) * bin_size;
        }
        return loc;
    }

    py::dict py_parse_loc(
        const std::string &chr_id,
        int64_t start,
        int64_t end,
        int32_t bin_size,
        bool full_bin = false
    ) {
        Loc loc = parse_loc(chr_id, start, end, bin_size, full_bin);
        py::dict result;
        result["chr_id"] = loc.chr_id;
        result["start"] = loc.start;
        result["end"] = loc.end;
        result["binned_start"] = loc.binned_start;
        result["binned_end"] = loc.binned_end;
        return result;
    }

    int32_t select_bin_size(int32_t bin_size = -1, int64_t bin_count = -1, int64_t span = -1) {
        if (bin_count < 0) {
            if (bin_size < 0) return bin_sizes.front();
            if (std::find(bin_sizes.begin(), bin_sizes.end(), bin_size) == bin_sizes.end()) {
                std::string available;
                for (const auto &size : bin_sizes) {
                    if (!available.empty()) available += ", ";
                    available += std::to_string(size);
                }
                throw std::runtime_error("bin_size " + std::to_string(bin_size) + " not available (" + available + ")");
            }
            return bin_size;
        }
        // select smallest bin_size so that resulting bin count is less than bin_count
        if (span < 0) throw std::runtime_error("span must be provided if bin_count is provided");
        for (const auto &size : bin_sizes) {
            if (size < bin_size) continue;
            int64_t count = (span + size - 1) / size;
            if (count < bin_count) return size;
        }
        return bin_sizes.back();
    }

    py::array_t<float> read_signal(
        const std::vector<std::string> &chr_ids,
        const std::vector<int64_t> &starts,
        const std::vector<int64_t> &ends,
        int32_t bin_size = -1,
        int64_t bin_count = -1,
        bool full_bin = false,
        float def_value = 0.0f,
        std::string mode = "observed",
        std::string normalization = "none",
        std::string unit = "bp",
        bool triangle = false,
        int64_t max_distance = -1
    ) {
        
        if (chr_ids.size() != 2 || starts.size() != 2 || ends.size() != 2) {
            throw std::runtime_error("chr_ids, starts and ends must each have 2 elements");
        }
        int64_t max_span = std::max(ends[0] - starts[0], ends[1] - starts[1]);
        bin_size = select_bin_size(bin_size, bin_count, max_span);
        auto loc_1 = parse_loc(chr_ids[0], starts[0], ends[0], bin_size, full_bin);
        auto loc_2 = parse_loc(chr_ids[1], starts[1], ends[1], bin_size, full_bin);

        std::transform(mode.begin(), mode.end(), mode.begin(), ::tolower);
        std::transform(normalization.begin(), normalization.end(), normalization.begin(), ::toupper);
        std::transform(unit.begin(), unit.end(), unit.begin(), ::toupper);

        auto mzd = hic_file->getMatrixZoomData(loc_1.chr_id, loc_2.chr_id, mode, normalization, unit, bin_size);
        auto data = mzd->getRecordsAsMatrix(loc_1.binned_start, loc_1.binned_end, loc_2.binned_start, loc_2.binned_end, def_value, triangle, max_distance);

        size_t row_count = (loc_1.binned_end - loc_1.binned_start) / bin_size;
        size_t col_count = (loc_2.binned_end - loc_2.binned_start) / bin_size;
        std::vector<size_t> shape = {row_count, col_count};
        std::vector<size_t> strides = {col_count * sizeof(float), sizeof(float)};
        return py::array_t<float>(shape, strides, data.data());

    }

    py::dict read_sparse_signal(
        const std::vector<std::string> &chr_ids,
        const std::vector<int64_t> &starts,
        const std::vector<int64_t> &ends,
        int32_t bin_size = -1,
        int64_t bin_count = -1,
        bool full_bin = false,
        std::string mode = "observed",
        std::string normalization = "none",
        std::string unit = "bp",
        bool triangle = false,
        int64_t max_distance = -1
    ) {
        
        if (chr_ids.size() != 2 || starts.size() != 2 || ends.size() != 2) {
            throw std::runtime_error("chr_ids, starts and ends must each have 2 elements");
        }
        int64_t max_span = std::max(ends[0] - starts[0], ends[1] - starts[1]);
        bin_size = select_bin_size(bin_size, bin_count, max_span);
        auto loc_1 = parse_loc(chr_ids[0], starts[0], ends[0], bin_size, full_bin);
        auto loc_2 = parse_loc(chr_ids[1], starts[1], ends[1], bin_size, full_bin);

        std::transform(mode.begin(), mode.end(), mode.begin(), ::tolower);
        std::transform(normalization.begin(), normalization.end(), normalization.begin(), ::toupper);
        std::transform(unit.begin(), unit.end(), unit.begin(), ::toupper);

        auto mzd = hic_file->getMatrixZoomData(loc_1.chr_id, loc_2.chr_id, mode, normalization, unit, bin_size);
        auto data = mzd->getRecordsAsSparseMatrix(loc_1.binned_start, loc_1.binned_end, loc_2.binned_start, loc_2.binned_end, triangle, max_distance);

        py::dict result;
        result["values"] = py::array_t<float>(data.values.size(), data.values.data());
        result["row"] = py::array_t<int32_t>(data.row.size(), data.row.data());
        result["col"] = py::array_t<int32_t>(data.col.size(), data.col.data());
        result["shape"] = py::make_tuple(std::get<0>(data.shape), std::get<1>(data.shape));
        return result;

    }

};


std::vector<py::array_t<int32_t>> compress_sparse_by_color(const std::vector<float> &values, const std::vector<int32_t> &row, const std::vector<int32_t> &col, int32_t color_count) {
    float min_value = 0.0f;
    float max_value = *std::max_element(values.begin(), values.end());

    std::vector<std::vector<int32_t>> result(color_count);
    for (uint64_t i = 0; i < values.size(); i++) {
        float value = (values[i] - min_value) / (max_value - min_value);
        if (std::isnan(value) || std::isinf(value)) continue;
        int32_t value_bin = static_cast<int32_t>(std::floor(value * (color_count - 1)));
        int32_t row_index = row[i];
        int32_t col_index = col[i];
        auto &result_bin = result[value_bin];
        if (!result_bin.empty()) {
            if (result_bin[result_bin.size() - 3] == row_index
            && result_bin[result_bin.size() - 2] + result_bin[result_bin.size() - 1] == col_index) {
                result_bin[result_bin.size() - 1] = result_bin[result_bin.size() - 1] + 1;
                continue;
            }
        }
        result_bin.insert(result_bin.end(), {row_index, col_index, 1});
    }

    std::vector<py::array_t<int32_t>> py_result(color_count);
    for (int32_t i = 0; i < color_count; i++) {
        std::vector<size_t> shape = {result[i].size() / 3, 3};
        std::vector<size_t> strides = {3 * sizeof(int32_t), sizeof(int32_t)};
        py_result[i] = py::array_t<int32_t>(shape, strides, result[i].data());
    }
    return py_result;
}





PYBIND11_MODULE(hic_io, m, py::mod_gil_not_used()) {
    m.doc() = "Process HiC files";

    py::class_<PyReader>(m, "Reader", py::module_local())
        .def(py::init<const std::string&>(), "Reader for HiC files",
            py::arg("path"))
        .def_readonly("bin_sizes", &PyReader::bin_sizes)
        .def_readonly("chr_sizes", &PyReader::chr_sizes)
        .def("select_bin_size", &PyReader::select_bin_size,
            "Select bin size",
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("span") = -1
        )
        .def("parse_chr", &PyReader::py_parse_chr,
            "Parse chromosome ID",
            py::arg("chr_id"))
        .def("parse_loc", &PyReader::py_parse_loc,
            "Parse location",
            py::arg("chr_id"),
            py::arg("start"),
            py::arg("end"),
            py::arg("bin_size"),
            py::arg("full_bin") = false
        )
        .def("read_signal", &PyReader::read_signal,
            "Read signal",
            py::arg("chr_ids"),
            py::arg("starts"),
            py::arg("ends"),
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f,
            py::arg("mode") = "observed",
            py::arg("normalization") = "none",
            py::arg("unit") = "bp",
            py::arg("triangle") = false,
            py::arg("max_distance") = -1
        )
        .def("read_sparse_signal", &PyReader::read_sparse_signal,
            "Read sparse signal",
            py::arg("chr_ids"),
            py::arg("starts"),
            py::arg("ends"),
            py::arg("bin_size") = -1,
            py::arg("bin_count") = -1,
            py::arg("full_bin") = false,
            py::arg("mode") = "observed",
            py::arg("normalization") = "none",
            py::arg("unit") = "bp",
            py::arg("triangle") = false,
            py::arg("max_distance") = -1
        );

    
    m.def("compress_sparse_by_color", &compress_sparse_by_color,
        "Compress sparse matrix by color",
        py::arg("values"),
        py::arg("row"),
        py::arg("col"),
        py::arg("color_count")
    );

}

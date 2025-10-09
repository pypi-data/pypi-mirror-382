#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "main.cpp"

namespace py = pybind11;


py::dict py_get_chr_sizes(const std::string& genome) {
    return py::cast(get_chr_sizes(genome));
}


std::function<void(uint64_t, uint64_t)> init_progress_callback(py::object progress) {
    if (progress.is_none()) return nullptr;
    return [progress](uint64_t current, uint64_t total) {
        progress(current, total);
    };
}

class PyReader {
    std::unique_ptr<Reader> reader;

public:
    py::dict main_header;
    py::list zoom_headers;
    py::dict auto_sql;
    py::dict total_summary;
    py::dict chr_tree_header;
    py::dict chr_sizes;
    py::str type;
    py::int_ data_count;
    
    PyReader(
        const std::string& path,
        uint64_t parallel = 24,
        float zoom_correction = 0.33
    ) {
        reader = std::make_unique<Reader>(path, parallel, zoom_correction);
        auto headers_future = reader->read_headers();
        headers_future.get();

        main_header["magic"] = reader->main_header.magic;
        main_header["version"] = reader->main_header.version;
        main_header["zoom_levels"] = reader->main_header.zoom_levels;
        main_header["chr_tree_offset"] = reader->main_header.chr_tree_offset;
        main_header["full_data_offset"] = reader->main_header.full_data_offset;
        main_header["full_index_offset"] = reader->main_header.full_index_offset;
        main_header["field_count"] = reader->main_header.field_count;
        main_header["defined_field_count"] = reader->main_header.defined_field_count;
        main_header["auto_sql_offset"] = reader->main_header.auto_sql_offset;
        main_header["total_summary_offset"] = reader->main_header.total_summary_offset;
        main_header["uncompress_buffer_size"] = reader->main_header.uncompress_buffer_size;
        main_header["reserved"] = reader->main_header.reserved;

        for (const auto& field : reader->auto_sql) {
            auto_sql[py::str(field.first)] = field.second;
        }

        total_summary["bases_covered"] = reader->total_summary.bases_covered;
        total_summary["min_value"] = reader->total_summary.min_value;
        total_summary["max_value"] = reader->total_summary.max_value;
        total_summary["sum_data"] = reader->total_summary.sum_data;
        total_summary["sum_squared"] = reader->total_summary.sum_squared;

        chr_tree_header["magic"] = reader->chr_tree_header.magic;
        chr_tree_header["block_size"] = reader->chr_tree_header.block_size;
        chr_tree_header["key_size"] = reader->chr_tree_header.key_size;
        chr_tree_header["value_size"] = reader->chr_tree_header.value_size;
        chr_tree_header["item_count"] = reader->chr_tree_header.item_count;
        chr_tree_header["reserved"] = reader->chr_tree_header.reserved;

        for (const auto& zoom_header : reader->zoom_headers) {
            py::dict zoom_header_dict;
            zoom_header_dict["reduction_level"] = zoom_header.reduction_level;
            zoom_header_dict["reserved"] = zoom_header.reserved;
            zoom_header_dict["data_offset"] = zoom_header.data_offset;
            zoom_header_dict["index_offset"] = zoom_header.index_offset;
            zoom_headers.append(zoom_header_dict);
        }
        
        for (const auto& chr : reader->chr_map) {
            chr_sizes[py::str(chr.first)] = chr.second.chr_size;
        }
    }
    
    py::array_t<float> read_signal(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t bin_size = 1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        int32_t zoom = 0,
        py::object progress = py::none()) {

        auto progress_callback = init_progress_callback(progress);
        auto values = reader->read_signal(
            chr_ids, starts, span, bin_size, bin_mode, full_bin, def_value, zoom, progress_callback
        );

        size_t row_count = chr_ids.size();
        size_t col_count = values.size() / row_count;
        std::vector<size_t> shape = {row_count, col_count};
        std::vector<size_t> strides = {col_count * sizeof(float), sizeof(float)};
        return py::array_t<float>(shape, strides, values.data());
    }

    py::array_t<float> quantify(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        const std::vector<int64_t>& ends = {},
        uint32_t span = 1,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = 0,
        py::object progress = py::none()) {

        auto progress_callback = init_progress_callback(progress);
        auto values = reader->quantify(
            chr_ids, starts, ends, span, def_value, reduce, zoom, progress_callback
        );
        
        std::vector<size_t> shape = {values.size()};
        std::vector<size_t> strides = {sizeof(float)};
        return py::array_t<float>(shape, strides, values.data());
    }

    py::array_t<float> profile(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t bin_size = 1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = 0,
        py::object progress = py::none()) {

        auto progress_callback = init_progress_callback(progress);
        auto values = reader->profile(
            chr_ids, starts, span, bin_size, bin_mode, full_bin, def_value, reduce, zoom, progress_callback
        );
        
        std::vector<size_t> shape = {values.size()};
        std::vector<size_t> strides = {sizeof(float)};
        return py::array_t<float>(shape, strides, values.data());
    }

    py::list read_entries(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        const std::vector<int64_t>& ends = {},
        uint32_t span = 1,
        py::object progress = py::none()) {

        std::function<void(uint64_t, uint64_t)> progress_callback = nullptr;
        if (!progress.is_none()) {
            progress_callback = [progress](uint64_t current, uint64_t total) {
                progress(current, total);
            };
        }

        auto locs_entries = reader->read_entries(
            chr_ids, starts, ends, span, progress_callback
        );

        py::list py_locs_entries;
        for (const auto& entries : locs_entries) {
            py::list py_entries;
            for (const auto& entry : entries) {
                py::dict py_entry;
                py_entry["chr"] = reader->chr_tree[entry.chr_index].key;
                py_entry["start"] = entry.start;
                py_entry["end"] = entry.end;
                for (const auto& field : entry.fields) {
                    py_entry[py::str(field.first)] = field.second;
                }
                py_entries.append(py_entry);
            }
            py_locs_entries.append(py_entries);
        }
        return py_locs_entries;
    }

    void to_bedgraph(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom = -1,
        py::object progress = py::none()
    ) {
        auto progress_callback = init_progress_callback(progress);
        reader->to_bedgraph(output_path, chr_ids, zoom, progress_callback);
    }
    
    void to_wig(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom = -1,
        py::object progress = py::none()
    ) {
        auto progress_callback = init_progress_callback(progress);
        reader->to_wig(output_path, chr_ids, zoom, progress_callback);
    }

    void to_bed(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        uint64_t col_count = 0,
        py::object progress = py::none()
    ) {
        auto progress_callback = init_progress_callback(progress);
        reader->to_bed(output_path, chr_ids, col_count, progress_callback);
    }

};


PYBIND11_MODULE(bigwig_io, m, py::mod_gil_not_used()) {
    m.doc() = "Process bigWig and bigBed files";

    m.def("get_chr_sizes", &py_get_chr_sizes, "Get chromosome sizes for a given genome",
        py::arg("genome"));

    py::class_<PyReader>(m, "Reader", py::module_local())
        .def(py::init<const std::string&, uint64_t>(), "Reader for bigWig and bigBed files",
            py::arg("path"), py::arg("parallel") = 24)
        .def_readonly("main_header", &PyReader::main_header)
        .def_readonly("auto_sql", &PyReader::auto_sql)
        .def_readonly("total_summary", &PyReader::total_summary)
        .def_readonly("chr_tree_header", &PyReader::chr_tree_header)
        .def_readonly("zoom_headers", &PyReader::zoom_headers)
        .def_readonly("chr_sizes", &PyReader::chr_sizes)
        .def_readonly("type", &PyReader::type)
        .def_readonly("data_count", &PyReader::data_count)
        .def("read_signal", &PyReader::read_signal,
            "Read values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"), py::arg("span"), 
            py::arg("bin_size") = 1, py::arg("bin_mode") = "mean", py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f, py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("quantify", &PyReader::quantify,
            "Quantify values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"),
            py::arg("ends") = std::vector<int64_t>{}, py::arg("span") = 1,
            py::arg("def_value") = 0.0f, py::arg("reduce") = "mean", py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("profile", &PyReader::profile,
            "Profile values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"), py::arg("span"),
            py::arg("bin_size") = 1, py::arg("bin_mode") = "mean", py::arg("full_bin") = false,
            py::arg("def_value") = 0.0f, py::arg("reduce") = "mean", py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("read_entries", &PyReader::read_entries,
            "Read entries from BigBed file",
            py::arg("chr_ids"), py::arg("starts"),
            py::arg("ends") = std::vector<int64_t>{}, py::arg("span") = 1,
            py::arg("progress") = py::none())
        .def("to_bedgraph", &PyReader::to_bedgraph,
            "Convert BigWig file to bedGraph format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<std::string>{},
            py::arg("zoom") = -1, py::arg("progress") = py::none())
        .def("to_wig", &PyReader::to_wig,
            "Convert BigWig file to WIG format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<std::string>{},
            py::arg("zoom") = -1, py::arg("progress") = py::none())
        .def("to_bed", &PyReader::to_bed,
            "Convert BigBed file to BED format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<std::string>{},
            py::arg("col_count") = 0, py::arg("progress") = py::none());

}

#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <deque>
#include <fstream>
#include <functional>
#include <future>
#include <map>
#include <mutex>
#include <string>
#include <tuple>
#include <vector>
#include <cmath>
#include <limits>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"
#include "reader_header.cpp"
#include "reader_values.cpp"






class Reader {
    std::string path;
    uint64_t parallel;
    float zoom_correction;
    std::shared_ptr<BufferedFilePool> file;

public:
    MainHeader main_header;
    std::vector<ZoomHeader> zoom_headers;
    OrderedMap<std::string, std::string> auto_sql;
    TotalSummary total_summary;
    ChrTreeHeader chr_tree_header;
    std::vector<ChrTreeLeaf> chr_tree;
    OrderedMap<std::string, ChrTreeLeaf> chr_map;
    std::string type;
    uint32_t data_count;

    Reader(
        const std::string& path,
        uint64_t parallel = 24,
        float zoom_correction = 0.33
    ) : path(path), parallel(parallel), zoom_correction(zoom_correction) {
        file = std::make_shared<BufferedFilePool>(path, "r", parallel);
    }

    std::future<void> read_headers() {
        return std::async(std::launch::async, [this]() {
            main_header = read_main_header(*file);
            zoom_headers = read_zoom_headers(*file, main_header.zoom_levels);
            auto_sql = read_auto_sql(*file, main_header.auto_sql_offset, main_header.field_count);
            total_summary = read_total_summary(*file, main_header.total_summary_offset);
            chr_tree_header = read_chr_tree_header(*file, main_header.chr_tree_offset);
            chr_tree = read_chr_tree(*file, main_header.chr_tree_offset + 32, chr_tree_header.key_size);
            chr_map = convert_chr_tree_to_map(chr_tree);
            type = main_header.magic == 0x888FFC26 ? "bigwig" : "bigbed";
            
            ByteArray buffer = file->read(4, main_header.full_data_offset).get();
            data_count = buffer.read_uint32(0);
        });
    }

    int32_t select_zoom(uint32_t bin_size) {
        int32_t best_level = -1;
        uint32_t best_reduction = 0;
        bin_size = static_cast<uint32_t>(std::round(bin_size * zoom_correction));
        for (uint16_t i = 0; i < zoom_headers.size(); ++i) {
            uint32_t reduction = zoom_headers[i].reduction_level;
            if (reduction <= bin_size && reduction > best_reduction) {
                best_reduction = reduction;
                best_level = i;
            }
        }
        return best_level;
    }

    ChrTreeLeaf parse_chr(const std::string& chr_id) {
        std::string chr_key = chr_id.substr(0, chr_tree_header.key_size);
        auto it = chr_map.find(chr_key);
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(lowercase(chr_key));
        if (it != chr_map.end()) return it->second;
        it = chr_map.find(uppercase(chr_key));
        if (it != chr_map.end()) return it->second;
        if (lowercase(chr_id.substr(0, 3)) == "chr") {
            chr_key = chr_id.substr(3).substr(0, chr_tree_header.key_size);
        } else {
            chr_key = ("chr" + chr_id).substr(0, chr_tree_header.key_size);
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
        throw std::runtime_error(fstring("chr {} not in bigwig ({})", chr_id, available));
    }

    Loc parse_loc(const std::string& chr_id, int64_t start, int64_t end) {
        auto chr_entry = parse_chr(chr_id);
        if (start > end) throw std::runtime_error(fstring("loc {}:{}-{} invalid", chr_id, start, end));
        Loc loc;
        loc.chr_index = chr_entry.chr_index;
        loc.start = start < 0 ? 0 : start;
        loc.end = end < 0 ? 0 : end;
        return loc;
    }

    std::vector<Loc> parse_locs(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        const std::vector<int64_t>& ends,
        uint32_t span = 1,
        uint32_t bin_size = 1,
        bool full_bin = false
    ) {
        if (chr_ids.size() != starts.size() || (!ends.empty() && chr_ids.size() != ends.size())) {
            throw std::runtime_error("length mismatch between chr_ids, starts or ends");
        }
        std::vector<Loc> locs(chr_ids.size());
        uint64_t values_offset = 0;
        for (uint64_t i = 0; i < chr_ids.size(); ++i) {
            auto chr_entry = parse_chr(chr_ids[i]);
            int64_t start = starts[i];
            int64_t end = ends.empty() ? starts[i] + span : ends[i];
            if (full_bin) {
                start = start >= 0
                    ? (start / bin_size) * bin_size
                    : -(((-start + bin_size - 1) / bin_size) * bin_size);
                end = end >= 0
                    ? ((end + bin_size - 1) / bin_size) * bin_size
                    : -((-end / bin_size) * bin_size);
            } else {
                start = start / bin_size * bin_size;
                end = end / bin_size * bin_size;
            }
            if (start > end) {
                throw std::runtime_error(fstring("loc {}:{}-{} at index {} invalid", chr_ids[i], start, end, i));
            }
            auto loc = parse_loc(chr_ids[i], start, end);
            loc.input_index = i;
            loc.values_start_index = values_offset + (loc.start - start) / bin_size;
            values_offset += (end - start) / bin_size;
            loc.values_end_index = values_offset;
            locs[i] = loc;
        }
        std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
            return std::tie(a.chr_index, a.start) < std::tie(b.chr_index, b.start);
        });
        return locs;
    }

    uint64_t get_coverage(const std::vector<Loc>& locs) {
        uint64_t coverage = 0;
        for (const auto& loc : locs) {
            coverage += (loc.end - loc.start);
        }
        return coverage;
    }

    std::vector<float> read_signal(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t bin_size = 1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        int32_t zoom = 0,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        if (bin_size == 0 || bin_size > span) bin_size = span;
        auto locs = parse_locs(chr_ids, starts, {}, span, bin_size);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (type == "bigbed") zoom = -1;
        int32_t zoom_index = zoom < 0 ? -1 : zoom > 0 ? zoom - 1 : select_zoom(bin_size);
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        
        if (type == "bigbed") {
            return pileup_entries_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                bin_size,
                def_value,
                auto_sql,
                parallel,
                tracker
            );
        } else if (bin_mode == "single" || bin_size == 1) {
            return read_signal_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                bin_size,
                def_value,
                zoom_index,
                parallel,
                tracker
            );
        } else {
            return read_signal_stats_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                bin_size,
                bin_mode,
                def_value,
                zoom_index,
                parallel,
                tracker
            );
        }

    }

    std::vector<float> quantify(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        const std::vector<int64_t>& ends = {},
        uint32_t span = 1,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = 0,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        uint32_t bin_size = 1;
        if (bin_size == 0 || bin_size > span) bin_size = span;
        auto locs = parse_locs(chr_ids, starts, ends, span, bin_size);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (type == "bigbed") zoom = -1;
        int32_t zoom_index = zoom < 0 ? -1 : zoom > 0 ? zoom - 1 : select_zoom(bin_size);
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);

        if (type == "bigbed") {
            return pileup_stats_entries_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                bin_size,
                def_value,
                reduce,
                auto_sql,
                parallel,
                tracker
            );
        } else {
            return read_stats_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                def_value,
                reduce,
                zoom_index,
                parallel,
                tracker
            );
        }

    }

    std::vector<float> profile(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t bin_size = 1,
        std::string bin_mode = "mean",
        bool full_bin = false,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = 0,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {

        if (bin_size == 0 || bin_size > span) bin_size = span;
        auto values = read_signal(chr_ids, starts, span, bin_size, bin_mode, full_bin, def_value, zoom, progress);

        uint32_t bin_count = values.size() / chr_ids.size();
        std::vector<FullValueStats> stats(bin_count);
        for (uint32_t col = 0; col < bin_count; ++col) {
            for (uint64_t row = 0; row < chr_ids.size(); ++row) {
                auto value = values[row * bin_count + col];
                if (std::isnan(value)) continue;
                stats[col].count += 1;
                stats[col].sum += value;
                stats[col].sum_squared += value * value;
                if (value < stats[col].min || std::isnan(stats[col].min)) stats[col].min = value;
                if (value > stats[col].max || std::isnan(stats[col].max)) stats[col].max = value;
            }
        }
        std::vector<float> profile(bin_count, def_value);
        for (uint32_t col = 0; col < bin_count; ++col) {
            if (stats[col].count == 0) continue;
            if (reduce == "mean") {
                profile[col] = stats[col].sum / stats[col].count;
            } else if (reduce == "sd") {
                float mean = stats[col].sum / stats[col].count;
                profile[col] = std::sqrt((stats[col].sum_squared / stats[col].count) - (mean * mean));
            } else if (reduce == "sem") {
                float mean = stats[col].sum / stats[col].count;
                float sd = std::sqrt((stats[col].sum_squared / stats[col].count) - (mean * mean));
                profile[col] = sd / std::sqrt(stats[col].count);
            } else if (reduce == "sum") {
                profile[col] = stats[col].sum;
            } else if (reduce == "min") {
                profile[col] = stats[col].min;
            } else if (reduce == "max") {
                profile[col] = stats[col].max;
            } else {
                throw std::runtime_error("reduce " + reduce + " invalid");
            }
        }
        return profile;

    }

    std::vector<std::vector<BedEntry>> read_entries(
        const std::vector<std::string>& chr_ids = {},
        const std::vector<int64_t>& starts = {},
        const std::vector<int64_t>& ends = {},
        uint32_t span = 1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigbed") throw std::runtime_error("read_entries only for bigbed");

        auto locs = parse_locs(chr_ids, starts, ends, span, 1);
        ProgressTracker tracker(get_coverage(locs), progress);

        uint64_t tree_offset = main_header.full_index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);

        return read_entries_at_locs(
            *file,
            main_header.uncompress_buffer_size,
            locs,
            tree_nodes,
            auto_sql,
            parallel,
            tracker
        );

    }

    void to_bedgraph(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigwig") throw std::runtime_error("to_bedgraph only for bigwig");

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");
        auto write_line = [&](std::string chr_id, uint32_t start, uint32_t end, float value) {
            std::string line =
                chr_id + "\t" +
                std::to_string(start) + "\t" +
                std::to_string(end) + "\t" +
                std::to_string(value) + "\n";
            output_file->write_string(line);
        };

        int32_t zoom_index = zoom <= 0 ? -1 : zoom - 1;
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);

            DataIntervalsGenerator data_intervals(node, buffer, zoom_index >= 0);
            for (auto& interval : data_intervals) {
                std::string chr_id = chr_tree[interval.chr_index].key;
                write_line(chr_id, interval.start, interval.end, interval.value);
            }
        }
        tracker.done();

    }

    void to_wig(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        int32_t zoom = -1,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigwig") throw std::runtime_error("to_wig only for bigwig");

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");
        auto write_header_line = [&](std::string chr_id, uint32_t start, int64_t span) {
            std::string line =
                "fixedStep chrom=" + chr_id +
                " start=" + std::to_string(start + 1) +
                " step=" + std::to_string(span) +
                " span=" + std::to_string(span) + "\n";
            output_file->write_string(line);
        };
        
        int32_t zoom_index = zoom <= 0 ? -1 : zoom - 1;
        uint64_t tree_offset = (zoom_index < 0) ?
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_index].index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            
            int64_t span = -1;
            DataIntervalsGenerator data_intervals(node, buffer, zoom_index >= 0);
            for (auto& interval : data_intervals) {
                std::string chr_id = chr_tree[interval.chr_index].key;
                if (interval.end - interval.start != span) {
                    span = interval.end - interval.start;
                    write_header_line(chr_id, interval.start, span);
                }
                output_file->write_string(std::to_string(interval.value) + "\n");
            }
        }
        tracker.done();

    }

    void to_bed(
        const std::string& output_path,
        const std::vector<std::string>& chr_ids = {},
        uint64_t col_count = 0,
        std::function<void(uint64_t, uint64_t)> progress = nullptr
    ) {

        if (type != "bigbed") throw std::runtime_error("to_bed only for bigbed");
        if (col_count == 0) col_count = main_header.field_count;
        if (col_count > main_header.field_count) {
            throw std::runtime_error(fstring("col_count {} exceeds number of fields {}", col_count, main_header.field_count));
        }

        std::vector<Loc> locs;
        locs.reserve(chr_ids.empty() ? chr_map.size() : chr_ids.size());
        for (auto chr_id : chr_ids.empty() ? chr_map.keys() : chr_ids) {
            auto chr_entry = parse_chr(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }
        ProgressTracker tracker(get_coverage(locs), progress);

        auto output_file = open_file(output_path, "w");

        uint64_t tree_offset = main_header.full_index_offset + 48;
        TreeNodesGenerator tree_nodes(*file, locs, tree_offset);
        for (auto& node_with_locs : tree_nodes) {
            tracker.update(tree_nodes.coverage);
            DataTreeLeaf node = node_with_locs.node;
            auto buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            BedEntriesGenerator bed_entries(buffer, auto_sql);
            for (auto& entry : bed_entries) {
                std::string chr_id = chr_tree[entry.chr_index].key;
                std::string line =
                    col_count == 1 ? chr_id :
                    col_count == 2 ? chr_id + "\t" + std::to_string(entry.start) :
                    chr_id + "\t" + std::to_string(entry.start) + "\t" + std::to_string(entry.end);
                uint64_t col_index = 3;
                for (const auto& field : entry.fields) {
                    if (col_index >= col_count) break;
                    line += "\t" + field.second;
                    col_index += 1;
                }
                line += "\n";
                output_file->write_string(line);
            }
        }
        tracker.done();

    }

};

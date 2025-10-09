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

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"
#include "reader_header.cpp"


WigDataHeader read_wig_data_header(const ByteArray& buffer) {
    WigDataHeader header;
    header.chr_index = buffer.read_uint32(0);
    header.chr_start = buffer.read_uint32(4);
    header.chr_end = buffer.read_uint32(8);
    header.item_step = buffer.read_uint32(12);
    header.item_span = buffer.read_uint32(16);
    header.type = buffer.read_uint8(20);
    header.reserved = buffer.read_uint8(21);
    header.item_count = buffer.read_uint16(22);
    return header;
}


ZoomDataRecord read_zoom_data_record(const ByteArray& buffer, uint64_t index) {
    uint64_t offset = index * 32;
    ZoomDataRecord record;
    record.chr_index = buffer.read_uint32(offset);
    record.chr_start = buffer.read_uint32(offset + 4);
    record.chr_end = buffer.read_uint32(offset + 8);
    record.valid_count = buffer.read_uint32(offset + 12);
    record.min_value = buffer.read_float(offset + 16);
    record.max_value = buffer.read_float(offset + 20);
    record.sum_data = buffer.read_float(offset + 24);
    record.sum_squared = buffer.read_float(offset + 28);
    return record;
}


class DataIntervalsGenerator : public GeneratorBase<DataIntervalsGenerator, DataInterval> {
    const ByteArray& buffer;
    bool is_zoom;
    WigDataHeader header;
    uint64_t count;
    uint64_t index = 0;

public:
    DataIntervalsGenerator(const DataTreeLeaf& node, const ByteArray& buffer, bool is_zoom = false) : buffer(buffer), is_zoom(is_zoom) {
        if (is_zoom) {
            count = node.data_size / 32;
        } else {
            header = read_wig_data_header(buffer);
            count = header.item_count;
        }
    }
    
    NextResult next() {
        while (index < count) {
            DataInterval data;
            if (is_zoom) { // zoom record
                ZoomDataRecord record = read_zoom_data_record(buffer, index);
                if (record.valid_count == 0) {
                    index += 1;
                    continue;
                }
                data.chr_index = record.chr_index;
                data.start = record.chr_start;
                data.end = record.chr_end;
                data.value = record.sum_data / record.valid_count;
            } else if (header.type == 1) { // bedgraph
                data.chr_index = header.chr_index;
                data.start = buffer.read_uint32(24 + index * 12);
                data.end = buffer.read_uint32(24 + index * 12 + 4);
                data.value = buffer.read_float(24 + index * 12 + 8);
            } else if (header.type == 2) { // variable step wig
                data.chr_index = header.chr_index;
                data.start = buffer.read_uint32(24 + index * 8);
                data.end = data.start + header.item_span;
                data.value = buffer.read_float(24 + index * 8 + 4);
            } else if (header.type == 3) { // fixed step wig
                data.chr_index = header.chr_index;
                data.start = header.chr_start + index * header.item_step;
                data.end = data.start + header.item_span;
                data.value = buffer.read_float(24 + index * 4);
            } else {
                throw std::runtime_error(fstring("wig data type {} invalid", header.type));
            }
            index += 1;
            return {data, false};
        }
        return {DataInterval{}, true};
    }
};


class BedEntriesGenerator : public GeneratorBase<BedEntriesGenerator, BedEntry> {
    const ByteArray& buffer;
    const OrderedMap<std::string, std::string>& auto_sql;
    uint64_t offset = 0;

public:
    BedEntriesGenerator(const ByteArray& buffer, const OrderedMap<std::string, std::string>& auto_sql)
    : buffer(buffer), auto_sql(auto_sql) {}

    NextResult next() {
        while (offset < buffer.size()) {
            BedEntry entry;
            entry.chr_index = buffer.read_uint32(offset);
            entry.start = buffer.read_uint32(offset + 4);
            entry.end = buffer.read_uint32(offset + 8);
            offset += 12;
            int64_t end_offset = buffer.index('\0', offset);
            if (end_offset == -1) throw std::runtime_error("invalid bed entry (null terminator not found)");
            std::string raw_fields = buffer.read_string(offset, end_offset - offset);
            auto fields = split_string(raw_fields, '\t');
            if (fields.size() != auto_sql.size() - 3) throw std::runtime_error("invalid bed entry (field count mismatch)");
            uint64_t field_index = 0;
            for (const auto& sql_field : auto_sql) {
                if (field_index >= 3) {
                    entry.fields.insert(sql_field.first, fields[field_index - 3]);
                }
                field_index += 1;
            }
            offset = end_offset + 1;
            return {entry, false};
        }
        return {BedEntry{}, true};
    }
};


class LocsLockManager {
private:
    std::vector<std::unique_ptr<std::mutex>> mutexes;

public:
    explicit LocsLockManager(uint32_t locs_count) {
        mutexes.reserve(locs_count);
        for (uint32_t i = 0; i < locs_count; ++i) {
            mutexes.push_back(std::make_unique<std::mutex>());
        }
    }

    std::vector<std::unique_lock<std::mutex>> lock_range(uint32_t start_loc_index, uint32_t end_loc_index) {
        std::vector<std::unique_lock<std::mutex>> locks;
        locks.reserve(end_loc_index - start_loc_index);
        for (uint32_t i = start_loc_index; i < end_loc_index; ++i) {
            if (i < mutexes.size()) {
                locks.emplace_back(*mutexes[i]);
            }
        }
        return locks;
    }
};


bool fill_values_with_value(
    const std::vector<Loc>& locs,
    std::vector<float>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t bin_size,
    uint32_t start, uint32_t end, float value) {

    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        if (start >= loc.end) continue;
        no_more_overlap = false;
        if (end <= loc.start) break;
        if (std::isnan(value)) continue;
        uint32_t overlap_start = std::max(start, loc.start);
        uint32_t overlap_end = std::min(end, loc.end);
        uint32_t loc_bin_start = loc.start / bin_size;
        uint32_t bin_start = overlap_start / bin_size;
        uint32_t bin_end = (overlap_end + bin_size - 1) / bin_size;
        for (uint32_t b = bin_start; b < bin_end; b += 1) {
            uint64_t value_index = loc.values_start_index + (b - loc_bin_start);
            values[value_index] = value;
        }
    }
    return no_more_overlap;
}


bool fill_values_stats_with_value(
    const std::vector<Loc>& locs,
    std::vector<ValueStats>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t bin_size,
    uint32_t start, uint32_t end, float value) {

    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        if (start >= loc.end) continue;
        no_more_overlap = false;
        if (end <= loc.start) break;
        if (std::isnan(value)) continue;
        uint32_t overlap_start = std::max(start, loc.start);
        uint32_t overlap_end = std::min(end, loc.end);
        uint32_t loc_bin_start = loc.start / bin_size;
        uint32_t bin_start = overlap_start / bin_size;
        uint32_t bin_end = (overlap_end + bin_size - 1) / bin_size;
        std::cout << "Filling loc " << loc_index << " from " << overlap_start << " to " << overlap_end << " (bins " << bin_start << " to " << bin_end << ") with value " << value << std::endl;
        for (uint32_t b = bin_start; b < bin_end; b += 1) {
            uint64_t value_index = loc.values_start_index + (b - loc_bin_start);
            ValueStats& stats = values[value_index];
            stats.sum += value;
            stats.count += 1;
        }
    }
    return no_more_overlap;
}


bool fill_stats_with_value(
    const std::vector<Loc>& locs,
    std::vector<FullValueStats>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t start, uint32_t end, float value) {

    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        if (start >= loc.end) continue;
        no_more_overlap = false;
        if (end <= loc.start) break;
        if (std::isnan(value)) continue;
        uint32_t overlap_start = std::max(start, loc.start);
        uint32_t overlap_end = std::min(end, loc.end);
        uint32_t overlap = overlap_end - overlap_start;
        FullValueStats& stats = values[loc_index];
        if (value < stats.min || std::isnan(stats.min)) stats.min = value;
        if (value > stats.max || std::isnan(stats.max)) stats.max = value;
        stats.sum += value * overlap;
        stats.sum_squared += value * value * overlap;
        stats.count += overlap;
    }
    return no_more_overlap;
}


void fill_values_at_locs(
    const ByteArray& buffer,
    const std::vector<Loc>& locs,
    bool is_zoom,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t bin_size,
    std::vector<float>& values) {
    
    DataIntervalsGenerator data_intervals(node, buffer, is_zoom);
    for (auto& interval : data_intervals) {
        auto no_more_overlap = fill_values_with_value(
            locs, values, start_loc_index, end_loc_index, bin_size,
            interval.start, interval.end, interval.value
        );
        if (no_more_overlap) break;
    }
}


void fill_values_stats_at_locs(
    const ByteArray& buffer,
    const std::vector<Loc>& locs,
    bool is_zoom,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t bin_size,
    std::vector<ValueStats>& values) {

    DataIntervalsGenerator data_intervals(node, buffer, is_zoom);
    for (auto& interval : data_intervals) {
        auto no_more_overlap = fill_values_stats_with_value(
            locs, values, start_loc_index, end_loc_index, bin_size,
            interval.start, interval.end, interval.value
        );
        if (no_more_overlap) break;
    }
}


void fill_stats_at_locs(
    const ByteArray& buffer,
    const std::vector<Loc>& locs,
    bool is_zoom,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    std::vector<FullValueStats>& values) {

    DataIntervalsGenerator data_intervals(node, buffer, is_zoom);
    for (auto& interval : data_intervals) {
        auto no_more_overlap = fill_stats_with_value(
            locs, values, start_loc_index, end_loc_index,
            interval.start, interval.end, interval.value
        );
        if (no_more_overlap) break;
    }
}


std::vector<float> reduce_values_stats(
    const std::vector<FullValueStats>& values_stats,
    const std::string& reduce,
    float def_value) {

    std::vector<float> values(values_stats.size(), def_value);
    for (uint64_t i = 0; i < values_stats.size(); ++i) {
        if (values_stats[i].count > 0) {
            if (reduce == "mean") {
                values[i] = values_stats[i].sum / values_stats[i].count;
            } else if (reduce == "sd") {
                float mean = values_stats[i].sum / values_stats[i].count;
                float variance = (values_stats[i].sum_squared / values_stats[i].count) - (mean * mean);
                values[i] = std::sqrt(variance);
            } else if (reduce == "sem") {
                float mean = values_stats[i].sum / values_stats[i].count;
                float variance = (values_stats[i].sum_squared / values_stats[i].count) - (mean * mean);
                values[i] = std::sqrt(variance) / std::sqrt(static_cast<float>(values_stats[i].count));
            } else if (reduce == "sum") {
                values[i] = values_stats[i].sum;
            } else if (reduce == "min") {
                values[i] = values_stats[i].min;
            } else if (reduce == "max") {
                values[i] = values_stats[i].max;
            } else {
                throw std::runtime_error("reduce " + reduce + " invalid");
            }
        }
    }
    return values;
}


std::vector<float> read_signal_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    uint32_t bin_size,
    float def_value,
    int32_t zoom_index,
    uint64_t parallel,
    ProgressTracker& tracker) {

    uint64_t values_size = locs.empty() ? 0 : locs.back().values_end_index;
    std::vector<float> values(values_size, def_value);

    std::deque<std::future<void>> futures;
    for (auto& node_with_locs : tree_nodes) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, node_with_locs, bin_size, &values, zoom_index]() {
            auto buffer = file.read(node_with_locs.node.data_size, node_with_locs.node.data_offset).get();
            if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
            fill_values_at_locs(
                buffer,
                locs,
                zoom_index >= 0,
                node_with_locs.node,
                node_with_locs.start_loc_index,
                node_with_locs.end_loc_index,
                bin_size,
                values
            );
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (parallel == 1) {
                future.get();
                futures.pop_front();
                continue;
            }
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    return values;
}


std::vector<float> read_signal_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    uint32_t bin_size,
    std::string bin_mode,
    float def_value,
    int32_t zoom_index,
    uint64_t parallel,
    ProgressTracker& tracker) {

    LocsLockManager lock_manager(locs.size());
    uint64_t values_size = locs.empty() ? 0 : locs.back().values_end_index;
    std::vector<ValueStats> values_stats(values_size);

    std::deque<std::future<void>> futures;
    for (auto& node_with_locs : tree_nodes) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, node_with_locs, bin_size, &values_stats, zoom_index, &lock_manager]() {
            auto buffer = file.read(node_with_locs.node.data_size, node_with_locs.node.data_offset).get();
            if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
            auto locks = lock_manager.lock_range(node_with_locs.start_loc_index, node_with_locs.end_loc_index);
            fill_values_stats_at_locs(
                buffer,
                locs,
                zoom_index >= 0,
                node_with_locs.node,
                node_with_locs.start_loc_index,
                node_with_locs.end_loc_index,
                bin_size,
                values_stats
            );
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (parallel == 1) {
                future.get();
                futures.pop_front();
                continue;
            }
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    std::vector<float> values(values_size, def_value);
    for (uint64_t i = 0; i < values_stats.size(); ++i) {
        if (values_stats[i].count > 0) {
            if (bin_mode == "mean")
                values[i] = values_stats[i].sum / values_stats[i].count;
            else if (bin_mode == "sum")
                values[i] = values_stats[i].sum;
            else {
                throw std::runtime_error("bin_mode " + bin_mode + " invalid");
            }
        }
    }

    return values;
}


std::vector<float> read_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    float def_value,
    std::string reduce,
    int32_t zoom_index,
    uint64_t parallel,
    ProgressTracker& tracker) {

    LocsLockManager lock_manager(locs.size());
    std::vector<FullValueStats> values_stats(locs.size());

    std::deque<std::future<void>> futures;
    for (auto& node_with_locs : tree_nodes) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, node_with_locs, &values_stats, zoom_index, &lock_manager]() {
            auto buffer = file.read(node_with_locs.node.data_size, node_with_locs.node.data_offset).get();
            if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
            auto locks = lock_manager.lock_range(node_with_locs.start_loc_index, node_with_locs.end_loc_index);
            fill_stats_at_locs(
                buffer,
                locs,
                zoom_index >= 0,
                node_with_locs.node,
                node_with_locs.start_loc_index,
                node_with_locs.end_loc_index,
                values_stats
            );
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (parallel == 1) {
                future.get();
                futures.pop_front();
                continue;
            }
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    return reduce_values_stats(values_stats, reduce, def_value);
}


std::vector<std::vector<BedEntry>> read_entries_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    const OrderedMap<std::string, std::string>& auto_sql,
    uint64_t parallel,
    ProgressTracker& tracker) {

    LocsLockManager lock_manager(locs.size());
    std::vector<std::vector<BedEntry>> locs_entries(locs.size());

    std::deque<std::future<void>> futures;
    for (auto& node_with_locs : tree_nodes) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, node_with_locs, &auto_sql, &locs_entries, &lock_manager]() {
            DataTreeLeaf node = node_with_locs.node;
            auto buffer = file.read(node.data_size, node.data_offset).get();
            if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
            auto locks = lock_manager.lock_range(node_with_locs.start_loc_index, node_with_locs.end_loc_index);
            BedEntriesGenerator bed_entries(buffer, auto_sql);
            for (auto& entry : bed_entries) {
                bool no_more_overlap = true;
                for (uint64_t loc_index = node_with_locs.start_loc_index; loc_index <= node_with_locs.end_loc_index; ++loc_index) {
                    const Loc& loc = locs[loc_index];
                    if (entry.chr_index != loc.chr_index) continue;
                    if (entry.start >= loc.end) continue;
                    no_more_overlap = false;
                    if (entry.end <= loc.start) break;
                    locs_entries[loc_index].push_back(entry);
                }
                if (no_more_overlap) break;
            }
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (parallel == 1) {
                future.get();
                futures.pop_front();
                continue;
            }
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    for (auto& entries : locs_entries) {
        std::sort(entries.begin(), entries.end(), [](const BedEntry& a, const BedEntry& b) {
            return std::tie(a.chr_index, a.start, a.end) < std::tie(b.chr_index, b.start, b.end);
        });
    }
    return locs_entries;
}


std::vector<float> pileup_entries_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    uint32_t bin_size,
    float def_value,
    const OrderedMap<std::string, std::string>& auto_sql,
    uint64_t parallel,
    ProgressTracker& tracker) {

    LocsLockManager lock_manager(locs.size());
    uint64_t values_size = locs.empty() ? 0 : locs.back().values_end_index;
    std::vector<float> values(values_size, def_value);

    std::deque<std::future<void>> futures;
    for (auto& node_with_locs : tree_nodes) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, node_with_locs, bin_size, &auto_sql, &values, &lock_manager]() {
            DataTreeLeaf node = node_with_locs.node;
            auto buffer = file.read(node.data_size, node.data_offset).get();
            if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
            auto locks = lock_manager.lock_range(node_with_locs.start_loc_index, node_with_locs.end_loc_index);
            BedEntriesGenerator bed_entries(buffer, auto_sql);
            for (auto& entry : bed_entries) {
                bool no_more_overlap = true;
                for (uint64_t loc_index = node_with_locs.start_loc_index; loc_index <= node_with_locs.end_loc_index; ++loc_index) {
                    const Loc& loc = locs[loc_index];
                    if (entry.chr_index != loc.chr_index) continue;
                    if (entry.start >= loc.end) continue;
                    no_more_overlap = false;
                    if (entry.end <= loc.start) break;
                    uint32_t overlap_start = std::max(entry.start, loc.start);
                    uint32_t overlap_end = std::min(entry.end, loc.end);
                    uint32_t loc_bin_start = loc.start / bin_size;
                    uint32_t bin_start = overlap_start / bin_size;
                    uint32_t bin_end = (overlap_end + bin_size - 1) / bin_size;
                    for (uint32_t b = bin_start; b < bin_end; b += 1) {
                        uint64_t value_index = loc.values_start_index + (b - loc_bin_start);
                        values[value_index] += 1.0;
                    }
                }
                if (no_more_overlap) break;
            }
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    return values;
}


std::vector<float> pileup_stats_entries_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodesGenerator& tree_nodes,
    uint32_t bin_size,
    float def_value,
    std::string reduce,
    const OrderedMap<std::string, std::string>& auto_sql,
    uint64_t parallel,
    ProgressTracker& tracker) {

    auto values = pileup_entries_at_locs(
        file, uncompress_buffer_size, locs, tree_nodes,
        bin_size, def_value, auto_sql, parallel, tracker
    );
    std::vector<FullValueStats> values_stats(locs.size());
    for (uint64_t row = 0; row < locs.size(); ++row) {
        Loc loc = locs[row];
        FullValueStats& stats = values_stats[row];
        for (auto i = loc.values_start_index; i < loc.values_end_index; ++i) {
            float value = values[i];
            if (!std::isnan(value)) {
                if (value < stats.min || std::isnan(stats.min)) stats.min = value;
                if (value > stats.max || std::isnan(stats.max)) stats.max = value;
                stats.sum += value;
                stats.sum_squared += value * value;
                stats.count += 1;
            }
        }
    }
    return reduce_values_stats(values_stats, reduce, def_value);

}

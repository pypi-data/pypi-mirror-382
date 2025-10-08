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
#include <iostream>
#include <regex>
#include <sstream>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"


MainHeader read_main_header(BufferedFilePool& file) {
    ByteArray buffer = file.read(64, 0).get();
    
    MainHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic != 0x888FFC26 && header.magic != 0x8789F2EB) {
        if (header.magic == 0x26FC8F88 || header.magic == 0xEBF28987) {
            throw std::runtime_error("incompatible endianness");
        }
        throw std::runtime_error("not a bigwig or bigbed file");
    }
    header.version = buffer.read_uint16(4);
    if (header.version < 3) {
        throw std::runtime_error(fstring("bigwig or bigbed version {} unsupported (>= 3)", header.version));
    }
    header.zoom_levels = buffer.read_uint16(6);
    header.chr_tree_offset = buffer.read_uint64(8);
    header.full_data_offset = buffer.read_uint64(16);
    header.full_index_offset = buffer.read_uint64(24);
    header.field_count = buffer.read_uint16(32);
    header.defined_field_count = buffer.read_uint16(34);
    header.auto_sql_offset = buffer.read_uint64(36);
    header.total_summary_offset = buffer.read_uint64(44);
    header.uncompress_buffer_size = buffer.read_uint32(52);
    header.reserved = buffer.read_uint64(56);
    
    return header;
}


std::vector<ZoomHeader> read_zoom_headers(BufferedFilePool& file, uint16_t zoom_levels) {
    std::vector<ZoomHeader> headers;
    ByteArray buffer = file.read(zoom_levels * 24, 64).get();

    for (uint16_t i = 0; i < zoom_levels; ++i) {
        ZoomHeader header;
        header.reduction_level = buffer.read_uint32(i * 24);
        header.reserved = buffer.read_uint32(i * 24 + 4);
        header.data_offset = buffer.read_uint64(i * 24 + 8);
        header.index_offset = buffer.read_uint64(i * 24 + 16);
        headers.push_back(header);
    }
    
    return headers;
}


OrderedMap<std::string, std::string> read_auto_sql(BufferedFilePool& file, uint64_t offset, uint16_t field_count) {
    if (offset == 0) return {};
    ByteArray buffer = file.read(1024, offset, false).get();
    while (buffer.index('\0') == -1) {
        offset += 1024;
        auto next_buffer = file.read(1024, offset, false).get();
        if (next_buffer.size() == 0) throw std::runtime_error("failed to read complete autosql");
        buffer = buffer.extend(next_buffer);
    }
    std::string sql_string = buffer.read_string(0, buffer.index('\0'));
    OrderedMap<std::string, std::string> fields;
    std::regex re(R"(\s*(\S+)\s+([^;]+);)");
    std::smatch match;
    std::istringstream iss(sql_string);
    std::string line;
    while (std::getline(iss, line)) {
        if (std::regex_search(line, match, re)) {
            std::string type = match[1];
            std::string field_list = match[2];
            std::regex field_re(R"(\s*(\S+)\s*(?:,|$))");
            std::sregex_iterator iter(field_list.begin(), field_list.end(), field_re);
            std::sregex_iterator end;
            for (; iter != end; ++iter) {
                std::string name = (*iter)[1].str();
                if (!name.empty()) {
                    fields.insert(name, type);
                }
            }
        }
    }
    if (fields.size() < 3
    || !std::regex_match(fields.key_at_index(0), std::regex(R"(^chr(?:om)_?(?:id|name)?$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(1), std::regex(R"(^(?:chr(?:om)?_?)?start$)", std::regex_constants::icase))
    || !std::regex_match(fields.key_at_index(2), std::regex(R"(^(?:chr(?:om)?_?)?end$)", std::regex_constants::icase))) {
        throw std::runtime_error("missing or misplaced chr, start or end in autosql");
    }
    if (fields.size() != field_count) {
        throw std::runtime_error(fstring("field count {} does not match autosql field count {}", field_count, fields.size()));
    }
    return fields;
}


TotalSummary read_total_summary(BufferedFilePool& file, uint64_t offset) {
    ByteArray buffer = file.read(40, offset).get();

    TotalSummary summary;
    summary.bases_covered = buffer.read_uint64(0);
    summary.min_value = buffer.read_double(8);
    summary.max_value = buffer.read_double(16);
    summary.sum_data = buffer.read_double(24);
    summary.sum_squared = buffer.read_double(32);
    
    return summary;
}


ChrTreeHeader read_chr_tree_header(BufferedFilePool& file, uint64_t offset) {
    ByteArray buffer = file.read(32, offset).get();

    ChrTreeHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic != 0x78CA8C91) {
        if (header.magic == 0x91CA8C78) {
            throw std::runtime_error("incompatible endianness (chromosome tree)");
        }
        throw std::runtime_error("invalid chromosome tree magic");
    }
    header.block_size = buffer.read_uint32(4);
    header.key_size = buffer.read_uint32(8);
    header.value_size = buffer.read_uint32(12);
    header.item_count = buffer.read_uint64(16);
    header.reserved = buffer.read_uint64(24);

    return header;
}


std::vector<ChrTreeLeaf> read_chr_tree(BufferedFilePool& file, uint64_t offset, uint32_t key_size) {
    std::vector<ChrTreeLeaf> leaves;
    ByteArray header_buffer = file.read(4, offset).get();

    ChrTreeNodeHeader node_header;
    node_header.is_leaf = header_buffer.read_uint8(0);
    node_header.reserved = header_buffer.read_uint8(1);
    node_header.count = header_buffer.read_uint16(2);

    offset += 4;
    for (uint16_t i = 0; i < node_header.count; ++i) {
        ByteArray buffer = file.read(key_size + 8, offset).get();
        if (node_header.is_leaf) {
            ChrTreeLeaf leaf;
            leaf.key = buffer.read_string(0, key_size);
            leaf.chr_index = buffer.read_uint32(key_size);
            leaf.chr_size = buffer.read_uint32(key_size + 4);
            leaves.push_back(leaf);
        } else {
            ChrTreeBranch branch;
            branch.key = buffer.read_string(0, key_size);
            branch.child_offset = buffer.read_uint64(key_size);
            auto child_leaves = read_chr_tree(file, branch.child_offset, key_size);
            leaves.insert(leaves.end(), child_leaves.begin(), child_leaves.end());
        }
        offset += key_size + 8;
    }

    std::sort(leaves.begin(), leaves.end(), [](const ChrTreeLeaf& a, const ChrTreeLeaf& b) {
        return a.chr_index < b.chr_index;
    });

    return leaves;
}


OrderedMap<std::string, ChrTreeLeaf> convert_chr_tree_to_map(const std::vector<ChrTreeLeaf>& leaves) {
    OrderedMap<std::string, ChrTreeLeaf> chr_map;
    for (const auto& leaf : leaves) {
        chr_map.insert(leaf.key, leaf);
    }
    return chr_map;
}


DataTreeHeader read_data_tree_header(BufferedFilePool& file, uint64_t offset) {
    ByteArray buffer = file.read(48, offset).get();

    DataTreeHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic == 0x61A0C5A0) throw std::runtime_error("incompatible endianness (data tree)");
    if (header.magic != 0x2468ACE0) throw std::runtime_error("invalid data tree magic");
    header.block_size = buffer.read_uint32(4);
    header.item_count = buffer.read_uint64(8);
    header.start_chr_index = buffer.read_uint32(16);
    header.start_base = buffer.read_uint32(20);
    header.end_chr_index = buffer.read_uint32(24);
    header.end_base = buffer.read_uint32(28);
    header.end_file_offset = buffer.read_uint64(32);
    header.items_per_slot = buffer.read_uint32(40);
    header.reserved = buffer.read_uint8(44);
    
    return header;
}


std::vector<DataTreeLeaf> read_data_tree(BufferedFilePool& file, uint64_t offset) {
    std::vector<DataTreeLeaf> leaves;
    ByteArray header_buffer = file.read(4, offset).get();
    DataTreeNodeHeader node_header;
    node_header.is_leaf = header_buffer.read_uint8(0);
    node_header.reserved = header_buffer.read_uint8(1);
    node_header.count = header_buffer.read_uint16(2);
    uint64_t node_size = node_header.is_leaf ? 32 : 24;

    offset += 4;
    for (uint16_t i = 0; i < node_header.count; ++i) {
        ByteArray buffer = file.read(node_size, offset).get();
        if (node_header.is_leaf) {
            DataTreeLeaf leaf;
            leaf.start_chr_index = buffer.read_uint32(0);
            leaf.start_base = buffer.read_uint32(4);
            leaf.end_chr_index = buffer.read_uint32(8);
            leaf.end_base = buffer.read_uint32(12);
            leaf.data_offset = buffer.read_uint64(16);
            leaf.data_size = buffer.read_uint64(24);
            leaves.push_back(leaf);
        } else {
            DataTreeBranch branch;
            branch.start_chr_index = buffer.read_uint32(0);
            branch.start_base = buffer.read_uint32(4);
            branch.end_chr_index = buffer.read_uint32(8);
            branch.end_base = buffer.read_uint32(12);
            branch.data_offset = buffer.read_uint64(16);
            auto child_leaves = read_data_tree(file, branch.data_offset);
            leaves.insert(leaves.end(), child_leaves.begin(), child_leaves.end());
        }
        offset += node_size;
    }

    std::sort(leaves.begin(), leaves.end(), [](const DataTreeLeaf& a, const DataTreeLeaf& b) {
        return std::tie(a.start_chr_index, a.start_base) < std::tie(b.start_chr_index, b.start_base);
    });

    return leaves;
}


struct TreeNodeWithLocs {
    DataTreeLeaf node;
    uint64_t start_loc_index;
    uint64_t end_loc_index;
};

class TreeNodesGenerator : public GeneratorBase<TreeNodesGenerator, TreeNodeWithLocs> {
    struct State {
        uint64_t offset;
        uint8_t is_leaf;
        uint16_t node_count;
        uint64_t node_size;
        ByteArray buffer;
        uint64_t buffer_index;
        uint16_t node_index;
    };

    BufferedFilePool& file;
    std::vector<Loc> locs;
    uint64_t start_loc_index;
    uint64_t end_loc_index;
    std::deque<State> states;

    State parse_node_header(uint64_t offset) {
        ByteArray header_buffer = file.read(4, offset).get();
        uint8_t is_leaf = header_buffer.read_uint8(0);
        // uint8_t reserved = header_buffer.read_uint8(1);
        uint16_t count = header_buffer.read_uint16(2);
        uint64_t node_size = is_leaf ? 32 : 24;
        ByteArray buffer = file.read(node_size * count, offset + 4).get();
        return {offset, is_leaf, count, node_size, buffer, 0, 0};
    }

public:
    uint64_t coverage;

    TreeNodesGenerator(BufferedFilePool& f, const std::vector<Loc>& l, uint64_t offset)
        : file(f), locs(l) {
            start_loc_index = 0;
            end_loc_index = locs.size();
            coverage = 0;
            states.push_front(parse_node_header(offset));
        }

    NextResult next() {
        while (!states.empty()) {
            State& header = states.front();
            if (header.node_index == header.node_count) states.pop_front();
            while (header.node_index < header.node_count) {
                uint32_t start_chr_index = header.buffer.read_uint32(header.buffer_index);
                uint32_t start_base = header.buffer.read_uint32(header.buffer_index + 4);
                uint32_t end_chr_index = header.buffer.read_uint32(header.buffer_index + 8);
                uint32_t end_base = header.buffer.read_uint32(header.buffer_index + 12);

                uint64_t node_end_loc_index = start_loc_index;
                for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
                    Loc loc = locs[loc_index];
                    if (loc.chr_index < start_chr_index || (loc.chr_index == start_chr_index && loc.end <= start_base)) {
                        coverage += static_cast<uint64_t>(loc.end - loc.start);
                        start_loc_index += 1;
                        continue;
                    }
                    if (loc.chr_index > end_chr_index || (loc.chr_index == end_chr_index && loc.start > end_base)) {
                        break;
                    }
                    node_end_loc_index = loc_index + 1;
                }
                if (node_end_loc_index > start_loc_index) {
                    if (header.is_leaf) {
                        DataTreeLeaf node;
                        node.start_chr_index = start_chr_index;
                        node.start_base = start_base;
                        node.end_chr_index = end_chr_index;
                        node.end_base = end_base;
                        node.data_offset = header.buffer.read_uint64(header.buffer_index + 16);
                        node.data_size = header.buffer.read_uint64(header.buffer_index + 24);
                        header.buffer_index += header.node_size;
                        header.node_index += 1;
                        return {{node, start_loc_index, node_end_loc_index}, false};
                    } else {
                        uint64_t data_offset = header.buffer.read_uint64(header.buffer_index + 16);
                        header.buffer_index += header.node_size;
                        header.node_index += 1;
                        states.push_front(parse_node_header(data_offset));
                        break;
                    }
                } else {
                    header.buffer_index += header.node_size;
                    header.node_index += 1;
                }
            }
        }
        while (start_loc_index < end_loc_index) {
            Loc loc = locs[start_loc_index];
            coverage += static_cast<uint64_t>(loc.end - loc.start);
            start_loc_index += 1;
        }
        return {{DataTreeLeaf(), 0, 0}, true};
    }

};

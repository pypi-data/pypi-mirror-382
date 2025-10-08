#pragma once

#include <cstdint>
#include <string>
#include <limits>

#include "util.cpp"


struct MainHeader {
    uint32_t magic;
    uint16_t version;
    uint16_t zoom_levels;
    uint64_t chr_tree_offset;
    uint64_t full_data_offset;
    uint64_t full_index_offset;
    uint16_t field_count;
    uint16_t defined_field_count;
    uint64_t auto_sql_offset;
    uint64_t total_summary_offset;
    uint32_t uncompress_buffer_size;
    uint64_t reserved;
};


struct ZoomHeader {
    uint32_t reduction_level;
    uint32_t reserved;
    uint64_t data_offset;
    uint64_t index_offset;
};


struct TotalSummary {
    uint64_t bases_covered;
    double min_value;
    double max_value;
    double sum_data;
    double sum_squared;
};


struct ChrTreeHeader {
    uint32_t magic;
    uint32_t block_size;
    uint32_t key_size;
    uint32_t value_size;
    uint64_t item_count;
    uint64_t reserved;
};


struct ChrTreeNodeHeader {
    uint8_t is_leaf;
    uint8_t reserved;
    uint16_t count;
};


struct ChrTreeLeaf {
    std::string key;
    uint32_t chr_index;
    uint32_t chr_size;
};


struct ChrTreeBranch {
    std::string key;
    uint64_t child_offset;
};


struct BedEntry {
    uint32_t chr_index;
    uint32_t start;
    uint32_t end;
    OrderedMap<std::string, std::string> fields;
};


struct WigDataHeader {
    uint32_t chr_index;
    uint32_t chr_start;
    uint32_t chr_end;
    uint32_t item_step;
    uint32_t item_span;
    uint8_t type;
    uint8_t reserved;
    uint16_t item_count;
};


struct DataTreeHeader {
    uint32_t magic;
    uint32_t block_size;
    uint64_t item_count;
    uint32_t start_chr_index;
    uint32_t start_base;
    uint32_t end_chr_index;
    uint32_t end_base;
    uint64_t end_file_offset;
    uint32_t items_per_slot;
    uint8_t reserved;
};


struct DataTreeNodeHeader {
    uint8_t is_leaf;
    uint8_t reserved;
    uint16_t count;
};


struct DataTreeLeaf {
    uint32_t start_chr_index;
    uint32_t start_base;
    uint32_t end_chr_index;
    uint32_t end_base;
    uint64_t data_offset;
    uint64_t data_size;
};


struct DataTreeBranch {
    uint32_t start_chr_index;
    uint32_t start_base;
    uint32_t end_chr_index;
    uint32_t end_base;
    uint64_t data_offset;
};


struct ZoomDataRecord {
    uint32_t chr_index;
    uint32_t chr_start;
    uint32_t chr_end;
    uint32_t valid_count;
    float min_value;
    float max_value;
    float sum_data;
    float sum_squared;
};


struct DataInterval {
    uint32_t chr_index;
    uint32_t start;
    uint32_t end;
    float value;
};


struct ValueStats {
    float sum = 0;
    uint32_t count = 0;
};
struct FullValueStats {
    float min = std::numeric_limits<float>::quiet_NaN();
    float max = std::numeric_limits<float>::quiet_NaN();
    float sum = 0;
    float sum_squared = 0;
    uint32_t count = 0;
};


struct Loc {
    uint32_t chr_index;
    uint32_t start;
    uint32_t end;
    uint64_t input_index;
    uint64_t values_start_index;
    uint64_t values_end_index;
    FullValueStats stats;
};

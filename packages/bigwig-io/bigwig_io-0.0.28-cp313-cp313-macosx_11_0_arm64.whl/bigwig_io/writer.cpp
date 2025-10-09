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


class BigwigWriter {
    std::shared_ptr<TemporaryDirectory> tmp_dir;
    std::string accumulator_chr = "";
    std::tuple<uint32_t, uint32_t, std::vector<float>> values_accumulator;
    std::vector<std::tuple<uint32_t, uint32_t, float>> intervals_accumulator;
    uint32_t block_size = 256;
    uint32_t items_per_slot = 1024;
    


    void flush_wig_data_block(const std::string& chr_id, uint32_t start, uint32_t end, const std::vector<float>& values) {
        // to do
    }

    void flush_bedgraph_data_block(const std::string& chr_id, const std::vector<std::tuple<uint32_t, uint32_t, float>>& intervals) {
        // to do
    }

    void flush_accumulators(const std::string& chr_id, uint32_t start, uint32_t resolution, bool interval = false, bool force = false) {
        if (std::get<2>(values_accumulator).size()) {
            auto accumulator_start = std::get<0>(values_accumulator);
            auto accumulator_resolution = std::get<1>(values_accumulator);
            auto accumulator_size = static_cast<uint32_t>(std::get<2>(values_accumulator).size());
            auto accumulator_end = accumulator_start + accumulator_resolution * accumulator_size;
            auto flush_all = force || interval ||
                chr_id != accumulator_chr ||
                start != accumulator_end ||
                resolution != accumulator_resolution;
            auto flush = flush_all || accumulator_size >= items_per_slot;
            if (!flush) return;
            uint32_t index = 0;
            for (index = 0; index < accumulator_size; index += block_size) {
                if (index + block_size > accumulator_size && !flush_all) break;
                auto block_start = accumulator_start + accumulator_resolution * index;
                auto block_end = block_start + accumulator_resolution * block_size;
                if (block_end > accumulator_end) block_end = accumulator_end;
                auto block_values = std::vector<float>(
                    std::get<2>(values_accumulator).begin() + index,
                    std::get<2>(values_accumulator).begin() + std::min(index + block_size, accumulator_size)
                );
                flush_wig_data_block(accumulator_chr, block_start, block_end, block_values);
            }
            if (index >= accumulator_size) {
                std::get<0>(values_accumulator) = start;
                std::get<2>(values_accumulator).clear();
            } else {
                std::get<0>(values_accumulator) += accumulator_resolution * index;
                std::get<2>(values_accumulator) = std::vector<float>(
                    std::get<2>(values_accumulator).begin() + index,
                    std::get<2>(values_accumulator).end()
                );
            }
            std::get<1>(values_accumulator) = resolution;
        } else if (!intervals_accumulator.empty()) {
            auto accumulator_size = static_cast<uint32_t>(intervals_accumulator.size());
            auto flush_all = force || !interval ||  chr_id != accumulator_chr;
            auto flush = flush_all || accumulator_size >= items_per_slot;
            if (!flush) return;
            uint32_t index = 0;
            for (index = 0; index < accumulator_size; index += block_size) {
                if (index + block_size > accumulator_size && !flush_all) break;
                auto block_intervals = std::vector<std::tuple<uint32_t, uint32_t, float>>(
                    intervals_accumulator.begin() + index,
                    intervals_accumulator.begin() + std::min(index + block_size, accumulator_size)
                );
                flush_bedgraph_data_block(accumulator_chr, block_intervals);
            }
            if (index >= accumulator_size) {
                intervals_accumulator.clear();
            } else {
                intervals_accumulator = std::vector<std::tuple<uint32_t, uint32_t, float>>(
                    intervals_accumulator.begin() + index,
                    intervals_accumulator.end()
                );
            }
        }
        accumulator_chr = chr_id;
    }



public:
    BigwigWriter(std::string path) {
        tmp_dir = std::make_shared<TemporaryDirectory>(path, ".tmp.");

        

    }



    void add_values(const std::string& chr_id, uint32_t start, uint32_t resolution, const std::vector<float>& values) {
        flush_accumulators(chr_id, start, resolution);
        std::get<2>(values_accumulator).insert(
            std::get<2>(values_accumulator).end(),
            values.begin(),
            values.end()
        );
    }

    void add_interval(const std::string& chr_id, uint32_t start, uint32_t end, float value) {
        flush_accumulators(chr_id, start, 0, true);
        intervals_accumulator.push_back(std::make_tuple(start, end, value));
    }




};


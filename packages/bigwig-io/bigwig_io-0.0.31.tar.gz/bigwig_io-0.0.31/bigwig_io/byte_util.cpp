#pragma once

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>

#include <zlib.h>


class ByteArray {
public:
    std::vector<uint8_t> data;

    ByteArray(const std::vector<uint8_t>& d) : data(d) {}
    ByteArray(std::vector<uint8_t>&& d) : data(std::move(d)) {}

    uint64_t size() const {
        return data.size();
    }

    uint8_t read_uint8(uint64_t offset) const {
        return data[offset];
    }

    uint16_t read_uint16(uint64_t offset) const {
        return *reinterpret_cast<const uint16_t*>(&data[offset]);
    }

    uint32_t read_uint32(uint64_t offset) const {
        return *reinterpret_cast<const uint32_t*>(&data[offset]);
    }

    uint64_t read_uint64(uint64_t offset) const {
        return *reinterpret_cast<const uint64_t*>(&data[offset]);
    }

    float read_float(uint64_t offset) const {
        return *reinterpret_cast<const float*>(&data[offset]);
    }

    double read_double(uint64_t offset) const {
        return *reinterpret_cast<const double*>(&data[offset]);
    }

    std::string read_string(uint64_t offset, uint64_t length) const {
        std::string item(data.begin() + offset, data.begin() + offset + length);
        auto null_pos = item.find('\0');
        if (null_pos != std::string::npos) item.resize(null_pos);
        return item;
    }


    std::string read_string_until(uint64_t offset, char delimiter = '\0', bool include_delimiter = false) const {
        auto delimiter_index = index(static_cast<uint8_t>(delimiter), offset);
        if (delimiter_index == -1) {
            return std::string(data.begin() + offset, data.end());
        } else if (include_delimiter) {
            return std::string(data.begin() + offset, data.begin() + delimiter_index + 1);
        } else {
            return std::string(data.begin() + offset, data.begin() + delimiter_index);
        }
    }

    std::vector<std::string> read_lines() const {
        std::vector<std::string> lines;
        std::istringstream stream(std::string(data.begin(), data.end()));
        std::string line;
        while (std::getline(stream, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            lines.push_back(std::move(line));
        }
        return lines;
    }

    ByteArray slice(uint64_t offset, uint64_t length) const {
        if (offset > data.size()) offset = data.size();
        if (offset + length > data.size()) length = data.size() - offset;
        std::vector<uint8_t> slice_data(data.begin() + offset, data.begin() + offset + length);
        return ByteArray(slice_data);
    }

    ByteArray extend(const ByteArray& other) const {
        std::vector<uint8_t> combined_data = data;
        combined_data.insert(combined_data.end(), other.data.begin(), other.data.end());
        return ByteArray(combined_data);
    }


    int64_t index(uint8_t byte, uint64_t start = 0) const {
        for (uint64_t i = start; i < data.size(); ++i) {
            if (data[i] == byte) return static_cast<int64_t>(i);
        }
        return -1;
    }

    ByteArray decompress(uint64_t buffer_size = 32768, uint64_t max_size = 1073741824) {
        if (buffer_size < 1 || buffer_size > max_size) {
            throw std::runtime_error("buffer size " + std::to_string(buffer_size) + " invalid");
        }
        std::vector<uint8_t> decompressed_data;
        std::vector<uint8_t> buffer(buffer_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = data.data();
        int init_result = inflateInit2(&stream, 15 + 32);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for decompression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        while (true) {
            stream.avail_out = static_cast<uInt>(buffer_size);
            stream.next_out = buffer.data();
            int ret = inflate(&stream, Z_NO_FLUSH);
            if (ret != Z_OK && ret != Z_STREAM_END) {
                std::string error_msg = "zlib decompression failed: ";
                switch (ret) {
                    case Z_STREAM_ERROR: error_msg += "invalid compression level"; break;
                    case Z_DATA_ERROR: error_msg += "invalid or incomplete deflate data"; break;
                    case Z_MEM_ERROR: error_msg += "out of memory"; break;
                    case Z_BUF_ERROR: error_msg += "no progress possible or output buffer too small"; break;
                    default: error_msg += "error code " + std::to_string(ret); break;
                }
                if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
                inflateEnd(&stream);
                throw std::runtime_error(error_msg);
            }
            uint64_t decompressed = buffer_size - stream.avail_out;
            if (decompressed_data.size() + decompressed > max_size) {
                inflateEnd(&stream);
                throw std::runtime_error("decompressed data exceeds limit (" + std::to_string(max_size) + ")");
            }
            if (ret == Z_STREAM_END && decompressed_data.size() == 0 && decompressed == buffer_size) {
                decompressed_data = std::move(buffer);
                break;
            }
            decompressed_data.insert(decompressed_data.end(), buffer.begin(), buffer.begin() + decompressed);
            if (ret == Z_STREAM_END) break;
        }
        inflateEnd(&stream);
        return ByteArray(std::move(decompressed_data));
    }

    ByteArray compress(std::string format = "gzip", int8_t compression_level = Z_DEFAULT_COMPRESSION) {
        uLong compressed_size = compressBound(static_cast<uLong>(data.size()));
        std::vector<uint8_t> compressed_data(compressed_size);
        z_stream stream{};
        stream.avail_in = static_cast<uInt>(data.size());
        stream.next_in = data.data();
        stream.avail_out = static_cast<uInt>(compressed_size);
        stream.next_out = compressed_data.data();
        int window_bits = format == "gzip" ? (15 + 16) : (format == "zlib" ? 15 : -15); // -15 = raw deflate
        int init_result = deflateInit2(&stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY);
        if (init_result != Z_OK) {
            throw std::runtime_error("failed to initialize zlib for compression: " + 
                std::string(stream.msg ? stream.msg : "unknown error"));
        }
        int ret = deflate(&stream, Z_FINISH);
        if (ret != Z_STREAM_END) {
            std::string error_msg = "zlib compression failed: ";
            switch (ret) {
                case Z_OK: error_msg += "incomplete compression"; break;
                case Z_STREAM_ERROR: error_msg += "invalid compression level or parameters"; break;
                case Z_BUF_ERROR: error_msg += "no progress possible or output buffer too small"; break;
                default: error_msg += "error code " + std::to_string(ret); break;
            }
            if (stream.msg) error_msg += " (" + std::string(stream.msg) + ")";
            deflateEnd(&stream);
            throw std::runtime_error(error_msg);
        }
        compressed_data.resize(stream.total_out);
        deflateEnd(&stream);
        return ByteArray(std::move(compressed_data));
    }

};

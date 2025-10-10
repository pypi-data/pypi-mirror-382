#pragma once

#include <cstdint>
#include <deque>
#include <fstream>
#include <future>
#include <map>
#include <memory>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <filesystem>
#include <random>
#include <queue>
#include <future>
#include <list>

#include <curl/curl.h>
#include <zlib.h>

#include "util.cpp"
#include "byte_util.cpp"


class File {
public:
    virtual ~File() = default;
    virtual int64_t get_file_size(bool acquire_lock = true) = 0;
    virtual std::vector<uint8_t> read(int64_t size, int64_t offset) = 0;
    virtual void write(const std::vector<uint8_t>& data, int64_t offset) = 0;

    virtual void write_string(const std::string& str, int64_t offset = -1) {
        std::vector<uint8_t> data(str.begin(), str.end());
        write(data, offset);
    }

};


class LocalFile : public File {
    std::string path;
    std::string mode;
    std::unique_ptr<std::fstream> file_handle;
    mutable std::mutex file_lock;

    void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) {
        file_handle->seekg(offset, dir);
        if (file_handle->fail()) {
            throw std::runtime_error("failed to seek to " + std::to_string(offset) + " in file " + path);
        }
    }

    int64_t tell() {
        int64_t offset = file_handle->tellg();
        if (offset < 0) throw std::runtime_error("error determining cursor position in file " + path);
        return offset;
    }

public:
    LocalFile(const std::string& p, const std::string& m = "r") : path(p), mode(m) {
        std::ios::openmode flag = std::ios::binary;
        if (mode == "r") {
            flag |= std::ios::in;
        } else if (mode == "w") {
            flag |= std::ios::out;
        } else {
            throw std::runtime_error("file open mode " + mode + " not supported");
        }
        file_handle = std::make_unique<std::fstream>(path, flag);
        if (!file_handle->is_open()) {
            throw std::runtime_error("failed to open file " + path);
        }
    }

    ~LocalFile() {
        if (file_handle && file_handle->is_open()) {
            file_handle->close();
        }
    }

    int64_t get_file_size(bool acquire_lock = true) override {
        std::unique_lock<std::mutex> lock(file_lock, std::defer_lock);
        if (acquire_lock) lock.lock();
        auto current_pos = tell();
        seek(0, std::ios::end);
        auto size = tell();
        seek(current_pos);
        return size;
    }

    std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1) override {
        if (mode != "r") throw std::runtime_error("error reading file " + path + " (not in read mode)");
        std::lock_guard<std::mutex> lock(file_lock);
        if (size < 0) size = get_file_size(false);
        if (offset >= 0) seek(offset);
        std::vector<uint8_t> buffer(size);
        if (size == 0) return buffer;
        file_handle->read(reinterpret_cast<char*>(buffer.data()), size);
        std::streamsize bytes_read = file_handle->gcount();
        if (file_handle->bad() || file_handle->fail()) {
            if (file_handle->eof()) {
                buffer.resize(bytes_read);
            } else {
                std::string reason = " (" + std::string(strerror(errno)) + ")";
                throw std::runtime_error("error reading file " + path + reason);
            }
        }
        return buffer;
    }

    void write(const std::vector<uint8_t>& data, int64_t offset = -1) override {
        if (mode != "w") throw std::runtime_error("error writing to file " + path + " (not in write mode)");
        std::lock_guard<std::mutex> lock(file_lock);
        if (offset >= 0) seek(offset);
        file_handle->write(reinterpret_cast<const char*>(data.data()), data.size());
        if (file_handle->bad() || file_handle->fail()) {
            std::string size = std::to_string(data.size());
            std::string reason = " (" + std::string(strerror(errno)) + ")";
            throw std::runtime_error("failed to write " + size + " bytes to file " + path + reason);
        }
    }

};


class CompressedLocalFile : public File {
    std::string path;
    std::string mode;
    std::unique_ptr<std::fstream> file_handle;
    mutable std::mutex file_lock;

    std::string format;
    int8_t compression_level;
    z_stream inner_stream;
    std::vector<uint8_t> buffer;
    uint64_t buffer_size = 32768;
    uint64_t buffer_start;
    uint64_t buffer_end;

    void init_zlib() {
        memset(&inner_stream, 0, sizeof(inner_stream));
        int window_bits;
        if (format == "gzip") {
            window_bits = MAX_WBITS | 16;
        } else if (format == "zlib") {
            window_bits = MAX_WBITS;
        } else if (format == "deflate" || format == "raw") {
            window_bits = -MAX_WBITS;
        } else {
            throw std::runtime_error("compression format " + format + " invalid");
        }
        if (mode == "r") {
            if (inflateInit2(&inner_stream, window_bits) != Z_OK) {
                std::string error_msg = inner_stream.msg ? inner_stream.msg : "unknown error";
                throw std::runtime_error("failed to initialize decompression stream: " + error_msg);
            }
        } else {
            if (deflateInit2(&inner_stream, compression_level, Z_DEFLATED, window_bits, 8, Z_DEFAULT_STRATEGY) != Z_OK) {
                std::string error_msg = inner_stream.msg ? inner_stream.msg : "unknown error";
                throw std::runtime_error("failed to initialize compression stream: " + error_msg);
            }
        }
        buffer.resize(buffer_size);
        buffer_start = 0;
        buffer_end = 0;
    }

    void cleanup_zlib() {
        if (mode == "r") {
            inflateEnd(&inner_stream);
        } else {
            deflateEnd(&inner_stream);
        }
    }

    void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) {
        if (offset != 0 || dir != std::ios::beg) {
            throw std::runtime_error("only seek(0) is allowed for compressed files");
        }
        file_handle->seekg(offset, dir);
        if (file_handle->fail()) {
            throw std::runtime_error("failed to seek to " + std::to_string(offset) + " in compressed file " + path);
        }
        cleanup_zlib();
        init_zlib();
    }

    int64_t tell() {
        int64_t offset = file_handle->tellg();
        if (offset < 0) throw std::runtime_error("error determining cursor position in compressed file " + path);
        return offset;
    }

    
public:
    CompressedLocalFile(
        const std::string& p,
        const std::string& m = "r",
        const std::string& f = "gzip",
        int8_t compression_level = Z_DEFAULT_COMPRESSION
    ) : path(p), mode(m), format(f), compression_level(compression_level) {

        std::ios::openmode flag = std::ios::binary;
        if (mode == "r") {
            flag |= std::ios::in;
        } else if (mode == "w") {
            flag |= std::ios::out;
        } else {
            throw std::runtime_error("file open mode " + mode + " not supported");
        }
        file_handle = std::make_unique<std::fstream>(path, flag);
        if (!file_handle->is_open()) {
            throw std::runtime_error("failed to open file " + path);
        }
        init_zlib();
    }

    ~CompressedLocalFile() {
        cleanup_zlib();
        if (file_handle && file_handle->is_open()) {
            file_handle->close();
        }
    }

    int64_t get_file_size(bool acquire_lock = true) override {
        std::unique_lock<std::mutex> lock(file_lock, std::defer_lock);
        if (acquire_lock) lock.lock();
        auto current_pos = tell();
        seek(0, std::ios::end);
        auto size = tell();
        seek(current_pos);
        return size;
    }

    std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1) override {
        if (mode != "r") throw std::runtime_error("error reading file " + path + " (not in read mode)");
        std::lock_guard<std::mutex> lock(file_lock);
        if (offset >= 0) seek(offset);
        std::vector<uint8_t> result;
        while (true) {
            if (buffer_end > buffer_start) {
                int64_t available = buffer_end - buffer_start;
                if (size >= 0 && available >= size) {
                    result.insert(result.end(), buffer.begin() + buffer_start, buffer.begin() + buffer_start + size);
                    buffer_start += size;
                    return result;
                } else {
                    result.insert(result.end(), buffer.begin() + buffer_start, buffer.begin() + buffer_end);
                    size -= available;
                    buffer_start = buffer_end;
                }
            }



            if (file_handle->eof()) {
                return result;
            }
            file_handle->read(reinterpret_cast<char*>(buffer.data()), buffer_size);
            std::streamsize bytes_read = file_handle->gcount();
            if (file_handle->bad() || file_handle->fail()) {
                if (file_handle->eof() && bytes_read == 0) {
                    return result;
                } else {
                    std::string reason = " (" + std::string(strerror(errno)) + ")";
                    throw std::runtime_error("error reading compressed file " + path + reason);
                }
            }
            if (bytes_read == 0) {
                return result;
            }
            inner_stream.avail_in = static_cast<uInt>(bytes_read);
            inner_stream.next_in = buffer.data();
            buffer_start = 0;
            buffer_end = 0;
            while (inner_stream.avail_in > 0) {
                inner_stream.avail_out = static_cast<uInt>(buffer_size - buffer_end);
                inner_stream.next_out = buffer.data() + buffer_end;
                int ret = inflate(&inner_stream, Z_NO_FLUSH);
                if (ret != Z_OK && ret != Z_STREAM_END) {
                    std::string error_msg = "zlib decompression failed: ";
                    switch (ret) {
                        case Z_STREAM_ERROR: error_msg += "invalid compression level"; break;
                        case Z_DATA_ERROR: error_msg += "invalid or incomplete deflate data"; break;
                        case Z_MEM_ERROR: error_msg += "out of memory"; break;
                        case Z_BUF_ERROR: error_msg += "no progress possible or output buffer too small"; break;
                        default: error_msg += "error code " + std::to_string(ret); break;
                    }
                    if (inner_stream.msg) error_msg += " (" + std::string(inner_stream.msg) + ")";
                    throw std::runtime_error(error_msg);
                }
                uint64_t decompressed = buffer_size - inner_stream.avail_out - buffer_end;
                buffer_end += decompressed;
                if (ret == Z_STREAM_END) break;
            }

        }
        



        return {};
    }


};








struct CurlWriteData {
    std::vector<uint8_t>* buffer;
    size_t expected_size;
};

static size_t custom_curl_write_callback(void* contents, size_t size, size_t nmemb, CurlWriteData* write_data) {
    size_t total_size = size * nmemb;
    uint8_t* data = static_cast<uint8_t*>(contents);
    
    write_data->buffer->insert(write_data->buffer->end(), data, data + total_size);
    return total_size;
}

class CurlGlobalManager {
private:
    std::mutex manager_lock;
    uint64_t ref_count;
    
    CurlGlobalManager() : ref_count(0) {}
    
public:
    CurlGlobalManager(const CurlGlobalManager&) = delete;
    CurlGlobalManager& operator=(const CurlGlobalManager&) = delete;
    
    static CurlGlobalManager& getInstance() {
        static CurlGlobalManager instance;
        return instance;
    }
    
    void initialize() {
        std::lock_guard<std::mutex> lock(manager_lock);
        if (ref_count == 0) curl_global_init(CURL_GLOBAL_DEFAULT);
        ref_count++;
    }
    
    void cleanup() {
        std::lock_guard<std::mutex> lock(manager_lock);
        ref_count--;
        if (ref_count == 0) curl_global_cleanup();
    }
    
    ~CurlGlobalManager() {
        if (ref_count > 0) curl_global_cleanup();
    }
};

class UrlFile : public File {
    std::string path;
    std::string mode;
    mutable std::mutex curl_lock;
    CURL* curl_handle;
    int64_t current_file_size = -1;
    int64_t current_offset = 0;

    std::vector<uint8_t> read_all() {
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        std::vector<uint8_t> buffer;
        CurlWriteData write_data;
        write_data.buffer = &buffer;
        write_data.expected_size = 0; // Not used for full read
        
        // Configure curl for this request
        curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, nullptr); // No range header
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, custom_curl_write_callback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &write_data);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, ""); // All supported
        
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        
        // Check response code
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 200) { // 200 = OK
            std::string reason = " (http request failed with code " + std::to_string(response_code) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        return buffer;
    }

public:
    UrlFile(const std::string& p, const std::string& m = "r") : path(p), mode(m), curl_handle(nullptr) {
        // Initialize curl globally using singleton
        CurlGlobalManager::getInstance().initialize();
        curl_handle = curl_easy_init();
        if (!curl_handle) {
            CurlGlobalManager::getInstance().cleanup(); // Clean up on failure
            throw std::runtime_error("failed to initialize curl");
        }
        
        // Set common curl options
        curl_easy_setopt(curl_handle, CURLOPT_URL, path.c_str());
        curl_easy_setopt(curl_handle, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_TIMEOUT, 30L);
        curl_easy_setopt(curl_handle, CURLOPT_CONNECTTIMEOUT, 10L);
        curl_easy_setopt(curl_handle, CURLOPT_USERAGENT, "UrlFile/1.0");
        curl_easy_setopt(curl_handle, CURLOPT_FAILONERROR, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, ""); // All supported
        curl_easy_setopt(curl_handle, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_2TLS);
    }
    
    ~UrlFile() {
        if (curl_handle) curl_easy_cleanup(curl_handle);
        CurlGlobalManager::getInstance().cleanup();
    }
    
    int64_t get_file_size(bool acquire_lock = true) override {
        if (current_file_size >= 0) return current_file_size;
        std::unique_lock<std::mutex> lock(curl_lock, std::defer_lock);
        if (acquire_lock) lock.lock();
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        double file_size = 0.0;
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_HEADER, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 1L);
        CURLcode res = curl_easy_perform(curl_handle);
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error determining size of " + path + reason);
        }
        res = curl_easy_getinfo(curl_handle, CURLINFO_CONTENT_LENGTH_DOWNLOAD_T, &file_size);
        if (res != CURLE_OK || file_size < 0) {
            std::string reason = " (could not get content length)";
            throw std::runtime_error("error determining size of " + path + reason);
        }
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 0L);
        current_file_size = static_cast<int64_t>(file_size);
        return current_file_size;
    }

    std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1) override {
        if (mode != "r") throw std::runtime_error("error reading file " + path + " (not in read mode)");
        std::lock_guard<std::mutex> lock(curl_lock);
        if (offset < 0) offset = current_offset;
        if (size < 0) {
            if (offset == 0) return read_all();
            size = get_file_size(false) - offset;
        }
        if (!curl_handle) throw std::runtime_error("curl_handle is not initialized");
        
        // Initialize buffer as empty, let curl callback fill it
        std::vector<uint8_t> buffer;
        buffer.reserve(size);
        CurlWriteData write_data;
        write_data.buffer = &buffer;
        write_data.expected_size = size;
        
        // Set up range request
        std::string range_header = "Range: bytes=" + std::to_string(offset) + "-" + std::to_string(offset + size - 1);
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, range_header.c_str());
        
        // Configure curl for this request
        curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, custom_curl_write_callback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &write_data);
        curl_easy_setopt(curl_handle, CURLOPT_ACCEPT_ENCODING, "");  // All supported
        
        // DEBUG: Enable verbose output to see all headers
        //curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 1L);
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        // DEBUG: Disable verbose output after request
        //curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 0L);
        //throw std::runtime_error("debug");
        
        // Clean up headers
        curl_slist_free_all(headers);
        
        if (res != CURLE_OK) {
            std::string reason = " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        
        // Check response code
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 206 && response_code != 200) { // 206 = Partial Content, 200 = OK
            std::string reason = " (http request failed with code " + std::to_string(response_code) + ")";
            throw std::runtime_error("error reading " + path + reason);
        }
        
        current_offset = offset + buffer.size();
        return buffer;
    }

    void write(const std::vector<uint8_t>& /* data */, int64_t /* offset */) override {
        if (mode != "w") throw std::runtime_error("error writing to file " + path + " (not in write mode)");
        throw std::runtime_error("writing to url not supported");
    }

};


std::shared_ptr<File> open_file(const std::string& path, const std::string& mode) {
    if (path.substr(0, 6) == "ftp://" || path.substr(0, 7) == "http://" || path.substr(0, 8) == "https://") {
        return std::make_shared<UrlFile>(path, mode);
    } else {
        return std::make_shared<LocalFile>(path, mode);
    }
}


class FilePool {
    std::mutex pool_lock;
    Semaphore read_lock;
    std::mutex write_lock;
    std::queue <std::shared_ptr<File>> pool;

    std::shared_ptr<File> get_file() {
        std::lock_guard<std::mutex> lock(pool_lock);
        auto file = pool.front();
        pool.pop();
        return file;
    }

    void return_file(std::shared_ptr<File> file) {
        std::lock_guard<std::mutex> lock(pool_lock);
        pool.push(file);
    }

public:
    FilePool(const std::string& path, const std::string& mode = "r", uint64_t parallel = 1) : read_lock(parallel) {
        for (uint64_t i = 0; i < parallel; ++i) {
            pool.push(open_file(path, mode));
        }
    }

    std::future<int64_t> get_file_size() {
        return std::async(std::launch::async, [this]() {
            SemaphoreGuard guard(read_lock);
            auto file = get_file();
            try {
                auto size = file->get_file_size();
                return_file(file);
                return size;
            } catch (...) {
                return_file(file);
                throw;
            }
        });
    }

    std::future<std::vector<uint8_t>> read(int64_t size, int64_t offset) {
        if (offset < 0) throw std::runtime_error("offset must be specified");
        return std::async(std::launch::async, [this, size, offset]() {
            SemaphoreGuard guard(read_lock);
            auto file = get_file();
            try {
                auto result = file->read(size, offset);
                return_file(file);
                return result;
            } catch (...) {
                return_file(file);
                throw;
            }
        });
    }

    std::future<void> write(const std::vector<uint8_t>& data, int64_t offset) {
        return std::async(std::launch::async, [this, data, offset]() {
            std::lock_guard<std::mutex> lock(write_lock);
            auto file = get_file();
            try {
                file->write(data, offset);
                return_file(file);
            } catch (...) {
                return_file(file);
                throw;
            }
        });
    }

};


class BufferedFilePoolBuffer {
public:
    uint64_t offset;
    uint64_t length;
    std::promise<ByteArray> data_promise;
    std::shared_future<ByteArray> data_future;

    BufferedFilePoolBuffer(uint64_t o, uint64_t l) : offset(o), length(l) {
        data_promise = std::promise<ByteArray>();
        data_future = data_promise.get_future().share();
    }

    bool contains(uint64_t req_offset, uint64_t req_length) const {
        return req_offset >= offset && req_offset + req_length <= offset + length;
    }

    ByteArray extract(uint64_t req_offset, uint64_t req_length, bool ensure_size) const {
        uint64_t start = req_offset - offset;
        const auto& data = data_future.get();
        if (ensure_size && start + req_length > data.size()) {
            throw std::runtime_error("requested data exceeds available buffer size");
        }
        return data.slice(start, req_length);
    }

};

class BufferedFilePool {
    FilePool file_pool;
    uint64_t buffer_size;
    uint64_t max_buffer_count;
    std::list<std::shared_ptr<BufferedFilePoolBuffer>> buffers;
    mutable std::mutex search_mutex;


public:
    BufferedFilePool(
        const std::string& path, const std::string& mode = "r", uint64_t parallel = 1,
        uint64_t bs = 65536, uint64_t mbc = 128)
        : file_pool(path, mode, parallel), buffer_size(bs), max_buffer_count(mbc) {}

    std::future<int64_t> get_file_size() {
        return file_pool.get_file_size();
    }

    std::future<ByteArray> read(int64_t size, int64_t offset, bool ensure_size = true) {
        if (size < 0 || offset < 0) throw std::runtime_error("size and offset must be specified");
        std::shared_ptr<BufferedFilePoolBuffer> buffer;
        std::unique_lock<std::mutex> search_lock(search_mutex);
        for (auto it = buffers.begin(); it != buffers.end(); ++it) {
            if ((*it)->contains(offset, size)) {
                buffer = *it;
                buffers.erase(it);
                buffers.push_front(buffer);
                search_lock.unlock();
                break;
            }
        }
        if (!buffer) {
            while (buffers.size() >= max_buffer_count) {
                buffers.pop_back();
            }
            int64_t req_start = (offset / buffer_size) * buffer_size;
            int64_t req_length = buffer_size;
            if (req_start + req_length < offset + size) {
                req_length = ((offset + size - req_start + buffer_size - 1) / buffer_size) * buffer_size;
            }
            buffer = std::make_shared<BufferedFilePoolBuffer>(req_start, req_length);
            buffers.push_front(buffer);
            search_lock.unlock();
            auto read_future = file_pool.read(req_length, req_start);
            (void)std::async(std::launch::async, [buffer, read_future = std::move(read_future)]() mutable {
                try {
                    auto data = read_future.get();
                    ByteArray byte_array(std::move(data));
                    buffer->data_promise.set_value(std::move(byte_array));
                } catch (...) {
                    buffer->data_promise.set_exception(std::current_exception());
                }
            });
        }
        return std::async(std::launch::deferred, [buffer, offset, size, ensure_size]() {
            return buffer->extract(offset, size, ensure_size);
        });
    }

    std::future<void> write(const std::vector<uint8_t>& data, int64_t offset) {
        return file_pool.write(data, offset);
    }

};


class TemporaryDirectory {
private:
    std::string path;
    bool cleanup_on_destroy = true;
    
    std::string find_random_suffix() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 15);
        std::string hex_chars = "0123456789abcdef";
        std::string random_suffix;
        for (int i = 0; i < 8; ++i) {
            random_suffix += hex_chars[dis(gen)];
        }
        return random_suffix;
    }

public:
    TemporaryDirectory(std::string parent, std::string prefix = "tmp.") {
        if (parent == "") parent = std::filesystem::temp_directory_path().string();
        path = parent + "/" + prefix + find_random_suffix();
        uint8_t counter = 0;
        while (std::filesystem::exists(path)) {
            path = parent + "/" + prefix + find_random_suffix();
            counter += 1;
            if (counter > 100) {
                throw std::runtime_error("failed to find a unique directory name in " + parent);
            }
        }
        std::error_code ec;
        if (!std::filesystem::create_directories(path, ec)) {
            throw std::runtime_error("failed to create temporary directory " +
                path + " (" + ec.message() + ")");
        }
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;
    TemporaryDirectory(TemporaryDirectory&& other) noexcept 
        : path(std::move(other.path)), cleanup_on_destroy(other.cleanup_on_destroy) {
        other.cleanup_on_destroy = false;
    }
    
    ~TemporaryDirectory() {
        if (cleanup_on_destroy) cleanup();
    }

    void cleanup() {
        if (std::filesystem::exists(path)) {
            std::error_code ec;
            std::filesystem::remove_all(path, ec);
            if (ec) {
                std::cerr << "WARNING: failed to remove temporary directory " 
                    << path << " (" << ec.message() << ")" << std::endl;
            }
        }
    }

    std::string file(const std::string& name) const {
        return path + "/" + name;
    }

};

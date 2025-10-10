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

#include <curl/curl.h>
#include "byte_util.cpp"
#include "util.cpp"

    


class File {

    struct NextLine {
        std::string line;
        bool done;
    };
    struct NextLineState {
        std::vector<uint8_t> buffer;
        uint64_t start;
        uint64_t end;
    };
    NextLineState next_line_state;

public:
    virtual ~File() = default;
    virtual std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1, int64_t min_size = -1) = 0;
    virtual void write(const std::vector<uint8_t>& data) = 0;
    virtual void write_string(const std::string& str) = 0;

    NextLine next_line() {
        while (true) {
            if (next_line_state.end >= next_line_state.buffer.size()) {
                std::vector<uint8_t> new_buffer = read(16384);
                if (new_buffer.empty()) break;
                next_line_state.buffer = std::move(
                    std::vector<uint8_t>(next_line_state.buffer.begin() + next_line_state.start, next_line_state.buffer.end())
                );
                next_line_state.start = 0;
                next_line_state.end = next_line_state.buffer.size();
                next_line_state.buffer.insert(next_line_state.buffer.end(), new_buffer.begin(), new_buffer.end());
            }
            char c = static_cast<char>(next_line_state.buffer[next_line_state.end]);
            next_line_state.end += 1;
            if (c == '\n') break;
        }
        if (next_line_state.start >= next_line_state.end) return { "", true };
        uint64_t line_end = next_line_state.end - 1;
        if (line_end > 0 && static_cast<char>(next_line_state.buffer[line_end - 1]) == '\r') line_end -= 1;
        std::string line(
            next_line_state.buffer.begin() + next_line_state.start,
            next_line_state.buffer.begin() + line_end
        );
        next_line_state.start = next_line_state.end;
        return { line, false };
    }
    
};


class LocalFile : public File {
    std::string path;
    std::string mode;
    std::unique_ptr<std::fstream> file_handle;
    mutable std::mutex file_mutex;

public:
    LocalFile(const std::string& p, const std::string& m = "r") : path(p), mode(m) {
        std::ios::openmode open_mode = std::ios::binary;
        if (mode == "r") {
            open_mode |= std::ios::in;
        } else if (mode == "w") {
            open_mode |= std::ios::out;
        } else {
            throw std::runtime_error("file open mode " + mode + " not supported");
        }
        file_handle = std::make_unique<std::fstream>(path, open_mode);
        if (!file_handle->is_open()) {
            throw std::runtime_error("failed to open file " + path);
        }
    }

    ~LocalFile() {
        if (file_handle && file_handle->is_open()) {
            file_handle->close();
        }
    }

    void seek(int64_t offset, std::ios::seekdir dir = std::ios::beg) {
        file_handle->seekg(offset, dir);
        if (file_handle->fail()) {
            throw std::runtime_error("failed to seek to " + std::to_string(offset) + " in file " + path);
        }
    }

    uint64_t get_file_size() {
        std::lock_guard<std::mutex> lock(file_mutex);
        auto current_pos = file_handle->tellg();
        seek(0, std::ios::end);
        auto size = file_handle->tellg();
        seek(current_pos);
        if (size < 0) throw std::runtime_error("error determining size of file " + path);
        return static_cast<uint64_t>(size);
    }

    std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1, int64_t min_size = -1) override {
        if (size < 0) size = get_file_size();
        std::lock_guard<std::mutex> lock(file_mutex);
        if (offset >= 0) seek(offset);
        std::vector<uint8_t> buffer(size);
        if (size == 0) return buffer;

        file_handle->read(reinterpret_cast<char*>(buffer.data()), size);
        std::streamsize bytes_read = file_handle->gcount();
        if (file_handle->bad() || (file_handle->fail() && !file_handle->eof())) {
            throw std::runtime_error("error reading file " + path + " (" + std::string(strerror(errno)) + ")");
        }
        if (static_cast<int64_t>(bytes_read) != size) {
            if (min_size >= 0 && static_cast<int64_t>(bytes_read) < min_size) {
                throw std::runtime_error("error reading file " + path + " (end of file reached)");
            } else {
                buffer.resize(bytes_read);
            }
        }

        return buffer;
    }

    void write(const std::vector<uint8_t>& data) override {
        std::lock_guard<std::mutex> lock(file_mutex);
        file_handle->write(reinterpret_cast<const char*>(data.data()), data.size());
        if (file_handle->bad() || file_handle->fail()) {
            throw std::runtime_error("failed to write " + std::to_string(data.size()) + " bytes to file " + path + " (" + std::string(strerror(errno)) + ")");
        }
    }

    void write_string(const std::string& str) override {
        std::vector<uint8_t> data(str.begin(), str.end());
        write(data);
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
    std::mutex mutex_;
    int ref_count_;
    
    CurlGlobalManager() : ref_count_(0) {}
    
public:
    CurlGlobalManager(const CurlGlobalManager&) = delete;
    CurlGlobalManager& operator=(const CurlGlobalManager&) = delete;
    
    static CurlGlobalManager& getInstance() {
        static CurlGlobalManager instance;
        return instance;
    }
    
    void initialize() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (ref_count_ == 0) curl_global_init(CURL_GLOBAL_DEFAULT);
        ref_count_++;
    }
    
    void cleanup() {
        std::lock_guard<std::mutex> lock(mutex_);
        ref_count_--;
        if (ref_count_ == 0) curl_global_cleanup();
    }
    
    ~CurlGlobalManager() {
        if (ref_count_ > 0)curl_global_cleanup();
    }
};

class UrlFile : public File {
    std::string path;
    std::string mode;
    mutable std::mutex curl_mutex;
    CURL* curl_handle;
    
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
    }
    
    ~UrlFile() {
        if (curl_handle) {
            curl_easy_cleanup(curl_handle);
        }
        CurlGlobalManager::getInstance().cleanup();
    }
    
    uint64_t get_file_size() {
        std::lock_guard<std::mutex> lock(curl_mutex);

        if (!curl_handle) {
            throw std::runtime_error("curl_handle is not initialized");
        }

        double file_size = 0.0;
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 1L);
        curl_easy_setopt(curl_handle, CURLOPT_HEADER, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 1L);
        
        CURLcode res = curl_easy_perform(curl_handle);
        if (res != CURLE_OK) {
            throw std::runtime_error("error determining size of " + path + " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")");
        }
        
        res = curl_easy_getinfo(curl_handle, CURLINFO_CONTENT_LENGTH_DOWNLOAD, &file_size);
        if (res != CURLE_OK || file_size < 0) {
            throw std::runtime_error("error determining size of " + path + " (could not get content length)");
        }
        
        // Reset curl options for future requests
        curl_easy_setopt(curl_handle, CURLOPT_NOBODY, 0L);
        curl_easy_setopt(curl_handle, CURLOPT_FILETIME, 0L);
        
        return static_cast<uint64_t>(file_size);
    }

    std::vector<uint8_t> read(int64_t size = -1, int64_t offset = -1, int64_t min_size = -1) override {
        if (size < 0 && offset < 0) return read_all();
        if (size < 0) throw std::runtime_error("size must be specified when offset is specified");
        std::lock_guard<std::mutex> lock(curl_mutex);

        if (!curl_handle) {
            throw std::runtime_error("curl_handle is not initialized");
        }

        std::vector<uint8_t> buffer(size);
        
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
        
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        
        // Clean up headers
        curl_slist_free_all(headers);
        
        if (res != CURLE_OK) {
            throw std::runtime_error("error reading " + path + " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")");
        }
        
        // Check response code and amount of data
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 206 && response_code != 200) { // 206 = Partial Content, 200 = OK
            throw std::runtime_error("error reading " + path + " (http request failed with code " + std::to_string(response_code) + ")");
        } else if (static_cast<int64_t>(buffer.size()) != size) {
            if (min_size >= 0 && static_cast<int64_t>(buffer.size()) < min_size) {
                throw std::runtime_error("error reading " + path + " (incomplete read)");
            } else if (static_cast<int64_t>(buffer.size()) > size) {
                buffer.resize(size);
            }
        }
        
        return buffer;
    }

    std::vector<uint8_t> read_all() {
        std::lock_guard<std::mutex> lock(curl_mutex);

        if (!curl_handle) {
            throw std::runtime_error("curl_handle is not initialized");
        }

        std::vector<uint8_t> buffer;
        
        CurlWriteData write_data;
        write_data.buffer = &buffer;
        write_data.expected_size = 0; // Not used for full read
        
        // Configure curl for this request
        curl_easy_setopt(curl_handle, CURLOPT_HTTPHEADER, nullptr); // No range header
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, custom_curl_write_callback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, &write_data);
        
        // Perform the request
        CURLcode res = curl_easy_perform(curl_handle);
        
        if (res != CURLE_OK) {
            throw std::runtime_error("error reading " + path + " (curl request failed: " + std::string(curl_easy_strerror(res)) + ")");
        }
        
        // Check response code
        long response_code;
        curl_easy_getinfo(curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
        if (response_code != 200) { // 200 = OK
            throw std::runtime_error("error reading " + path + " (http request failed with code " + std::to_string(response_code) + ")");
        }
        
        return buffer;
    }

    void write(const std::vector<uint8_t>& /* data */) override {
        throw std::runtime_error("writing to url not supported");
    }

    void write_string(const std::string& /* str */) override {
        throw std::runtime_error("writing to url not supported");
    }

};


struct BufferedFileBuffer {
    int64_t offset;
    uint64_t length;
    std::promise<ByteArray> data_promise;
    std::shared_future<ByteArray> data_future;

    BufferedFileBuffer(int64_t o, uint64_t l)
        : offset(o), length(l) {
        data_promise = std::promise<ByteArray>();
        data_future = data_promise.get_future().share();
    }

    bool contains(int64_t req_offset, uint64_t req_length) const {
        return req_offset >= offset && req_offset + req_length <= offset + length;
    }

    ByteArray extract(int64_t req_offset, uint64_t req_length) const {
        int64_t start = req_offset - offset;
        const auto& data = data_future.get();
        return data.slice(start, req_length).data;
    }
};

class BufferedFile {
    std::shared_ptr<File> file;
    std::deque<std::shared_ptr<BufferedFileBuffer>> buffers;
    uint64_t max_buffers;
    uint64_t buffer_size;
    mutable std::mutex search_mutex;
    mutable Semaphore file_semaphore;

public:
    BufferedFile(const std::shared_ptr<File>& f, uint64_t mb = 100, uint64_t bs = 65536) 
        : file(f), max_buffers(mb), buffer_size(bs), file_semaphore(12) {}

    ByteArray read(uint64_t size, int64_t offset, int64_t min_size = -1) {
        std::unique_lock<std::mutex> search_lock(search_mutex);
        for (auto it = buffers.begin(); it != buffers.end(); ++it) {
            if ((*it)->contains(offset, size)) {
                auto buffer = *it;
                buffers.erase(it);
                buffers.push_front(buffer);
                search_lock.unlock();
                return buffer->extract(offset, size);
            }
        }
        while (buffers.size() >= max_buffers) {
            buffers.pop_back();
        }
        uint64_t read_size = std::max(size, buffer_size);
        int64_t read_min_size = (min_size >= 0) ? min_size : size;
        auto buffer = std::make_shared<BufferedFileBuffer>(offset, read_min_size);
        buffers.push_front(buffer);
        search_lock.unlock();
        try {
            SemaphoreGuard guard(file_semaphore);
            ByteArray data(file->read(read_size, offset, read_min_size));
            buffer->data_promise.set_value(std::move(data));
        } catch (...) {
            buffer->data_promise.set_exception(std::current_exception());
        }
        return buffer->data_future.get();
    }

};


std::shared_ptr<File> open_file(const std::string& path, const std::string& mode) {
    if (path.substr(0, 7) == "http://" || path.substr(0, 8) == "https://" || path.substr(0, 6) == "ftp://") {
        return std::make_shared<UrlFile>(path, mode);
    } else {
        return std::make_shared<LocalFile>(path, mode);
    }
}


std::map<std::string, std::vector<std::string>> read_tsv(const std::string& path) {
    auto file = open_file(path, "r");
    std::map<std::string, std::vector<std::string>> result;
    
    // Read the entire file
    const size_t chunk_size = 8192;
    std::vector<uint8_t> file_data;
    int64_t offset = 0;
    
    while (true) {
        auto chunk = file->read(chunk_size, offset);
        if (chunk.empty()) break;
        file_data.insert(file_data.end(), chunk.begin(), chunk.end());
        offset += chunk.size();
        if (chunk.size() < chunk_size) break; // End of file
    }
    
    // Convert to string
    std::string content(file_data.begin(), file_data.end());
    std::istringstream stream(content);
    std::string line;
    std::vector<std::string> headers;
    
    // Read header line
    if (std::getline(stream, line)) {
        std::stringstream ss(line);
        std::string header;
        
        while (std::getline(ss, header, '\t')) {
            headers.push_back(header);
            result[header] = std::vector<std::string>();
        }
    } else {
        throw std::runtime_error("file is empty or cannot read header line");
    }
    
    // Read data lines
    while (std::getline(stream, line)) {
        std::stringstream ss(line);
        std::string value;
        size_t col_index = 0;
        
        while (std::getline(ss, value, '\t') && col_index < headers.size()) {
            result[headers[col_index]].push_back(value);
            col_index++;
        }
        
        // Fill missing columns with empty strings if line has fewer columns
        while (col_index < headers.size()) {
            result[headers[col_index]].push_back("");
            col_index++;
        }
    }
    
    return result;
}


class DataFrame {
    std::map<std::string, std::vector<std::string>> string_columns;
    std::map<std::string, std::vector<int64_t>> int_columns;
    std::map<std::string, std::vector<uint64_t>> uint_columns;
    std::map<std::string, std::vector<double>> double_columns;
    std::map<std::string, std::vector<bool>> bool_columns;
    
    int64_t parse_int64(const std::string& value) const {
        if (value.empty()) return 0;
        return std::stoll(value);
    }
    uint64_t parse_uint64(const std::string& value) const {
        if (value.empty()) return 0;
        return std::stoull(value);
    }
    double parse_double(const std::string& value) const {
        if (value.empty()) return 0.0;
        return std::stod(value);
    }
    bool parse_bool(const std::string& value) const {
        if (value.empty()) return false;
        std::string lower_val = value;
        std::transform(lower_val.begin(), lower_val.end(), lower_val.begin(), ::tolower);
        if (lower_val == "true" || lower_val == "1" || lower_val == "yes") return true;
        if (lower_val == "false" || lower_val == "0" || lower_val == "no") return false;
        throw std::runtime_error("cannot parse boolean value: " + value);
    }
    
public:
    DataFrame(const std::map<std::string, std::vector<std::string>>& columns)
        : string_columns(columns) {}
    
    void set_types(const std::map<std::string, std::string>& types) {
        for (const auto& pair : types) {
            const std::string& key = pair.first;
            const std::string& type = pair.second;
            
            auto col_it = string_columns.find(key);
            if (col_it == string_columns.end()) {
                throw std::runtime_error("column " + key + " not found");
            }
            
            const std::vector<std::string>& column = col_it->second;
            
            if (type == "int64") {
                int_columns[key].clear();
                for (const auto& value : column) {
                    int_columns[key].push_back(parse_int64(value));
                }
            } else if (type == "uint64") {
                uint_columns[key].clear();
                for (const auto& value : column) {
                    uint_columns[key].push_back(parse_uint64(value));
                }
            } else if (type == "double") {
                double_columns[key].clear();
                for (const auto& value : column) {
                    double_columns[key].push_back(parse_double(value));
                }
            } else if (type == "bool") {
                bool_columns[key].clear();
                for (const auto& value : column) {
                    bool_columns[key].push_back(parse_bool(value));
                }
            } else if (type != "string") {
                throw std::runtime_error("column type " + type + " not supported");
            }
        }
    }

    const std::vector<std::string>& get_string_column(const std::string& name) const {
        return string_columns.at(name);
    }
    
    const std::vector<int64_t>& get_int_column(const std::string& name) const {
        return int_columns.at(name);
    }
    
    const std::vector<uint64_t>& get_uint_column(const std::string& name) const {
        return uint_columns.at(name);
    }
    
    const std::vector<double>& get_double_column(const std::string& name) const {
        return double_columns.at(name);
    }
    
    const std::vector<bool>& get_bool_column(const std::string& name) const {
        return bool_columns.at(name);
    }

    void print_summary() const {
        std::cout << "DataFrame Summary:" << std::endl;
        std::cout << "String columns: ";
        for (const auto& pair : string_columns) {
            std::cout << pair.first << " (" << pair.second.size() << " rows), ";
        }
        std::cout << std::endl;
        std::cout << "Int64 columns: ";
        for (const auto& pair : int_columns) {
            std::cout << pair.first << " (" << pair.second.size() << " rows), ";
        }
        std::cout << std::endl;
        std::cout << "UInt64 columns: ";
        for (const auto& pair : uint_columns) {
            std::cout << pair.first << " (" << pair.second.size() << " rows), ";
        }
        std::cout << std::endl;
        std::cout << "Double columns: ";
        for (const auto& pair : double_columns) {
            std::cout << pair.first << " (" << pair.second.size() << " rows), ";
        }
        std::cout << std::endl;
        std::cout << "Bool columns: ";
        for (const auto& pair : bool_columns) {
            std::cout << pair.first << " (" << pair.second.size() << " rows), ";
        }
        std::cout << std::endl;
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

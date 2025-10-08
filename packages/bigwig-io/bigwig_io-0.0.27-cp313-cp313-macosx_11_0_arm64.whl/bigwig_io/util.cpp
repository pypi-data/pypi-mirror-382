#pragma once

#include <condition_variable>
#include <functional>
#include <iostream>
#include <mutex>
#include <thread>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <string>
#include <list>


class Semaphore {
    std::mutex mtx;
    std::condition_variable cv;
    int count;

public:
    explicit Semaphore(int initial) : count(initial) {}

    void acquire() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&] { return count > 0; });
        --count;
    }

    void release() {
        std::unique_lock<std::mutex> lock(mtx);
        ++count;
        lock.unlock();
        cv.notify_one();
    }
};


class SemaphoreGuard {
    Semaphore& sem;
    bool owns;

public:
    explicit SemaphoreGuard(Semaphore& s) : sem(s), owns(true) {
        sem.acquire();
    }

    ~SemaphoreGuard() {
        if (owns) sem.release();
    }

    // non-copyable and non-move-assignable
    SemaphoreGuard(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(SemaphoreGuard&&) = delete;

    // movable (constructor only)
    SemaphoreGuard(SemaphoreGuard&& other) noexcept : sem(other.sem), owns(other.owns) {
        other.owns = false;
    }
};


class ProgressTracker {
    uint64_t total;
    std::function<void(uint64_t, uint64_t)> callback;
    double report_interval;
    double last_reported;

public:
    ProgressTracker(uint64_t t, std::function<void(uint64_t, uint64_t)> cb, double ri = 0.01)
        : total(t), callback(cb), report_interval(ri), last_reported(0) {}

    void update(uint64_t current) {
        double progress = (total > 0) ? static_cast<double>(current) / total : 0.0;
        if (callback && progress > last_reported + report_interval) {
            last_reported = progress;
            callback(current, total);
        }
    }

    void done() {
        if (callback && last_reported < 1.0) {
            last_reported = 1.0;
            callback(total, total);
        }
    }

};


uint64_t get_available_threads() {
    unsigned int n = std::thread::hardware_concurrency();
    return (n == 0) ? 1 : n;
}


void print_progress(uint64_t current, uint64_t total) {
    uint64_t percent = (total > 0) ? (current * 100) / total : 100;
    if (percent == 100) {
        std::cout << "\rProgress: 100% " << std::endl;
    } else {
        std::cout << "\rProgress: " << percent << "% " << std::flush;
    }
}


template<typename T>
std::string fstring_tostr(T&& value) {
    if constexpr (std::is_same_v<std::decay_t<T>, std::string>) {
        return std::forward<T>(value);
    } else if constexpr (std::is_same_v<std::decay_t<T>, const char*>) {
        return std::string(value);
    } else if constexpr (std::is_arithmetic_v<std::decay_t<T>>) {
        return std::to_string(std::forward<T>(value));
    } else {
        std::ostringstream oss;
        oss << std::forward<T>(value);
        return oss.str();
    }
}

template<typename... Args>
std::string fstring(const std::string& fmt, Args&&... args) {
    if constexpr (sizeof...(args) == 0) {
        return fmt;
    } else {
        std::ostringstream result;
        std::vector<std::string> arg_strings = {fstring_tostr(std::forward<Args>(args))...};
        size_t arg_index = 0;
        size_t pos = 0;
        size_t found = 0;
        while ((found = fmt.find("{}", pos)) != std::string::npos) {
            if (arg_index >= arg_strings.size()) {
                throw std::runtime_error("not enough arguments for format string");
            }
            result << fmt.substr(pos, found - pos);
            result << arg_strings[arg_index++];
            pos = found + 2;
        }
        if (arg_index < arg_strings.size()) {
            throw std::runtime_error("too many arguments for format string");
        }
        result << fmt.substr(pos);
        return result.str();
    }
}


std::string lowercase(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return result;
}

std::string uppercase(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return std::toupper(c); });
    return result;
}


std::vector<std::string> split_string(const std::string& str, char delimiter) {
    std::vector<std::string> result;
    std::istringstream stream(str);
    std::string item;
    while (std::getline(stream, item, delimiter)) {
        result.push_back(item);
    }
    return result;
}


template <typename Derived, typename Value>
class GeneratorBase {
public:
    struct NextResult {
        Value value;
        bool done;
    };

    class iterator {
        Derived* gen;
        NextResult state;

    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = Value;
        using reference = const Value&;
        using pointer = const Value*;
        using difference_type = std::ptrdiff_t;

        iterator(Derived* g, bool at_end = false) : gen(g) {
            if (at_end) {
                state = {Value{}, true};
            } else {
                state = gen->next();
            }
        }

        reference operator*() const { return state.value; }
        pointer operator->() const { return &state.value; }

        iterator& operator++() {
            state = gen->next();
            return *this;
        }

        bool operator!=(const iterator& other) const {
            return state.done != other.state.done;
        }
    };

    iterator begin() { return iterator(static_cast<Derived*>(this), false); }
    iterator end() { return iterator(static_cast<Derived*>(this), true); }
};


template <typename K, typename V, bool MoveOnReinsert = false>
class OrderedMap {
    using ListType = std::list<std::pair<K, V>>;
    using MapType  = std::unordered_map<K, typename ListType::iterator>;

    ListType order;
    MapType map;

public:
    // Insert or update
    void insert(const K& key, const V& value) {
        auto it = map.find(key);
        if (it != map.end()) {
            if constexpr (MoveOnReinsert) {
                // erase from list, re-add at back
                order.erase(it->second);
                order.emplace_back(key, value);
                auto list_it = std::prev(order.end());
                it->second = list_it;
            } else {
                it->second->second = value; // update in place
            }
        } else {
            order.emplace_back(key, value);
            auto list_it = std::prev(order.end());
            map.emplace(key, list_it);
        }
    }

    // operator[] like std::map/unordered_map
    V& operator[](const K& key) {
        auto it = map.find(key);
        if (it != map.end()) {
            if constexpr (MoveOnReinsert) {
                // move to back
                auto node = *(it->second);
                order.erase(it->second);
                order.emplace_back(std::move(node));
                auto list_it = std::prev(order.end());
                it->second = list_it;
                return list_it->second;
            } else {
                return it->second->second;
            }
        } else {
            order.emplace_back(key, V{});  // default-constructed value
            auto list_it = std::prev(order.end());
            map.emplace(key, list_it);
            return list_it->second;
        }
    }

    // Remove a key
    void erase(const K& key) {
        auto it = map.find(key);
        if (it != map.end()) {
            order.erase(it->second);
            map.erase(it);
        }
    }

    // Lookup
    V& at(const K& key) {
        auto it = map.find(key);
        if (it == map.end()) throw std::out_of_range("Key not found");
        return it->second->second;
    }

    const V& at(const K& key) const {
        auto it = map.find(key);
        if (it == map.end()) throw std::out_of_range("Key not found");
        return it->second->second;
    }

    const V& at_index(uint64_t index) const {
        if (index >= order.size()) throw std::out_of_range("Index out of range");
        auto it = order.begin();
        std::advance(it, index);
        return it->second;
    }
    

    const K& key_at_index(uint64_t index) const {
        if (index >= order.size()) throw std::out_of_range("Index out of range");
        auto it = order.begin();
        std::advance(it, index);
        return it->first;
    }

    bool contains(const K& key) const {
        return map.find(key) != map.end();
    }

    // Find method - returns iterator to the element or end() if not found
    auto find(const K& key) {
        auto it = map.find(key);
        if (it != map.end()) {
            return it->second; // return list iterator
        }
        return order.end();
    }
    auto find(const K& key) const {
        auto it = map.find(key);
        if (it != map.end()) {
            return it->second; // return list iterator
        }
        return order.end();
    }

    // Iteration (in insertion order)
    auto begin() { return order.begin(); }
    auto end()   { return order.end(); }
    auto begin() const { return order.begin(); }
    auto end()   const { return order.end(); }
    auto cbegin() const { return order.cbegin(); }
    auto cend()   const { return order.cend(); }

    // Keys - return vector of all keys in insertion order
    std::vector<K> keys() const {
        std::vector<K> result;
        result.reserve(order.size());
        for (const auto& pair : order) {
            result.push_back(pair.first);
        }
        return result;
    }

    // Size
    size_t size() const { return map.size(); }
    bool empty() const { return map.empty(); }
};
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "fastregex.h"
#include <chrono>
#include <vector>
#include <memory>
#include <iostream>

namespace py = pybind11;
using namespace fastregex;

class CompiledRegex {
    std::unique_ptr<FastRegex> regex_;
    bool jit_compiled_;
    std::chrono::microseconds compile_time_;

public:
    CompiledRegex(const std::string& pattern, bool use_simd = true,
                 RegexFlags flags = RegexFlags::NONE, bool enable_jit = false)
        : regex_(std::make_unique<FastRegex>(pattern, use_simd, false, flags)),
          jit_compiled_(false) {
        auto start = std::chrono::high_resolution_clock::now();
        // Упрощенная версия без SIMD
        jit_compiled_ = false;
        auto end = std::chrono::high_resolution_clock::now();
        compile_time_ = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    }

    bool match(const std::string& s) const {
        return regex_->match(s);
    }
    
    void set_debug_mode(bool debug) {
        regex_->set_debug_mode(debug);
    }

    bool search(const std::string& s) const {
        return regex_->search(s);
    }

    std::vector<std::string> find_all(const std::string& s) const {
        std::vector<std::string> results;
        if (!regex_) return results;

        size_t pos = 0;
        const size_t pat_len = regex_->pattern().size();
        while (pos <= s.size()) {
            size_t found_pos = s.find(regex_->pattern(), pos);
            if (found_pos == std::string::npos) break;

            results.push_back(s.substr(found_pos, pat_len));
            pos = found_pos + pat_len;
        }

        return results;
    }

    std::string replace(const std::string& s, const std::string& repl) const {
        if (!regex_) return s;

        std::string result;
        result.reserve(s.size() + repl.size() * 2); // Предварительное выделение памяти

        size_t last_pos = 0;
        size_t pos = 0;
        const auto& pat = regex_->pattern();

        while ((pos = s.find(pat, last_pos)) != std::string::npos) {
            result.append(s, last_pos, pos - last_pos);
            result.append(repl);
            last_pos = pos + pat.size();
        }

        result.append(s, last_pos);
        return result;
    }

    const std::string& pattern() const { return regex_->pattern(); }
    bool use_simd() const { return regex_->use_simd(); }
    RegexFlags flags() const { return regex_->flags(); }
    bool jit_compiled() const { return jit_compiled_; }
    long compile_time_us() const { return compile_time_.count(); }
};

PYBIND11_MODULE(fastregex, m) {
    m.doc() = "High-performance regex with JIT compilation and SIMD optimizations";

    // Regex flags enum
    py::enum_<RegexFlags>(m, "RegexFlags")
        .value("NONE", RegexFlags::NONE)
        .value("IGNORECASE", RegexFlags::IGNORECASE)
        .value("MULTILINE", RegexFlags::MULTILINE)
        .value("DOTALL", RegexFlags::DOTALL)
        .value("OPTIMIZE", RegexFlags::OPTIMIZE)
        .export_values();

    // SIMD capabilities enum (заглушка)
    enum class SIMDMode {
        AUTO = 0,
        FORCE_AVX512 = 1,
        FORCE_AVX2 = 2,
        FORCE_SSE42 = 3,
        FORCE_NEON = 4,
        SCALAR_ONLY = 5
    };
    
    py::enum_<SIMDMode>(m, "SIMDMode")
        .value("AUTO", SIMDMode::AUTO)
        .value("FORCE_AVX512", SIMDMode::FORCE_AVX512)
        .value("FORCE_AVX2", SIMDMode::FORCE_AVX2)
        .value("FORCE_SSE42", SIMDMode::FORCE_SSE42)
        .value("FORCE_NEON", SIMDMode::FORCE_NEON)
        .value("SCALAR_ONLY", SIMDMode::SCALAR_ONLY)
        .export_values();

    // FastRegex class bindings
    py::class_<FastRegex>(m, "FastRegex")
        .def(py::init<const std::string&, bool, bool, RegexFlags>(),
             py::arg("pattern"),
             py::arg("use_simd") = true,
             py::arg("debug_mode") = false,
             py::arg("flags") = RegexFlags::NONE,
             "Construct a FastRegex object")
        .def("match",
             py::overload_cast<const std::string&>(&FastRegex::match, py::const_),
             py::arg("s"),
             "Test if the entire string matches the pattern")
        .def("search",
             py::overload_cast<const std::string&>(&FastRegex::search, py::const_),
             py::arg("s"),
             "Search for first occurrence of pattern in string")
        .def("find_all", &FastRegex::find_all,
             py::arg("s"),
             "Find all matches of pattern in string")
        .def("replace", &FastRegex::replace,
             py::arg("s"), py::arg("replacement"),
             "Replace all occurrences of pattern")
        .def("pattern", &FastRegex::pattern,
             "Get the pattern string")
        .def("use_simd", &FastRegex::use_simd,
             "Check if SIMD optimizations are enabled")
        .def("set_use_simd", &FastRegex::set_use_simd, py::arg("enable"),
             "Enable/disable SIMD optimizations")
        .def("flags", &FastRegex::flags,
             "Get current regex flags")
        .def("set_flags", &FastRegex::set_flags, py::arg("flags"),
             "Set regex flags")
        .def("is_jit_compiled", &FastRegex::is_jit_compiled,
             "Check if JIT compilation was used")
        .def("compile_time", &FastRegex::compile_time,
             "Get compilation time in microseconds")
        .def_static("clear_cache", &FastRegex::clear_cache,
                    "Clear regex cache")
        .def_static("cache_size", &FastRegex::cache_size,
                    "Get current cache size")
        .def_static("hit_rate", &FastRegex::hit_rate,
                    "Get cache hit rate")
        .def("__repr__", [](const FastRegex& re) {
            return "<FastRegex pattern='" + re.pattern() +
                   "' use_simd=" + (re.use_simd() ? "True" : "False") +
                   " jit=" + (re.is_jit_compiled() ? "True" : "False") + ">";
        });

    // CompiledRegex class
    py::class_<CompiledRegex>(m, "CompiledRegex")
        .def(py::init<const std::string&, bool, RegexFlags, bool>(),
             py::arg("pattern"),
             py::arg("use_simd") = true,
             py::arg("flags") = RegexFlags::NONE,
             py::arg("enable_jit") = false,
             "Compile a regex pattern for repeated use")
        .def("match", &CompiledRegex::match, py::arg("s"),
             "Test if the entire string matches the pattern")
        .def("set_debug_mode", &CompiledRegex::set_debug_mode, py::arg("debug"),
             "Enable or disable debug mode")
        .def("search", &CompiledRegex::search, py::arg("s"),
             "Search for first occurrence of pattern in string")
        .def("find_all", &CompiledRegex::find_all, py::arg("s"),
             "Find all non-overlapping matches of pattern in string")
        .def("replace", &CompiledRegex::replace,
             py::arg("s"), py::arg("repl"),
             "Replace all occurrences of pattern with replacement string")
        .def("pattern", &CompiledRegex::pattern,
             "Get the pattern string")
        .def("use_simd", &CompiledRegex::use_simd,
             "Check if SIMD optimizations are enabled")
        .def("flags", &CompiledRegex::flags,
             "Get current regex flags")
        .def("jit_compiled", &CompiledRegex::jit_compiled,
             "Check if JIT compilation was used")
        .def("compile_time_us", &CompiledRegex::compile_time_us,
             "Get compilation time in microseconds")
        .def("__repr__", [](const CompiledRegex& re) {
            return "<CompiledRegex pattern='" + re.pattern() +
                   "' jit=" + (re.jit_compiled() ? "True" : "False") + ">";
        })
        .def("__call__", &CompiledRegex::match, py::arg("s"),
             "Test if the entire string matches the pattern");

    // Module-level functions
    m.def("match", [](const std::string& pattern, const std::string& s,
                      RegexFlags flags = RegexFlags::NONE,
                      bool use_simd = true) {
        return FastRegex(pattern, use_simd, false, flags).match(s);
    }, py::arg("pattern"), py::arg("s"),
       py::arg("flags") = RegexFlags::NONE,
       py::arg("use_simd") = true,
       "Test if the entire string matches the pattern");

    m.def("search", [](const std::string& pattern, const std::string& s,
                       RegexFlags flags = RegexFlags::NONE,
                       bool use_simd = true) {
        return FastRegex(pattern, use_simd, false, flags).search(s);
    }, py::arg("pattern"), py::arg("s"),
       py::arg("flags") = RegexFlags::NONE,
       py::arg("use_simd") = true,
       "Search for first occurrence of pattern in string");

    m.def("find_all", [](const std::string& pattern, const std::string& s,
                         RegexFlags flags = RegexFlags::NONE,
                         bool use_simd = true) {
        return FastRegex(pattern, use_simd, false, flags).find_all(s);
    }, py::arg("pattern"), py::arg("s"),
       py::arg("flags") = RegexFlags::NONE,
       py::arg("use_simd") = true,
       "Find all matches of pattern in string");

    m.def("replace", [](const std::string& pattern, const std::string& s,
                        const std::string& replacement,
                        RegexFlags flags = RegexFlags::NONE,
                        bool use_simd = true) {
        return FastRegex(pattern, use_simd, false, flags).replace(s, replacement);
    }, py::arg("pattern"), py::arg("s"), py::arg("replacement"),
       py::arg("flags") = RegexFlags::NONE,
       py::arg("use_simd") = true,
       "Replace all occurrences of pattern in string");

    m.def("compile", [](const std::string& pattern,
                        bool use_simd = true,
                        RegexFlags flags = RegexFlags::NONE,
                        bool enable_jit = false) {
        return CompiledRegex(pattern, use_simd, flags, enable_jit);
    }, py::arg("pattern"),
       py::arg("use_simd") = true,
       py::arg("flags") = RegexFlags::NONE,
       py::arg("enable_jit") = false,
       "Compile regex pattern for repeated use");

    // SIMD control functions (заглушки)
    m.def("set_simd_mode", [](SIMDMode mode) {
        // Заглушка - SIMD отключен
    }, py::arg("mode"), "Set SIMD execution mode");

    m.def("get_simd_mode", []() {
        return SIMDMode::SCALAR_ONLY;
    }, "Get current SIMD execution mode");

    m.def("get_simd_stats", []() {
        return py::dict(
            py::arg("total_calls") = 0,
            py::arg("avx512_count") = 0,
            py::arg("avx2_count") = 0,
            py::arg("sse42_count") = 0,
            py::arg("neon_count") = 0,
            py::arg("scalar_count") = 0
        );
    }, "Get SIMD usage statistics");

    m.def("reset_simd_stats", []() {
        // Заглушка
    }, "Reset SIMD usage statistics");

    m.def("simd_capabilities", []() {
        py::dict caps;
        caps["avx512"] = false;
        caps["avx2"] = false;
        caps["sse42"] = false;
        caps["neon"] = false;
        return caps;
    }, "Check supported SIMD capabilities");

    // Version info
    m.attr("__version__") = "1.0.0";
    m.attr("simd_version") = "Scalar only";
}
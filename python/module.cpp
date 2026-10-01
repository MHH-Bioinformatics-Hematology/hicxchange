// hic2cool._hicxchange: the C++ converters for the Python package. Messages go
// through the sys.stdout, sys.stderr and input() current at the time of the
// call, so that code redirecting them captures the output as with the pure
// Python hic2cool. The work runs without the GIL.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <hicfilecpp/errors.hpp>

#include "hicxchange/hicxchange.hpp"

namespace py = pybind11;

namespace {

hicxchange::Console python_console() {
    hicxchange::Console console;
    console.out = [](const std::string& line) {
        py::gil_scoped_acquire gil;
        py::module_::import("builtins").attr("print")(py::str(line));
    };
    console.err = [](const std::string& line) {
        py::gil_scoped_acquire gil;
        py::module_ sys = py::module_::import("sys");
        py::module_::import("builtins").attr("print")(py::str(line), py::arg("file") = sys.attr("stderr"));
    };
    console.input = [](const std::string& prompt) {
        py::gil_scoped_acquire gil;
        return py::module_::import("builtins").attr("input")(py::str(prompt)).cast<std::string>();
    };
    return console;
}

}  // namespace

PYBIND11_MODULE(_hicxchange, m) {
    m.doc() = "C++ implementation of hic2cool and cool2hic";
    m.attr("__version__") = hicxchange::kVersion;

    static py::exception<hicxchange::ExitError> exit_error(m, "ExitError", PyExc_RuntimeError);
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) {
                std::rethrow_exception(p);
            }
        } catch (const hicxchange::ExitError& e) {
            py::set_error(exit_error, e.what());
        } catch (const hicfilecpp::HicError& e) {
            py::set_error(exit_error, (std::string("!!! ERROR. ") + e.what()).c_str());
        }
    });

    m.def("available_threads", &hicxchange::available_threads);

    m.def(
        "convert",
        [](const std::string& infile, const std::string& outfile, std::int64_t resolution, int nproc,
           bool show_warnings, bool silent, const std::string& storage_mode) {
            const auto console = python_console();
            py::gil_scoped_release release;
            return hicxchange::hic2cool_convert(infile, outfile, resolution, nproc, show_warnings, silent, storage_mode,
                                              console);
        },
        py::arg("infile"), py::arg("outfile"), py::arg("resolution") = 0, py::arg("nproc") = 0,
        py::arg("show_warnings") = false, py::arg("silent") = false, py::arg("storage_mode") = "symmetric-upper");

    m.def(
        "extract_norms",
        [](const std::string& infile, const std::string& outfile, bool exclude_mt, bool show_warnings, bool silent) {
            const auto console = python_console();
            py::gil_scoped_release release;
            hicxchange::hic2cool_extractnorms(infile, outfile, exclude_mt, show_warnings, silent, console);
        },
        py::arg("infile"), py::arg("outfile"), py::arg("exclude_mt") = false, py::arg("show_warnings") = false,
        py::arg("silent") = false);

    m.def(
        "update",
        [](const std::string& infile, const std::string& outfile, bool show_warnings, bool silent) {
            const auto console = python_console();
            py::gil_scoped_release release;
            hicxchange::hic2cool_update(infile, outfile, show_warnings, silent, console);
        },
        py::arg("infile"), py::arg("outfile") = "", py::arg("show_warnings") = false, py::arg("silent") = false);

    m.def(
        "cool2hic",
        [](const std::string& infile, const std::string& outfile, std::int64_t resolution,
           const std::vector<std::int64_t>& add_resolutions, int nproc, int hic_version,
           const std::string& normalizations, std::optional<std::string> cooler_weight, const std::string& genome,
           bool show_warnings, bool silent, const std::string& triangle) {
            hicxchange::Cool2hicOptions options;
            options.resolution = resolution;
            options.add_resolutions = add_resolutions;
            options.nproc = nproc;
            options.hic_version = hic_version;
            options.normalizations = normalizations;
            options.cooler_weight = std::move(cooler_weight);
            options.genome = genome;
            options.triangle = triangle;
            options.show_warnings = show_warnings;
            options.silent = silent;
            const auto console = python_console();
            py::gil_scoped_release release;
            return hicxchange::cool2hic_convert(infile, outfile, options, console);
        },
        py::arg("infile"), py::arg("outfile"), py::arg("resolution") = 0,
        py::arg("add_resolutions") = std::vector<std::int64_t>{}, py::arg("nproc") = 0, py::arg("hic_version") = 9,
        py::arg("normalizations") = "auto", py::arg("cooler_weight") = py::none(), py::arg("genome") = "",
        py::arg("show_warnings") = false, py::arg("silent") = false, py::arg("triangle") = "auto");
}

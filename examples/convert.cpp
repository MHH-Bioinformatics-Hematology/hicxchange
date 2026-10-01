// Converting in both directions through the library rather than the command
// line: a .hic file to a multi-resolution cool file and back.
//
//     convert matrix.hic out.mcool roundtrip.hic

#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

#include <hicxchange/hicxchange.hpp>

namespace {

// Messages go through a Console, so a caller can route them somewhere other
// than the process's standard streams. Console::standard() prints to stdout and
// stderr as the command line does; this one marks where each line came from.
hicxchange::Console makeConsole() {
    hicxchange::Console console;
    console.out = [](const std::string& line) { std::cout << "[convert] " << line << '\n'; };
    console.err = [](const std::string& line) { std::cerr << "[convert] " << line << '\n'; };
    // Called where the Python package calls input(); the conversions below
    // never prompt, so returning an empty line is enough.
    console.input = [](const std::string& prompt) {
        std::cout << prompt;
        return std::string();
    };
    return console;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: convert <in.hic> <out.mcool> <roundtrip.hic>\n";
        return 2;
    }
    const std::string hicPath = argv[1];
    const std::string coolPath = argv[2];
    const std::string backPath = argv[3];

    const hicxchange::Console console = makeConsole();

    try {
        // .hic to cool. An empty resolution list takes every base pair
        // resolution of the file; nproc 0 uses every core this process may run
        // on, and the output does not depend on it.
        const std::vector<std::int64_t> resolutions;   // all of them
        const int nproc = 0;
        const bool showWarnings = false;
        const bool silent = false;
        const std::string written = hicxchange::hic2cool_convert_mcool(
            hicPath, coolPath, resolutions, nproc, showWarnings, silent, console);

        // cool back to .hic. The options hold the defaults of the subtool, so
        // only what differs from them has to be set.
        hicxchange::Cool2hicOptions options;
        options.hic_version = 9;   // 8 writes what Juicer tools 1.22 writes
        options.nproc = 0;
        // "auto" carries over the normalization columns the cool file has and
        // computes VC, VC_SQRT, KR and SCALE when it has none; a list such as
        // "VC,SCALE" computes those regardless.
        options.normalizations = "auto";
        const std::string back = hicxchange::cool2hic_convert(written, backPath, options, console);

        std::cout << "wrote " << written << " and " << back << " on "
                  << hicxchange::available_threads() << " threads\n";
    } catch (const hicxchange::ExitError& error) {
        // The conditions under which the command line prints to standard error
        // and exits with status 1.
        std::cerr << "conversion failed: " << error.what() << '\n';
        return 1;
    }
    return 0;
}

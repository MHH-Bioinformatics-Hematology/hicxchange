// The hicxchange command: one executable with the subtools hic2cool and
// cool2hic. Each subtool keeps the arguments, help texts and exit statuses it
// had as a command of its own, so that only the program name changes.

#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include <hiccpp/errors.hpp>

#include "hicxchange/hicxchange.hpp"
#include "subtools.hpp"

namespace {

const char* kUsage = "usage: hicxchange [-h] [-v] subtool: {hic2cool, cool2hic} ...";

const char* kHelp = R"(usage: hicxchange [-h] [-v] subtool: {hic2cool, cool2hic} ...

Converting Hi-C contact matrices between the Juicer .hic format and the cooler
.cool and .mcool formats, in both directions.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

subtools:
  choose one of the following subtools:

  subtool: {hic2cool, cool2hic}
    hic2cool            .hic to cool or mcool, with the modes convert, update
                        and extract-norms
    cool2hic            cool or mcool to .hic version 8 or 9

Run a subtool with -h for its own options, for example
"hicxchange hic2cool convert -h".
)";

[[noreturn]] void usage_error(const std::string& message) {
    std::cerr << kUsage << "\nhicxchange: error: " << message << std::endl;
    std::exit(2);
}

int run(const std::vector<std::string>& args) {
    std::size_t i = 0;
    for (; i < args.size(); ++i) {
        if (args[i] == "-h" || args[i] == "--help") {
            std::cout << kHelp;
            return 0;
        }
        if (args[i] == "-v" || args[i] == "--version") {
            std::cout << "hicxchange " << hicxchange::kVersion << std::endl;
            return 0;
        }
        if (args[i].empty() || args[i][0] != '-') {
            break;
        }
        usage_error("unrecognized arguments: " + args[i]);
    }
    if (i >= args.size()) {
        usage_error("the following arguments are required: subtool: {hic2cool, cool2hic}");
    }
    const std::string subtool = args[i];
    const std::vector<std::string> rest(args.begin() + static_cast<std::ptrdiff_t>(i) + 1, args.end());
    if (subtool == "hic2cool") {
        return hicxchange::cli::run_hic2cool(rest);
    }
    if (subtool == "cool2hic") {
        return hicxchange::cli::run_cool2hic(rest);
    }
    usage_error("argument subtool: {hic2cool, cool2hic}: invalid choice: '" + subtool +
                "' (choose from hic2cool, cool2hic)");
}

}  // namespace

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    try {
        return run(std::vector<std::string>(argv + 1, argv + argc));
    } catch (const hicxchange::ExitError& e) {
        std::cout.flush();
        std::cerr << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cout.flush();
        std::cerr << "!!! ERROR. " << e.what() << std::endl;
        return 1;
    }
}

// The cool2hic command: a .cool or .mcool file to a .hic file.

#include <exception>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "argparse_lite.hpp"
#include "hic2cool/hic2cool.hpp"

namespace {

using hic2cool::cli::Option;
using hic2cool::cli::Parser;

const char* kUsage = R"(usage: cool2hic [-h] [-v] [-r RESOLUTION] [-a ADD_RESOLUTIONS] [-p NPROC]
                [--hic-version {8,9}] [-n NORMALIZATIONS]
                [--cooler-weight NAME] [-g GENOME] [-s] [-w]
                infile outfile)";

const char* kHelp = R"(usage: cool2hic [-h] [-v] [-r RESOLUTION] [-a ADD_RESOLUTIONS] [-p NPROC]
                [--hic-version {8,9}] [-n NORMALIZATIONS]
                [--cooler-weight NAME] [-g GENOME] [-s] [-w]
                infile outfile

convert a cooler file (.cool, .mcool or file.mcool::/resolutions/<bp>) to a
hic file

positional arguments:
  infile                cooler input file path or URI
  outfile               hic output file path

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -r RESOLUTION, --resolution RESOLUTION
                        integer bp resolution of the cooler file to write.
                        Setting to 0 (default) will use all resolutions of the
                        file
  -a ADD_RESOLUTIONS, --add-resolutions ADD_RESOLUTIONS
                        comma separated bp resolutions to add, binned from the
                        finest resolution written (each a multiple of it),
                        for example 2500000,1000000,500000
  -p NPROC, --nproc NPROC
                        number of threads to use. default set to 0, all
                        available CPUs
  --hic-version {8,9}   hic format version to write: 8 (Juicer tools 1.22) or
                        9 (Juicer tools 2), default 9
  -n NORMALIZATIONS, --normalizations NORMALIZATIONS
                        'auto' (default): write the normalization vectors
                        stored in the bins table (as hic2cool writes them),
                        or compute VC, VC_SQRT, KR and SCALE when there are
                        none. 'none': no normalization. Otherwise a comma
                        separated list of VC, VC_SQRT, KR and SCALE to compute
  --cooler-weight NAME  also write cooler's balancing weights (the bins column
                        'weight') as the divisive hic normalization vector
                        NAME
  -g GENOME, --genome GENOME
                        genome id for the hic header. default: the cooler
                        file's genome-assembly attribute
  -s, --silent          if used, silence standard program output
  -w, --warnings        if used, print out non-critical WARNING messages,
                        which are hidden by default. Silent mode takes
                        precedence over this
)";

int run(const std::vector<std::string>& args) {
    for (const auto& arg : args) {
        if (arg == "-v" || arg == "--version") {
            std::cout << "cool2hic " << hic2cool::kVersion << std::endl;
            return 0;
        }
    }
    Parser parser("cool2hic", kUsage, kHelp);
    parser.positional("infile");
    parser.positional("outfile");
    parser.option(Option{"-v", "--version", "", false, ""});
    parser.option(Option{"-r", "--resolution", "RESOLUTION", true, "0"});
    parser.option(Option{"-a", "--add-resolutions", "ADD_RESOLUTIONS", false, ""});
    parser.option(Option{"-p", "--nproc", "NPROC", true, "0"});
    parser.option(Option{"", "--hic-version", "{8,9}", true, "9"});
    parser.option(Option{"-n", "--normalizations", "NORMALIZATIONS", false, "auto"});
    parser.option(Option{"", "--cooler-weight", "NAME", false, ""});
    parser.option(Option{"-g", "--genome", "GENOME", false, ""});
    parser.option(Option{"-s", "--silent", "", false, ""});
    parser.option(Option{"-w", "--warnings", "", false, ""});
    parser.parse(args);
    if (!parser.unrecognized().empty()) {
        std::string list;
        for (const auto& word : parser.unrecognized()) {
            list += (list.empty() ? "" : " ") + word;
        }
        parser.error("unrecognized arguments: " + list);
    }
    hic2cool::Cool2hicOptions options;
    options.resolution = parser.integer("--resolution");
    options.nproc = static_cast<int>(parser.integer("--nproc"));
    options.hic_version = static_cast<int>(parser.integer("--hic-version"));
    if (options.hic_version != 8 && options.hic_version != 9) {
        parser.error("argument --hic-version: invalid choice: " + std::to_string(options.hic_version) +
                     " (choose from 8, 9)");
    }
    std::stringstream extra(parser.value("--add-resolutions"));
    std::string item;
    while (std::getline(extra, item, ',')) {
        if (item.find_first_not_of(" \t") == std::string::npos) {
            continue;
        }
        try {
            std::size_t pos = 0;
            options.add_resolutions.push_back(std::stoll(item, &pos));
            if (item.find_first_not_of(" \t", pos) != std::string::npos) {
                throw std::invalid_argument(item);
            }
        } catch (const std::exception&) {
            parser.error("argument -a/--add-resolutions: invalid int value: '" + item + "'");
        }
    }
    options.normalizations = parser.value("--normalizations");
    if (parser.given("--cooler-weight")) {
        options.cooler_weight = parser.value("--cooler-weight");
    }
    options.genome = parser.value("--genome");
    options.show_warnings = parser.flag("--warnings");
    options.silent = parser.flag("--silent");
    hic2cool::cool2hic_convert(parser.arg("infile"), parser.arg("outfile"), options);
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    try {
        return run(std::vector<std::string>(argv + 1, argv + argc));
    } catch (const hic2cool::ExitError& e) {
        std::cout.flush();
        std::cerr << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cout.flush();
        std::cerr << "!!! ERROR. " << e.what() << std::endl;
        return 1;
    }
}

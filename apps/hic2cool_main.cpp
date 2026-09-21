// The hic2cool command: the modes convert, update and extract-norms with the
// arguments, help texts and exit statuses of hic2cool 1.0.1's __main__.py.
// Changed: -p/--nproc defaults to 0, all available CPUs.

#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include <hicfilecpp/errors.hpp>

#include "argparse_lite.hpp"
#include "hic2cool/hic2cool.hpp"

namespace {

using hic2cool::cli::Option;
using hic2cool::cli::Parser;

const char* kMainUsage = "usage: hic2cool [-h] [-v] mode: {convert, update, extract-norms} ...";

const char* kMainHelp = R"(usage: hic2cool [-h] [-v] mode: {convert, update, extract-norms} ...

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

program modes:
  choose one of the following modes to run hic2cool:

  mode: {convert, update, extract-norms}
    convert             convert a hic file to a cooler file
    update              update a cooler file produced by hic2cool
    extract-norms       extract normalization vectors from a cooler file and
                        add them to a cooler file
)";

const char* kConvertUsage = R"(usage: hic2cool convert [-h] [-r RESOLUTION] [-p NPROC] [-s] [-w]
                        [--storage-mode {symmetric-upper,square}]
                        infile outfile)";

const char* kConvertHelp = R"(usage: hic2cool convert [-h] [-r RESOLUTION] [-p NPROC] [-s] [-w]
                        [--storage-mode {symmetric-upper,square}]
                        infile outfile

convert a hic file to a cooler file

positional arguments:
  infile                hic input file path
  outfile               cooler output file path

options:
  -h, --help            show this help message and exit
  -r RESOLUTION, --resolution RESOLUTION
                        integer bp resolution desired in cooler file. Setting
                        to 0 (default) will use all resolutions. If all
                        resolutions are used, a multi-res .cool file will be
                        created, which has a different hdf5 structure. See the
                        README for more info
  -p NPROC, --nproc NPROC
                        number of threads to use to parse hic file. default
                        set to 0, all available CPUs
  -s, --silent          if used, silence standard program output
  -w, --warnings        if used, print out non-critical WARNING messages,
                        which are hidden by default. Silent mode takes
                        precedence over this
  --storage-mode {symmetric-upper,square}
                        symmetric-upper (default) stores the upper triangle,
                        as hic2cool always has; square stores both triangles,
                        cooler's layout for asymmetric matrices
)";

const char* kUpdateUsage = "usage: hic2cool update [-h] [-o OUTFILE] [-s] [-w] infile";

const char* kUpdateHelp = R"(usage: hic2cool update [-h] [-o OUTFILE] [-s] [-w] infile

update a cooler file produced by hic2cool

positional arguments:
  infile                cooler input file path

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        optional new output file path
  -s, --silent          if used, silence standard program output
  -w, --warnings        if used, print out non-critical WARNING messages,
                        which are hidden by default. Silent mode takes
                        precedence over this
)";

const char* kExtractUsage = "usage: hic2cool extract-norms [-h] [-e] [-s] [-w] infile outfile";

const char* kExtractHelp = R"(usage: hic2cool extract-norms [-h] [-e] [-s] [-w] infile outfile

extract normalization vectors from a cooler file and add them to a cooler file

positional arguments:
  infile            hic file path
  outfile           cooler file path

options:
  -h, --help        show this help message and exit
  -e, --exclude-mt  if used, exclude the mitochondria (MT) from the output
  -s, --silent      if used, silence standard program output
  -w, --warnings    if used, print out non-critical WARNING messages, which
                    are hidden by default. Silent mode takes precedence over
                    this
)";

void shared_options(Parser& parser) {
    parser.option(Option{"-s", "--silent", "", false, ""});
    parser.option(Option{"-w", "--warnings", "", false, ""});
}

[[noreturn]] void main_error(const std::string& message) {
    std::cerr << kMainUsage << "\nhic2cool: error: " << message << std::endl;
    std::exit(2);
}

int run(const std::vector<std::string>& args) {
    // The primary parser: -h and -v before the mode.
    std::size_t i = 0;
    for (; i < args.size(); ++i) {
        if (args[i] == "-h" || args[i] == "--help" || args[i] == "--h" || args[i] == "--he" || args[i] == "--hel") {
            std::cout << kMainHelp;
            return 0;
        }
        if (args[i] == "-v" || args[i] == "--version" || (args[i].rfind("--v", 0) == 0 &&
                                                          std::string("--version").rfind(args[i], 0) == 0)) {
            std::cout << "hic2cool " << hic2cool::kVersion << std::endl;
            return 0;
        }
        if (args[i].empty() || args[i][0] != '-') {
            break;
        }
    }
    if (i >= args.size()) {
        main_error("the following arguments are required: mode: {convert, update, extract-norms}");
    }
    const std::string mode = args[i];
    std::vector<std::string> rest(args.begin() + static_cast<std::ptrdiff_t>(i) + 1, args.end());
    const auto check_extra = [](const Parser& parser) {
        if (!parser.unrecognized().empty()) {
            std::string list;
            for (const auto& word : parser.unrecognized()) {
                list += (list.empty() ? "" : " ") + word;
            }
            main_error("unrecognized arguments: " + list);
        }
    };
    if (mode == "convert") {
        Parser parser("hic2cool convert", kConvertUsage, kConvertHelp);
        parser.positional("infile");
        parser.positional("outfile");
        parser.option(Option{"-r", "--resolution", "RESOLUTION", true, "0"});
        parser.option(Option{"-p", "--nproc", "NPROC", true, "0"});
        parser.option(Option{"", "--storage-mode", "{symmetric-upper,square}", false, "symmetric-upper"});
        shared_options(parser);
        parser.parse(rest);
        check_extra(parser);
        const std::string storage_mode = parser.value("--storage-mode");
        if (storage_mode != "symmetric-upper" && storage_mode != "square") {
            parser.error("argument --storage-mode: invalid choice: '" + storage_mode +
                         "' (choose from 'symmetric-upper', 'square')");
        }
        hic2cool::hic2cool_convert(parser.arg("infile"), parser.arg("outfile"), parser.integer("--resolution"),
                                   static_cast<int>(parser.integer("--nproc")), parser.flag("--warnings"),
                                   parser.flag("--silent"), storage_mode);
    } else if (mode == "update") {
        Parser parser("hic2cool update", kUpdateUsage, kUpdateHelp);
        parser.positional("infile");
        parser.option(Option{"-o", "--outfile", "OUTFILE", false, ""});
        shared_options(parser);
        parser.parse(rest);
        check_extra(parser);
        hic2cool::hic2cool_update(parser.arg("infile"), parser.value("--outfile"), parser.flag("--warnings"),
                                  parser.flag("--silent"));
    } else if (mode == "extract-norms") {
        Parser parser("hic2cool extract-norms", kExtractUsage, kExtractHelp);
        parser.positional("infile");
        parser.positional("outfile");
        parser.option(Option{"-e", "--exclude-mt", "", false, ""});
        shared_options(parser);
        parser.parse(rest);
        check_extra(parser);
        hic2cool::hic2cool_extractnorms(parser.arg("infile"), parser.arg("outfile"), parser.flag("--exclude-mt"),
                                        parser.flag("--warnings"), parser.flag("--silent"));
    } else {
        main_error("argument mode: {convert, update, extract-norms}: invalid choice: '" + mode +
                   "' (choose from convert, update, extract-norms)");
    }
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

// The part of Python's argparse the command line tools use: options with and
// without values, abbreviated long options, grouped short flags, positional
// arguments, and argparse's usage and error messages (exit status 2).

#ifndef HIC2COOL_ARGPARSE_LITE_HPP
#define HIC2COOL_ARGPARSE_LITE_HPP

#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace hic2cool::cli {

struct Option {
    std::string short_name;  // "-r" or empty
    std::string long_name;   // "--resolution"
    std::string metavar;     // empty: a flag (store_true)
    bool integer = false;
    std::string fallback;    // default value of an option with a value
};

class Parser {
  public:
    Parser(std::string prog, std::string usage, std::string help)
        : prog_(std::move(prog)), usage_(std::move(usage)), help_(std::move(help)) {}

    void option(const Option& option) { options_.push_back(option); }
    void positional(const std::string& name) { positionals_.push_back(name); }

    [[noreturn]] void error(const std::string& message) const {
        std::cerr << usage_ << "\n" << prog_ << ": error: " << message << std::endl;
        std::exit(2);
    }

    // Parses args; returns false with the unparsed words in `extra` when
    // allow_extra is set, as parse_known_args does.
    void parse(const std::vector<std::string>& args) {
        std::vector<std::string> positional_values;
        bool only_positionals = false;
        for (std::size_t i = 0; i < args.size(); ++i) {
            const std::string& arg = args[i];
            if (only_positionals || arg.size() < 2 || arg[0] != '-' || is_number(arg)) {
                positional_values.push_back(arg);
                continue;
            }
            if (arg == "--") {
                only_positionals = true;
                continue;
            }
            if (arg == "-h" || (arg.rfind("--h", 0) == 0 && std::string("--help").rfind(arg, 0) == 0)) {
                std::cout << help_;
                std::exit(0);
            }
            if (arg.rfind("--", 0) == 0) {
                const auto eq = arg.find('=');
                const std::string name = arg.substr(0, eq);
                std::vector<const Option*> matches;
                for (const auto& o : options_) {
                    if (o.long_name == name) {
                        matches = {&o};
                        break;
                    }
                    if (o.long_name.rfind(name, 0) == 0) {
                        matches.push_back(&o);
                    }
                }
                if (matches.empty()) {
                    unrecognized_.push_back(arg);
                    continue;
                }
                if (matches.size() > 1) {
                    std::string list;
                    for (const auto* m : matches) {
                        list += (list.empty() ? "" : ", ") + m->long_name;
                    }
                    error("ambiguous option: " + name + " could match " + list);
                }
                const Option& o = *matches[0];
                if (o.metavar.empty()) {
                    if (eq != std::string::npos) {
                        error("argument " + label(o) + ": ignored explicit argument '" + arg.substr(eq + 1) + "'");
                    }
                    flags_[o.long_name] = true;
                } else if (eq != std::string::npos) {
                    store(o, arg.substr(eq + 1));
                } else {
                    if (i + 1 >= args.size() || (args[i + 1].size() > 1 && args[i + 1][0] == '-' &&
                                                 !is_number(args[i + 1]))) {
                        error("argument " + label(o) + ": expected one argument");
                    }
                    store(o, args[++i]);
                }
                continue;
            }
            // short options, possibly grouped: -sw, -r5000
            for (std::size_t k = 1; k < arg.size(); ++k) {
                const std::string name = std::string("-") + arg[k];
                if (name == "-h") {
                    std::cout << help_;
                    std::exit(0);
                }
                const Option* found = nullptr;
                for (const auto& o : options_) {
                    if (o.short_name == name) {
                        found = &o;
                    }
                }
                if (found == nullptr) {
                    unrecognized_.push_back(k == 1 ? arg : name);
                    break;
                }
                if (found->metavar.empty()) {
                    flags_[found->long_name] = true;
                    continue;
                }
                if (k + 1 < arg.size()) {
                    std::string value = arg.substr(k + 1);
                    if (value[0] == '=') {
                        value.erase(0, 1);
                    }
                    store(*found, value);
                } else {
                    if (i + 1 >= args.size() || (args[i + 1].size() > 1 && args[i + 1][0] == '-' &&
                                                 !is_number(args[i + 1]))) {
                        error("argument " + label(*found) + ": expected one argument");
                    }
                    store(*found, args[++i]);
                }
                break;
            }
        }
        if (positional_values.size() < positionals_.size()) {
            std::string missing;
            for (std::size_t p = positional_values.size(); p < positionals_.size(); ++p) {
                missing += (missing.empty() ? "" : ", ") + positionals_[p];
            }
            error("the following arguments are required: " + missing);
        }
        for (std::size_t p = 0; p < positional_values.size(); ++p) {
            if (p < positionals_.size()) {
                positional_values_[positionals_[p]] = positional_values[p];
            } else {
                unrecognized_.push_back(positional_values[p]);
            }
        }
    }

    [[nodiscard]] const std::vector<std::string>& unrecognized() const { return unrecognized_; }
    [[nodiscard]] bool flag(const std::string& long_name) const { return flags_.count(long_name) > 0; }
    [[nodiscard]] std::string value(const std::string& long_name) const {
        const auto it = values_.find(long_name);
        if (it != values_.end()) {
            return it->second;
        }
        for (const auto& o : options_) {
            if (o.long_name == long_name) {
                return o.fallback;
            }
        }
        return {};
    }
    [[nodiscard]] bool given(const std::string& long_name) const { return values_.count(long_name) > 0; }
    [[nodiscard]] std::int64_t integer(const std::string& long_name) const { return std::stoll(value(long_name)); }
    [[nodiscard]] const std::string& arg(const std::string& name) const { return positional_values_.at(name); }

  private:
    static bool is_number(const std::string& text) {
        if (text.size() < 2 || text[0] != '-') {
            return false;
        }
        char* end = nullptr;
        std::strtod(text.c_str(), &end);
        return end != nullptr && *end == '\0';
    }

    static std::string label(const Option& o) {
        return o.short_name.empty() ? o.long_name : o.short_name + "/" + o.long_name;
    }

    void store(const Option& o, const std::string& value) {
        if (o.integer) {
            std::string trimmed = value;
            trimmed.erase(0, trimmed.find_first_not_of(" \t"));
            trimmed.erase(trimmed.find_last_not_of(" \t") + 1);
            std::size_t pos = 0;
            bool ok = !trimmed.empty();
            try {
                std::stoll(trimmed, &pos);
                ok = ok && pos == trimmed.size();
            } catch (...) {
                ok = false;
            }
            if (!ok) {
                error("argument " + label(o) + ": invalid int value: '" + value + "'");
            }
            values_[o.long_name] = trimmed;
        } else {
            values_[o.long_name] = value;
        }
    }

    std::string prog_;
    std::string usage_;
    std::string help_;
    std::vector<Option> options_;
    std::vector<std::string> positionals_;
    std::map<std::string, bool> flags_;
    std::map<std::string, std::string> values_;
    std::map<std::string, std::string> positional_values_;
    std::vector<std::string> unrecognized_;
};

}  // namespace hic2cool::cli

#endif  // HIC2COOL_ARGPARSE_LITE_HPP

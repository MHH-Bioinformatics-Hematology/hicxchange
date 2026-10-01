// The subtools of the hicxchange command, each in its own translation unit.

#ifndef HICXCHANGE_SUBTOOLS_HPP
#define HICXCHANGE_SUBTOOLS_HPP

#include <string>
#include <vector>

namespace hicxchange::cli {

// hicxchange hic2cool: .hic to cool, with the modes convert, update and
// extract-norms of hic2cool 1.0.1.
int run_hic2cool(const std::vector<std::string>& args);
// hicxchange cool2hic: cool and mcool to .hic.
int run_cool2hic(const std::vector<std::string>& args);

}  // namespace hicxchange::cli

#endif  // HICXCHANGE_SUBTOOLS_HPP

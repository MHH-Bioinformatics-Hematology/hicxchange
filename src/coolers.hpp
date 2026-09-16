#ifndef HIC2COOL_COOLERS_HPP
#define HIC2COOL_COOLERS_HPP

#include <string>
#include <vector>

#include "h5.hpp"

namespace hic2cool::detail {

// cooler.fileops.list_coolers: the paths of the cooler groups in a file,
// natsorted.
[[nodiscard]] std::vector<std::string> list_coolers(const h5::File& file);

}  // namespace hic2cool::detail

#endif  // HIC2COOL_COOLERS_HPP

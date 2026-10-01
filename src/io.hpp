// The HDF5 reading and writing and the thread pool come from coolercpp.

#ifndef HICXCHANGE_IO_HPP
#define HICXCHANGE_IO_HPP

#include <coolercpp/fastio.hpp>
#include <coolercpp/parallel.hpp>

namespace hicxchange::detail {

namespace h5 = coolercpp::fastio;
using coolercpp::ThreadPool;

}  // namespace hicxchange::detail

#endif  // HICXCHANGE_IO_HPP

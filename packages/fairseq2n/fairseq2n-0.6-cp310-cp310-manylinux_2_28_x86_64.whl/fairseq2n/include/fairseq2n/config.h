// Copyright (c) Meta Platforms, Inc. and affiliates.
// All rights reserved.
//
// This source code is licensed under the BSD-style license found in the
// LICENSE file in the root directory of this source tree.

#pragma once

#include <cstdint>
#include <optional>

namespace fairseq2n {

inline constexpr std::int32_t version_major = 0;
inline constexpr std::int32_t version_minor = 6;
inline constexpr std::int32_t version_patch = ;

inline constexpr char torch_version[] = "2.8.0";
inline constexpr char torch_variant[] = "CUDA 12.8"

inline constexpr bool supports_image = true;

inline constexpr bool supports_cuda = true;
inline constexpr std::optional<std::int32_t> cuda_version_major = 12;
inline constexpr std::optional<std::int32_t> cuda_version_minor = 8;

}  // namespace fairseq2n

<!--
SPDX-FileCopyrightText: Copyright 2020-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>

SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the License); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an AS IS BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
# Vela Releases

These are the release notes for all Vela releases.  They document all of the
main feature changes, interface changes and reported defects that have been
fixed.  The version numbering adheres to the
[semantic versioning](https://semver.org/) scheme.

## Release 4.4.1 - 07/10/2025

* Fixed a bug with using incorrect quantisation when performing reshape removal


## Release 4.4.0 - 01/09/2025

**Main feature changes:**

* Updated to TOSA v1.0
  * Support for TOSA v0.80 is now removed. Users are encouraged to migrate models to v1.0 for continued compatibility.
* Ethos-U85:
  * Added decomposition support for FULLY_CONNECTED, MATMUL, AVG_POOL, ARGMAX
    * Enabling strides, dilation, tensors, and ranks greater than native Ethos-U can support
  * Added support for Conv2D with non-constant weights and/or bias
* Ethos-U55/Ethos-U65:
  * None

**Interface changes:**

* None

**Reported defect fixes:**

* Ethos-U55/Ethos-U65:
  * Fixed issue with consecutive Split operators (MLCE-1518, MLCE-1520)
* Ethos-U85:
  * Fixed issue with LUT followed by a Reshape (MLCE-1549)
  * Fixed issue with constant CPU-only tensors being incorrectly placed in ReadOnly memory (MLCE-1524)
  * Fixed issue with values near zero in LUT table for RSQRT (MLCE-1518)


## Release 4.3.0 - 20/05/2025

**Main feature changes:**

* Extended operator support:
  * Ethos-U85:
    * TFLite:
      * LOG, LSTM, STRIDED_SLICE with strides larger than one, RELU_0_TO_1
  * Ethos-U55/Ethos-U65:
    * TFLite:
      * RELU_0_TO_1
* Upgrade TensorFlow Lite support to version 2.18.1

**Interface changes:**

* None

**Reported defect fixes:**

* Ethos-U55/Ethos-U65
  * None
* Ethos-U85
  * Improved weight format selection for models with 2:4 sparse weights (MLCE-1473)
* General
  * Fixed issue with slicing of 64-bit bias causing segmentation fault (MLCE-1476)
  * Fixed graph connection issues caused by Reshape removal (MLCE-1496)
  * Fixed unintended disabling of the `--cpu-tensor-alignment` option (MLCE-1472)
  * Fixed issue where fused activations are recorded as CPU operators (MLCE-1461)
  * Fixed various issues with MAC count in summary (MLCE-1493 & MLCE-1461)


## Release 4.2.0 - 27/02/2025

The Vela compiler has moved from
[ML Platform](https://review.mlplatform.org/plugins/gitiles/ml/ethos-u/ethos-u-vela)
to [Arm's GitLab instance](https://gitlab.arm.com/artificial-intelligence/ethos-u/ethos-u-vela).
With this move, the process of filing bugs and submitting contributions has been updated. See
[BUGS.md](BUGS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Main feature changes:**

* Extended operator support:
  * Ethos-U85:
    * TOSA: CONV3D
    * TFLite: MIRROR_PAD and SELECT
  * Ethos-U55/Ethos-U65:
    * TFLite: RESIZE when height or width is 1

**Interface changes:**

* Addition of CLI options:
  * `--cop-format`
  * `--separate-io-regions`
  * `--list-configs`

**Reported defect fixes:**

* Ethos-U55/Ethos-U65
  * Fixed issue with feature map box calculations for Slice operator (MLCE-1433)
  * Fixed incorrect shape usage in PReLU optimization (MLCE-1437)
  * Fixed issue with execution order optimization of Split operator (MLCE-1415)
* General
  * Fix integer overflow errors due to NumPy 2.0 no longer promoting mixed
    type operations to a 64-bit data type (MLCE-1418)
  * Add documentation of the output format option (MLCE-1446)


## Release 4.1.0 - 26/11/2024

**Main feature changes:**

* Added TOSA v0.80.0 support for Ethos-U85
  * Base Inference Profile and 8K Level
  * Includes all integer operators apart from CONV3D, DIM, COND_IF, WHILE_LOOP
  * Includes decomposition support for CONV2D and elementwise operators
    * Enabling strides, dilation, tensors, and ranks greater than native Ethos-U can support
  * Includes variable tensor support
* Improved Ethos-U85 TOSA operator fusing for better performance
* Multiple improvements to performance estimation and elementwise chaining
* Added support for generating and releasing binary wheels. Wheels are released for all
combinations of Python 3.9-3.13 and Linux (x86-64), Linux (AArch64), Windows (x86-64) and
macOS (AArch64)
* Removed internal Vela cycle estimates from summary. See Interface Changes section
for option to display the estimates.

**Interface changes:**

* Addition of CLI option to display internal Vela performance estimates in the summary:
  * `--verbose-cycle-estimate`

**Reported defect fixes:**

* Ethos-U55/Ethos-U65
  * Add max kernel size constraint for SOFTMAX (MLCE-1404)
* Ethos-U85
  * Update constraint class to reject feature maps with data type float (MLCE-1403)
  * Reset all chaining registers before primary operation (MLCE-1403)
* General
  * Avoid rounding issues by using float during RSQRT int16 LUT table generation


## Release 4.0.0 - 04/09/2024

**Main feature changes:**

* Added initial support for Ethos-U85
  * Supported TFLite operators listed in SUPPORTED_OPS.md
  * No backwards incompatible changes for Ethos-U55 or Ethos-U65
* Upgrade TensorFlow Lite support to version 2.17
* NumPy 2.0 compatibility

**Interface changes:**

* Addition of fields in the configuration file:
  * `*_max_reads` and `*_max_writes`
  * `*_ports_used` for Ethos-U85 System configurations

* Addition of CLI debug options for the Regor compilation path:
  * `--debug-force-regor`
  * `--disable-chaining`
  * `--disable-fwd`
  * `--disable-cascading`
  * `--disable-buffering`

**Reported defect fixes:**

* Ethos-U55/Ethos-U65
  * Fixed issue with reshaping of MEAN operator (MLCE-1293)
  * Fixed issue with extracting strides from STRIDED_SLICE operator attribute (MLCE-1316)


## Release 3.12.0 - 20/05/2024

**Main feature changes:**

* Extended operator support: STRIDED_SLICE with strides in H/W > 1
* Upgrade TensorFlow Lite support to version 2.16

**Interface changes:**

* None

**Reported defect fixes:**

* Fixed CONCAT operators split between multiple subgraphs (MLCE-1223 & MLCE-1252)
* Fixed issue with combining STRIDED_SLICE operation with elementwise broadcasting (MLCE-1223)
* Fixed issue with LUT index calculation and STRIDED_SLICE optimisation (MLCE-1253)


## Release 3.11.0 - 19/02/2024

**Main feature changes:**

* New operator support: MIRROR_PAD
* Upgrade TensorFlow Lite support to version 2.15
* Fixed issue with reporting incorrect peak memory usage with verbose allocation option
* Fixed issue with incorrect number of CPU operators in summary report
* Fixed rounding mode issue with int16 FULLY_CONNECTED

**Interface changes:**

* None

**Reported defect fixes:**

* Fixed issue with passing through FULLY_CONNECTED operators with dynamic weights (MLCE-1176)


## Release 3.10.0 - 16/11/2023

**Main feature changes:**

* New operator support: SQUARED_DIFFERENCE, TRANSPOSE
* Upgrade TensorFlow Lite support to version 2.14
* Improved stride checking and support for:
  * AVERAGE_POOL_2D, CONV_2D, MAX_POOL_2D, TRANSPOSE_CONV
* Added missing pass-through options for RANDOM_UNIFORM

**Interface changes:**

* None

**Reported defect fixes:**

* Removed duplicate CPU tensors (MLCE-1103 & MLCE-1106)


## Release 3.9.0 - 15/08/2023

**Main feature changes:**

* New operator support: RSQRT
* Extended Mean operator support
* Enabled weight buffering for the Size optimisation strategy (CLI option "--optimise Size")
* Improved documentation of verbose CLI options
* Upgrade TensorFlow Lite support to version 2.12

**Interface changes:**

* None

**Reported defect fixes:**

* Fixed crash when rewriting Slice operator (MLCE-918)
* Fixed issues with faulty memory overwrite for reshape operator (MLCE-1003)
* Fixed runtime issues for grouped convolutions (MLCE-1076)
* Enabled cascading for resize operators (MLCE-1058)


## Release 3.8.0 - 17/05/2023

**Main feature changes:**

* New operator support: ARG_MAX, UNIDIRECTIONAL_SEQUENCE_LSTM, EXP
* Improved CONV_2D striding support
* Upgrade TensorFlow Lite support to version 2.11
* Changed MEAN operator implementation to match changes in TensorFlow Lite reference kernels
* Fixed int8 and int16 fusing of PAD and AVERAGE_POOL_2D
* Fixed issues with pass-through support for:
  * Resource variables
  * Fused activation attribute and missing attributes
* Improved documentation of verbose CLI options

**Interface changes:**

* Addition of CLI options:
  * `--verbose-progress`

**Reported defect fixes:**

* Compilation progress feedback (MLCE-1009)
* Reduced compilation time for large networks (MLCE-1009)
* Fixed handling of invalid RESHAPE operators (MLCE-997)
* Fixed crash when passing-through semantically incorrect operators with missing attributes (MLCE-1027)


## Release 3.7.0 - 16/02/2023

**Main feature changes:**

* Added support for Tensor is_variable attribute
  * Requires TensorFlow Lite for Microcontrollers PR#1676 see
    <https://github.com/tensorflow/tflite-micro/pull/1676>
* Added pass-through support for Resource Variable operators to allow them to run on the CPU
* Moved from install and distribution using setup.py to setup.cfg and pyproject.toml
* Changed to conform to Arm’s inclusive language policy
* Added stride 4 support for CONV_2D operator with 1-D kernel
* Fixes and improvements to Cascading and Performance Estimation
* Asymmetric weights are no longer forced to be symmetric by default, see new CLI option

**Interface changes:**

* Addition of CLI options:
  * `--force-symmetric-int-weights`

**Reported defect fixes:**

* Conflicting Size and Performance optimisations caused high SRAM usage (MLCE-953)
* AArch64 undefined casting behaviour in NumPy (MLCE-968)
* Performance estimation reporting regression (MLCE-973)
* Assert due to consecutive reshapes (MLCE-987)
* Assert with illegal SPLIT operators (MLCE-997)
* Assert when elementwise operators follow a SPLIT operator (MLCE-997)
* STRIDED_SLICE operator with shrink_axis_mask was not fully supported (MLCE-1014)

## Release 3.6.0 - 23/11/2022

**Main feature changes:**

* New operator support: RESIZE_BILINEAR (Half-Pixel Centers), RESIZE_NEAREST_NEIGHBOR
  (Half-Pixel Centers), PReLU
* Add support for dilation >2 for CONV_2D and DEPTHWISE_CONV_2D kernels
* Improve per-layer performance estimation reporting and documentation
* Ethos-U65 performance improvements
* Fixed SIGSEGV crash from weight codec
* Fixed installation problems on AArch64 with Python 3.8
* Upgrade TensorFlow Lite support to version 2.10
  * Under certain circumstanced the optimised model may not match TensorFlow 2.10
    for int16x8 CONV2D, TRANSPOSE_CONV2D and FULLY_CONNECTED, see
    <https://github.com/tensorflow/tensorflow/issues/53763> for more information

**Interface changes:**

* None

**Reported defect fixes:**

* Add support for multiple TFLite subgraphs (MLCE-907)
* Add missing operators in Vela debug DB (MLCE-913)
* Optimize fast storage for feature maps (MLCE-929)
* Reshape bias tensor as 1D (MLCE-944)
* Update offset calculation for Slice (MLCE-945)

## Release 3.5.0 - 23/08/2022

**Main feature changes:**

* New operator support: RESIZE_NEAREST_NEIGHBOR, SHAPE
* Cascading support for elementwise operators
* Ethos-U65 performance improvements
* Upgrade TensorFlow Lite support to version 2.9
  * Under certain circumstanced the optimised model may not match TensorFlow 2.9
    for int16x8 CONV2D, TRANSPOSE_CONV2D and FULLY_CONNECTED, see
    <https://github.com/tensorflow/tensorflow/issues/53763> for more information

**Interface changes:**

* None

**Reported defect fixes:**

* SRAM usage is higher than with old `--pareto-metric BwCycMemBlkH` option for some networks (MLCE-860)
* Assert caused by CONCATENATION operator with invalid tensor shapes (MLCE-896)

## Release 3.4.0 - 24/05/2022

**Main feature changes:**

* Support hosting of third party system configuration files in ethosu/config_files/*
  * New configs can be contributed by following the information in OPTIONS.md
* Upgrade TensorFlow Lite support to version 2.8
* Ethos-U65 performance optimisations
* Improvements to HillClimb tensor allocator
* Add mypy support to pre-commit checks
* General bug fixes to functionality and improve stability
* Lower Python requirement to Python 3.7 for greater compatibility with other tools

**Interface changes:**

* Addition of CLI options:
  * `--list-config-files`, `--verbose-performance`, `--hillclimb-max-iterations`

**Reported defect fixes:**

* Splitting into multiple Ethos-U Custom operators (MLCE-800)
* Layer-wise performance information (MLCE-759)
* Unable to find a valid block config (MLCE-776)
* LeakyReLU does not support negative alpha values (MLCE-817)
* Command stream disassembly does not contain address (MLCE-823)
* FULLY_CONNECTED does not implicitly reshape greather than rank-2 input tensor (MLCE-691)

## Release 3.3.0 - 25/02/2022

**Main feature changes:**

* Upgrade TensorFlow Lite support to version 2.7
  * Increases Python requirement to at least version 3.8
* Scheduling algorithm improvements
  * Improved spilling reduces DRAM bandwidth for Ethos-U65 Dedicated SRAM
  * Improved weight buffering increases performance for Ethos-U65 512-MAC
  * Optimised tensor allocation reduces compilation time for large networks
* Extended operator support:
  * RESIZE_BILINEAR: Adds support for upscaling on NPU by factors of 4x4 and 8x8

**Interface changes:**

* None

**Reported defect fixes:**

* Memory corruption with custom operator and zero concatenation (MLCE-678)
* Crash when creating explicit padding (MLCE-684)
* Fix assert when setting address on identical LUT tensors (MLCE-691)
* Reduce SRAM usage for some elementwise operations (MLCE-750)
* Issue when running a model with Padding (MLCE-768)

## Release 3.2.0 - 26/11/2021

**Main feature changes:**

* Bug fixes
* Documentation of community bug reporting via Phabricator on ML Platform
* New operator support: EXPAND_DIMS
* Extended experimental TOSA support

**Interface changes:**

* External API v1.2
  * Fixed bug in `npu_find_block_configs()` with Conv1D optimisation

* Verbose output
  * Clarified Subgraph IO Summary

* Summary output
  * Removed incorrect passes information
  * Fixed and reformatted the reporting of CPU operators

**Reported defect fixes:**

* Clarified section on access cycles in PERFORMANCE.md (MLCE-654)
* Crash due to mismatch in padding shape in OFM (MLCE-652)
* Bug where back to back activations were ignored (MLCE-650)
* Output mismatch for unsupported RESHAPE with 16-bit 5D tensors (MLCE-630)
* Bug where tensors with "skip connections" were incorrectly handled (MLCE-621)
* Crash due to the same tensor being used for both inputs to operator (MLCE-620)
* Missing constraint on batch size for MEAN operator (MLCE-619)
* Bug where third-party custom ops were not passed through correctly (MLCE-602)
* Crash due to mismatch in tensor indices for EXP operator (MLCE-599)

## Release 3.1.0 - 30/08/2021

**Main feature changes:**

* New operator support: SQUEEZE
* Updated support for TensorFlow 2.5
* Experimental limited support for reading TOSA files

**Interface changes:**

* Re-addition of CLI option:
  * `--recursion-limit`
* External API v1.1
  * Re-instated functionality of `find_block_configs()` from Vela 2.1.0

**Reported defect fixes:**

* Bug with IFM box depth for convolutions fused with SPLIT (MLCE-490)
* Bug with missing attribute from integer type (MLCE-534)
* Bug with incorrect options in TensorFlow Lite mapping (MLCE-427)

## Release 3.0.0 - 28/05/2021

**Main feature changes:**

* Improved user control over Vela
  * Allowing user to specify an arena cache size target
  * Allowing user to optimise for inference time or memory footprint
* Extended operator support for PAD and MEAN
* Multiple improvements to reduce compilation time

**Interface changes:**

* Addition of CLI options:
  * `--optimise`, `--arena-cache-size`
* Removal of CLI options:
  * `--cascading`, `--cache-bias-scale-tensor`, `--ifm-streaming`,
  * `--force-block-config`, `--block-config-limit`, `--recursion-limit`
  * `--nhcwb16-between-cascaded-passes`, `--weight-estimation-scaling`
  * `--pareto-metric`, `--verbose-pareto-frontier-schedules`

**Reported defect fixes:**

* Regression in FullyConnected between v2.0.1 and v2.1.0 (MLCE-484)
* Output mismatch for 16-bit TANH and SIGMOID (MLCE-362)
* Improved `--verbose-graph` CLI option output (MLCE-482)
* Bug with `--verbose-operators` CLI option (MLCE-444)
* Bug with incorrect tensor format chosen for SPLIT (MLCE-331)
* Bug with STRIDED_SLICE padding (MLCE-425)
* Bug with RESHAPE at the edge of Ethos-U custom operator (MLCE-443)
* Document Vela memory configuration and options (MLCE-410 & MLCE-498)

## Release 2.1.0 - 25/02/2021

**Main feature changes:**

* New operator support: PAD, MEAN and HARD_SWISH
* New HillClimb tensor allocator (default)
* Network performance improved of shallow layers
* Updated support to TensorFlow Lite 2.4
* Added Microsoft Windows 10 support
* Extended debug database to support multiple Ethos-U Custom operators
* Added cascading support to RESIZE_BILINEAR
* Improved performance estimations

**Interface changes:**

* Addition of Vela configuration (.ini) file options:
  * `MEM_burst_length`, `MEM_read_latency`, `MEM_write_latency`
* Change to CLI options:
  * `--tensor-allocator` (change default to HillClimb)
* Addition of CLI options:
  * `--verbose-all`

**Reported defect fixes:**

* Bug with handling multiple custom operators (MLCE-329)
* Bug with configuring Ethos-U55 with DRAM (MLCE-322)

## Release 2.0.1 - 03/12/2020

* Fixed a broken link in the long description used by PyPi

## Release 2.0.0 - 30/11/2020

**Main feature changes:**

* Advanced Spilling for Ethos-U65 Dedicated SRAM
* Specific network performance improvements for Ethos-U65 Dedicated SRAM
* General performance improvements for different networks and system
configurations
* Support SOFTMAX batching
* Improved supported operator checking and reporting
* Improved pass-through of Ethos-U hardware unsupported operators
* Enhanced performance estimations
* Extended external API
* New Vela configuration file format (with example `vela.ini`)
* Updated support to TensorFlow Lite 2.3
* Made 8-bit TANH and LOGISTIC bit-exact and faster
* Generation of a network debug database to aid profiling and debug

**Interface changes:**

* Non-backwards compatible changes to the Vela configuration (.ini) file
* Removal of CLI options:
  * `--show-minimum-possible-allocation`, `--ifm-ofm-overlap`
  * `--permanent-storage`, `--global-memory-clock-scale`
* Change to CLI options:
  * `--config` (support multiple)
  * `--accelerator-config` (change 'yoda' to 'ethos-u65')
* Addition of CLI options:
  * `--api-version`, `--supported-ops-report`, `--enable-debug-db`
  * `--verbose-config`, `--cache-bias-scale-tensor`, `--memory-mode`
  * `--cpu-tensor-alignment`
* Addition of External APIs:
  * Command Stream generation, Driver Payload creation, and Finding a Block
Config

**Reported defect fixes:**

* Add support for 128-Byte alignment (`--cpu-tensor-alignment`) (MLCE-221)
* Bug with SPLIT and non-unique scale & bias tensors (MLCE-234)
* Bug with overlapping tensor buffers in CONCATENATION (MLCE-246)
* Bug with a non-splitting SPLIT (MLCE-247)
* Regression in STRIDED_SLICE between v1.0.0 and v1.2.0 (MLCE-252)
* Add batch support to SOFTMAX (MLCE-265)
* Vela config file examples (MLCE-277)

## Release 1.2.0 - 31/08/2020

**Main feature changes:**

* New Ethos-U NPU operator support: SOFTMAX and QUANTIZE (requantise only)
* Improved Ethos-U NPU operator support: RESIZE_BILINEAR and LEAKY_RELU
* Improved pass-through of operators not supported by Ethos-U NPU
* Preserve TensorFlow Lite (.tflite) file metadata
* Improved network performance
* Performance estimation statistics improved
* New external API

**Interface changes:**

* Addition of CLI options: `--weight-estimation-scaling`
* Addition of External APIs: Weight compression and Bias & scale encoding

**Reported defect fixes:**

* Custom operator not passing through Vela (MLCE-223)
* Flash usage increases in 1.1.0 (MLCE-227)
* Vela fails with optional bias tensor (MLCE-231)

## Release 1.1.0 - 30/06/2020

**Main feature changes:**

* Multi-core support
* DRAM memory allocation support

**Interface changes:**

* Change to CLI options: `--accelerator-config` (added values `yoda-256` and
`yoda-512`)

## Release 1.0.0 - 18/06/2020

**Main feature changes:**

* Int16 support
* New HW operator support: RESIZE_BILINEAR and TRANSPOSE_CONV
* NHCWB16 support between cascaded passes
* Stride 3 support
* pre-commit framework for code formatting, linting and testing

**Interface changes:**

* Removal of CLI options: `--batch-size`, `--inter-pass-cycle-delay`,
`--dram-bandwidth`
* Addition of CLI options: `--nhcwb16-between-cascaded-passes`

**Reported defect fixes:**

* Crop2D operator not passing through optimizer (MLCE-218)
* Custom Operator not passing through optimizer (MLCE-219)

## Release 0.1.0 - 29/04/2020

Initial release.

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
# Vela

Vela is a compiler for [Arm Ethos-U NPU](https://www.arm.com/products/silicon-ip-cpu)
edge AI devices.  It is used to convert neural networks defined in [TOSA](https://www.mlplatform.org/tosa/)
or [TensorFlow Lite/LiteRT](https://ai.google.dev/edge/litert) format into
Ethos-U command streams.

The input network must have quantised activations and quantised weights in order
to be accelerated by the Ethos-U.

More details about Ethos-U devices:
* Ethos-U55, [product](https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u55) and [developer](https://developer.arm.com/Processors/Ethos-U55) information
* Ethos-U65, [product](https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u65) and [developer](https://developer.arm.com/Processors/Ethos-U65) information
* Ethos-U85, [product](https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u85) and [developer](https://developer.arm.com/Processors/Ethos-U85) information

## Installation

Vela runs on:
* Apple macOS
* Linux
* Microsoft Windows

The simplest way to obtain Vela is to install it directly from [PyPi](https://pypi.org/project/ethos-u-vela/).
The following will install the latest released version:

```bash
pip3 install ethos-u-vela
```

### Requirements

If your system does not match one of the pre-built binary wheels on PyPi then
the installation process will attempt to build Vela from its source code.  To do
this it requires the following:
* Development version of Python 3 containing the Python/C API header files
   - e.g. `apt install python3.10-dev`
* C99 and C++17 capable compiler and toolchain
    - For Apple macOS; XCode or Command Line Tools are recommended,
      see <https://developer.apple.com/xcode/resources/> or `xcode-select --install`
    - For Linux operating systems; a GNU or Clang toolchain is recommended,
      e.g. `apt install build-essential`
    - For Microsoft Windows 10; the Microsoft Visual C++ 14.2 Build Tools are recommended,
      see <https://wiki.python.org/moin/WindowsCompilers>
* CMake
    - See <https://cmake.org/download/>

### Manually Building

The source code is available from [Arm's GitLab Instance](https://gitlab.arm.com/artificial-intelligence/ethos-u/ethos-u-vela),
see [Building From Source](BUILD.md) for more details.

## Getting Started

Once installed, Vela can be run from the command line by specifying just two
settings:
* Target Ethos-U device; `--accelerator-config`
* Neural network file; `.tflite` or `.tosa`

```bash
vela --accelerator-config ethos-u55-128  my_network.tflite
```

However, it is highly recommended that you specify some additional settings that
describe the Ethos-U system and what optimisation strategy the compiler should
use.  The three additional settings are:
* System configuration; `--system-config`
* Memory mode; `--memory-mode`
* Optimisation strategy; `--optimise`

The system configuration and memory mode refer to definitions in a configuration
file.  These are specific to the target system.  However an example
configuration (`Arm/vela.ini`) containing some generic reference systems is
provided as part of the installation.

The optimisation strategy indicates whether the compiler should minimise
inference time or runtime memory usage.

See [CLI Options](OPTIONS.md) for more information.

Example of how to set the system configuration and memory mode:
```bash
vela --config Arm/vela.ini --system-config Ethos_U85_SYS_DRAM_High --memory-mode Dedicated_Sram_384KB --accelerator-config ethos-u85-256  my_network.tosa
```

Example of how to set the optimisation strategy:
```bash
vela --optimise Size --accelerator-config ethos-u55-64  my_network.tflite
```

Command to list all known configuration files:
```bash
vela --list-config-files
```

Command to list all configurations in a configuration file:
```bash
vela --list-configs Arm/vela.ini
```

### Output

The result of the compilation is an optimised network in either TFLite or Raw
format depending upon the input network.  This can be overridden using the
`--output-format option`.

TFLite output contains TensorFlow Lite Custom operators for those parts of
the network that can be accelerated by the Ethos-U NPU.  Parts of the network
that cannot be accelerated are left unchanged.

Raw output contains the command stream and weight data required to run Ethos-U
parts of the optimised network.  This is stored in [`.npz`](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format)
format.  See the Output format [CLI Option](OPTIONS.md) for more information.
This does not contain CPU parts of the network and so cannot be used for
converting TFLite to TOSA.

#### Warnings

It is important to thoroughly review and understand all warning messages
generated by the compiler as they could indicate that not all operators were
optimally converted to run on the Ethos-U.

#### Performance information

A performance estimation summary is reported after compilation.  The cycle and
bandwidth numbers should not be taken as accurate representations of real
performance numbers and they should not be compared against those from other
compilations that use different settings or configurations.  The numbers
reported allow the compiler to make its optimisation decisions only.  For
accurate performance numbers the network should be run and profiled on an FPGA.
For approximate performance numbers the network can be run on a Fixed
Virtual Platform (FVP) Model.

## Additional Vela Information
* [External APIs](API.md)
* [Bug Reporting](BUGS.md)
* [Building From Source](BUILD.md)
* [Contributing](CONTRIBUTING.md)
* [CLI Options](OPTIONS.md)
* [Debug Database](DEBUG_DB.md)
* [Performance Estimations](PERFORMANCE.md)
* [Operator Support](SUPPORTED_OPS.md)
* [Changelog](CHANGELOG.md)
* [Security Vulnerabilities](SECURITY.md)
* [Testing](TESTING.md)

## Inclusive language commitment

This product conforms to Arm’s inclusive language policy and, to the best of our
knowledge, does not contain any non-inclusive language.  If you find something
that concerns you then email [terms@arm.com](mailto:terms@arm.com).

## License

Vela is licensed under [Apache License 2.0](LICENSE.txt).
# SPDX-FileCopyrightText: Copyright 2021, 2024-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Description:
# Functions used to write to a raw format (.npz) file.
import numpy as np

from .high_level_command_to_npu_op import get_region
from .nn_graph import PassPlacement
from .operation import Op


def write_rawdata_output(nng, arch, filename):
    subgraphs_to_write = [sg for sg in nng.subgraphs if sg.placement == PassPlacement.Cpu]

    for sg_idx, sg in enumerate(subgraphs_to_write):
        custom_op = None
        for ps in sg.passes:
            for op in ps.ops:
                if op.type == Op.CustomNpuOp:
                    custom_op = op
                    break
            if custom_op:
                break

        if custom_op:
            ifm_shapes = []
            ifm_elem_sizes = []
            ifm_regions = []
            ifm_offsets = []
            ofm_shapes = []
            ofm_elem_sizes = []
            ofm_regions = []
            ofm_offsets = []
            cmd_stream_tensor, weight_tensor, scratch_tensor, scratch_fast_tensor = custom_op.inputs[:4]
            weight_region = get_region(weight_tensor.mem_type, arch)
            scratch_region = get_region(scratch_tensor.mem_type, arch)
            scratch_fast_region = get_region(scratch_fast_tensor.mem_type, arch)
            for ifm in custom_op.inputs[4:]:
                ifm_shapes.append(ifm.get_full_shape())
                ifm_regions.append(get_region(ifm.mem_type, arch))
                ifm_offsets.append(ifm.address)
                ifm_elem_sizes.append(ifm.element_size())
            for ofm in custom_op.outputs:
                ofm_shapes.append(ofm.get_full_shape())
                ofm_regions.append(get_region(ofm.mem_type, arch))
                ofm_offsets.append(ofm.address)
                ofm_elem_sizes.append(ofm.element_size())

            filename_sg = f"{filename}_vela_sg{sg_idx}.npz"
            np.savez(
                filename_sg,
                cmd_data=cmd_stream_tensor.values,
                weight_data=weight_tensor.values,
                weight_region=weight_region,
                scratch_shape=scratch_tensor.shape,
                scratch_region=scratch_region,
                scratch_size=int(scratch_tensor.shape[0]),
                scratch_fast_shape=scratch_fast_tensor.shape,
                scratch_fast_region=scratch_fast_region,
                scratch_fast_size=int(scratch_fast_tensor.shape[0]),
                input_shape=ifm_shapes,
                input_elem_size=ifm_elem_sizes,
                input_region=ifm_regions,
                input_offset=ifm_offsets,
                output_shape=ofm_shapes,
                output_elem_size=ofm_elem_sizes,
                output_region=ofm_regions,
                output_offset=ofm_offsets,
                variable_shape=[],
                variable_elem_size=[],
                variable_region=[],
                variable_offset=[],
            )


# Write out a CompiledRawModel to a numpy raw file.
def write_rawdata_output_from_model(filename, model):
    filename_sg = f"{filename}_vela.npz"
    np.savez(
        filename_sg,
        cmd_data=model.command_stream,
        weight_data=model.read_only.data,
        weight_region=model.read_only.region,
        scratch_shape=[model.scratch.size],
        scratch_region=model.scratch.region,
        scratch_size=model.scratch.size,
        scratch_fast_shape=[model.scratch_fast.size],
        scratch_fast_region=model.scratch_fast.region,
        scratch_fast_size=model.scratch_fast.size,
        input_shape=[t.shape for t in model.inputs],
        input_elem_size=[t.element_size for t in model.inputs],
        input_region=[t.region for t in model.inputs],
        input_offset=[t.address for t in model.inputs],
        output_shape=[t.shape for t in model.outputs],
        output_elem_size=[t.element_size for t in model.outputs],
        output_region=[t.region for t in model.outputs],
        output_offset=[t.address for t in model.outputs],
        variable_shape=[t.shape for t in model.variables],
        variable_elem_size=[t.element_size for t in model.variables],
        variable_region=[t.region for t in model.variables],
        variable_offset=[t.address for t in model.variables],
    )

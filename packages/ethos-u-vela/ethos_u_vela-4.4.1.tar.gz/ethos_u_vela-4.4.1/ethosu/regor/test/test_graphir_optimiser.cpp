//
// SPDX-FileCopyrightText: Copyright 2024-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>
//
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the License); you may
// not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an AS IS BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#include "common/common.hpp"

#include "architecture/ethosu85/ethos_u85.hpp"
#include "compiler/graphir_optimiser.hpp"
#include "compiler/scheduler_packing.hpp"
#include "compiler/tensor_properties.hpp"
#include "util.hpp"

#include <fmt/format.h>
#include <catch_all.hpp>

#include "regor.h"

using namespace regor;


TEST_CASE("test_graphir_optimiser - constant propagation")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    SECTION("SHL operation")
    {
        auto graph = [&]()
        {
            std::vector<std::shared_ptr<Operation>> ops;
            auto cifm = CreateTensor("CIFM", Shape(1, 1, 1, 10), DataType::Int8, 1);
            auto cifm1 = CreateTensor("CIFM1", Shape(1, 1, 10, 1), DataType::Int8, 2);
            auto cofm = CreateTensor("COFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto ifm = CreateTensor("IFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto ofm = CreateTensor("OFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto cop = CreateOperation(OpType::SHL, TensorUsage::IFM, cifm, TensorUsage::IFM1, cifm1, TensorUsage::OFM, cofm);
            auto op = CreateOperation(OpType::Add, TensorUsage::IFM, ifm, TensorUsage::IFM1, cofm, TensorUsage::OFM, ofm);
            ops.push_back(std::move(cop));
            ops.push_back(std::move(op));

            // Create graph with ops
            return CreateGraph(ops);
        }();

        GraphOptimiserOptions options;
        const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

        std::vector<Operation *> allOps;

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 2);

        REQUIRE(!optimiser.empty());
        optimiser.back()->Process(graph.get());
        allOps.clear();

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 1);
        REQUIRE(allOps[0]->Inputs()[TensorUsage::IFM1].tensor->IsConstant());
        auto iview = allOps[0]->Inputs()[TensorUsage::IFM1].tensor->View();
        auto idata = iview.RawData<int8_t>();
        for ( int i = 0; i < allOps[0]->Inputs()[TensorUsage::IFM1].tensor->StorageShape().Elements(); i++ )
        {
            REQUIRE(idata[i] == 1 << 2);
        }
    }

    SECTION("MemoryCopy operation")
    {
        auto graph = [&]()
        {
            std::vector<std::shared_ptr<Operation>> ops;
            auto cifm = CreateTensor("CIFM", Shape(1, 1, 1, 10), DataType::Int8, 1);
            auto cofm = CreateTensor("COFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto ifm = CreateTensor("IFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto ofm = CreateTensor("OFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto cop = CreateOperation(OpType::MemoryCopy, TensorUsage::IFM, cifm, TensorUsage::OFM, cofm);
            auto op = CreateOperation(OpType::Add, TensorUsage::IFM, ifm, TensorUsage::IFM1, cofm, TensorUsage::OFM, ofm);
            ops.push_back(std::move(cop));
            ops.push_back(std::move(op));

            // Create graph with ops
            return CreateGraph(ops);
        }();

        GraphOptimiserOptions options;
        const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

        std::vector<Operation *> allOps;

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 2);

        REQUIRE(!optimiser.empty());
        optimiser.back()->Process(graph.get());
        allOps.clear();

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 1);
        REQUIRE(allOps[0]->Inputs()[TensorUsage::IFM1].tensor->IsConstant());
        auto iview = allOps[0]->Inputs()[TensorUsage::IFM1].tensor->View();
        auto idata = iview.RawData<int8_t>();
        for ( int i = 0; i < allOps[0]->Inputs()[TensorUsage::IFM1].tensor->StorageShape().Elements(); i++ )
        {
            REQUIRE(idata[i] == 1);
        }
    }

    SECTION("Traversal order")
    {
        auto graph = [&]()
        {
            std::vector<std::shared_ptr<Operation>> ops;
            auto cifm = CreateTensor("CIFM", Shape(1, 1, 1, 10), DataType::Int8, 1);
            auto cifm1 = CreateTensor("CIFM1", Shape(1, 1, 10, 1), DataType::Int8, 2);
            auto cifm2 = CreateTensor("CIFM2", Shape(1, 1, 10, 1), DataType::Int8, 3);
            auto cofm = CreateTensor("COFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto cofm2 = CreateTensor("COFM2", Shape(1, 1, 10, 10), DataType::Int8);
            auto ifm = CreateTensor("IFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto ofm = CreateTensor("OFM", Shape(1, 1, 10, 10), DataType::Int8);
            auto cop = CreateOperation(OpType::SHL, TensorUsage::IFM, cifm, TensorUsage::IFM1, cifm1, TensorUsage::OFM, cofm);
            auto cop2 = CreateOperation(OpType::SHL, TensorUsage::IFM, cofm, TensorUsage::IFM1, cifm2, TensorUsage::OFM, cofm2);
            auto op = CreateOperation(OpType::Add, TensorUsage::IFM, ifm, TensorUsage::IFM1, cofm2, TensorUsage::OFM, ofm);
            ops.push_back(std::move(cop));
            ops.push_back(std::move(cop2));
            ops.push_back(std::move(op));

            // Create graph with ops
            return CreateGraph(ops);
        }();

        GraphOptimiserOptions options;
        const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

        std::vector<Operation *> allOps;

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 3);

        REQUIRE(!optimiser.empty());
        optimiser.back()->Process(graph.get());
        allOps.clear();

        graph->GetAllOperations(allOps);
        REQUIRE(allOps.size() == 1);
        REQUIRE(allOps[0]->Inputs()[TensorUsage::IFM1].tensor->IsConstant());
        auto iview = allOps[0]->Inputs()[TensorUsage::IFM1].tensor->View();
        auto idata = iview.RawData<int8_t>();
        for ( int i = 0; i < allOps[0]->Inputs()[TensorUsage::IFM1].tensor->StorageShape().Elements(); i++ )
        {
            REQUIRE(idata[i] == (1 << 2) << 3);
        }
    }
}

TEST_CASE("test_graphir_optimiser - ReduceSum")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    SECTION("Zero point")
    {
        constexpr int ZP = 10;

        auto graph = [&]()
        {
            std::vector<std::shared_ptr<Operation>> ops;
            auto ifm = CreateTensor("IFM", Shape(1, 4, 4, 25), DataType::Int8);
            auto ofm = CreateTensor("OFM", ifm->StorageShape().WithDepth(1), DataType::Int8);
            auto op = CreateOperation(OpType::ReduceSum, TensorUsage::IFM, ifm, TensorUsage::OFM, ofm);
            op->Input(TensorUsage::IFM)->quantization.zeroPoints.clear();
            op->Input(TensorUsage::IFM)->quantization.zeroPoints.push_back(ZP);
            op->Attribute<axis_attr_t>()->axis = ifm->StorageShape().Size() - 1;
            ops.push_back(std::move(op));

            // Create graph with ops
            return CreateGraph(ops);
        }();

        GraphOptimiserOptions options;
        const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

        REQUIRE(!optimiser.empty());
        optimiser.back()->Process(graph.get());

        SchedulerPacking packing(arch.get(), false);
        auto scheduleOps = packing.Process(graph.get());

        REQUIRE(scheduleOps.size() == 1);
        REQUIRE(scheduleOps[0]->SubOps().size() == 1);
        REQUIRE(scheduleOps[0]->SubOps()[0]->IFM(1)->tensor->IsConstant());
        REQUIRE(scheduleOps[0]->SubOps()[0]->IFM(1)->tensor->bufferView.Elements() == 1);
        REQUIRE(scheduleOps[0]->SubOps()[0]->IFM(1)->tensor->bufferView.StrideBytes() == sizeof(int32_t));
        auto view = scheduleOps[0]->SubOps()[0]->IFM(1)->tensor->bufferView.Values<int32_t>();
        REQUIRE(view[0] == scheduleOps[0]->IFM(0)->shape.Depth() * ZP);
        if ( scheduleOps[0]->IFM(0)->quantization.zeroPoints.size() > 0 )
            REQUIRE(scheduleOps[0]->IFM(0)->quantization.zeroPoints[0] == 0);
    }
}

TEST_CASE("test_graphir_optimiser - transpose removal")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    std::vector<std::shared_ptr<Operation>> ops;
    auto cadd = CreateTensor("CADD", Shape(1, 1, 1, 1), DataType::Int8, 1);
    auto input = CreateTensor("INPUT", Shape(1, 10, 5, 4), DataType::Int8);
    auto ofm1 = CreateTensor("OFM", Shape(1, 10, 5, 4), DataType::Int8);
    auto ofm2 = CreateTensor("OFM", Shape(1, 10, 5, 4), DataType::Int8);
    auto output = CreateTensor("OUTPUT", Shape(1, 10, 5, 4), DataType::Int8);

    // Add->Transpose(none)->Add
    ops.push_back(CreateOperation(OpType::Add, TensorUsage::IFM, input, TensorUsage::IFM1, cadd, TensorUsage::OFM, ofm1));

    ops.push_back(CreateOperation(OpType::Transpose, TensorUsage::IFM, ofm1, TensorUsage::OFM, ofm2));
    transpose_attr_t *attr = ops.back()->Attribute<transpose_attr_t>();
    attr->perm = Shape(0, 1, 2, 3);

    ops.push_back(CreateOperation(OpType::Add, TensorUsage::IFM, ofm2, TensorUsage::IFM1, cadd, TensorUsage::OFM, output));

    auto graph = CreateGraph(ops);

    GraphOptimiserOptions options;
    const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

    optimiser.back()->Process(graph.get());

    std::vector<Operation *> allOps;
    graph->GetAllOperations(allOps);
    REQUIRE(allOps.size() == 2);
    REQUIRE(allOps.front()->Type() == OpType::Add);
    REQUIRE(allOps.back()->Type() == OpType::Add);
    REQUIRE(allOps.front()->Output(TensorUsage::OFM)->tensor == allOps.back()->Input(TensorUsage::IFM)->tensor);
}

TEST_CASE("test_graphir_optimiser - transpose merge")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    std::vector<std::shared_ptr<Operation>> ops;
    auto cadd = CreateTensor("CADD", Shape(1, 1, 1, 1), DataType::Int8, 1);
    auto input = CreateTensor("INPUT", Shape(1, 10, 4, 5), DataType::Int8);
    auto ofm1 = CreateTensor("OFM", Shape(1, 10, 4, 5), DataType::Int8);
    auto ofm2 = CreateTensor("OFM", Shape(1, 10, 5, 4), DataType::Int8);
    auto ofm3 = CreateTensor("OFM", Shape(1, 10, 4, 5), DataType::Int8);
    auto output = CreateTensor("OUTPUT", Shape(1, 10, 4, 5), DataType::Int8);

    // Add->Transpose(there)->Transpose(back)->Add
    ops.push_back(CreateOperation(OpType::Add, TensorUsage::IFM, input, TensorUsage::IFM1, cadd, TensorUsage::OFM, ofm1));

    ops.push_back(CreateOperation(OpType::Transpose, TensorUsage::IFM, ofm1, TensorUsage::OFM, ofm2));
    transpose_attr_t *attr = ops.back()->Attribute<transpose_attr_t>();
    attr->perm = Shape(0, 1, 3, 2);

    ops.push_back(CreateOperation(OpType::Transpose, TensorUsage::IFM, ofm2, TensorUsage::OFM, ofm3));
    attr = ops.back()->Attribute<transpose_attr_t>();
    attr->perm = Shape(0, 1, 3, 2);

    ops.push_back(CreateOperation(OpType::Add, TensorUsage::IFM, ofm3, TensorUsage::IFM1, cadd, TensorUsage::OFM, output));

    auto graph = CreateGraph(ops);

    GraphOptimiserOptions options;
    const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

    optimiser.back()->Process(graph.get());

    // Result Add->Add
    std::vector<Operation *> allOps;
    graph->GetAllOperations(allOps);
    REQUIRE(allOps.size() == 2);
    REQUIRE(allOps.front()->Type() == OpType::Add);
    REQUIRE(allOps.back()->Type() == OpType::Add);
    REQUIRE(allOps.front()->Output(TensorUsage::OFM)->tensor == allOps.back()->Input(TensorUsage::IFM)->tensor);
}

TEST_CASE("test_graphir_optimiser - replace pad by explicit padding")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    // Constant data for the Pad op's paddings tensor
    std::vector<int8_t> paddings = {{
        0,
        0,
        1 /* top */,
        4 /* bottom*/,
        3 /* left */,
        2 /* right */,
        0,
        0,
    }};

    std::vector<std::shared_ptr<Operation>> ops;
    auto padIfm = CreateTensor("INPUT", Shape(1, 7, 7, 3), DataType::Int8, 1);
    auto padParam = CreateTensor("PADPARAM", Shape(8), DataType::Int8, std::move(paddings));
    auto padOfm = CreateTensor("PADOFM", Shape(1, 12, 12, 3), DataType::Int8);
    auto convWeights = CreateTensor("WEIGHTS", Shape(1, 6, 6, 9), DataType::Int8, 42);
    auto convBias = CreateTensor("BIAS", Shape(1, 1, 1, 9), DataType::Int8, 0);
    auto convOfm = CreateTensor("OUTPUT", Shape(1, 7, 7, 9), DataType::Int8);

    // Create Pad op
    ops.push_back(CreateOperation(OpType::Pad, TensorUsage::IFM, padIfm, TensorUsage::Params, padParam, TensorUsage::OFM, padOfm));
    pad_attr_t *attr = ops.back()->Attribute<pad_attr_t>();
    attr->pad_const = 0;

    // Create Conv2D op
    ops.push_back(CreateOperation(OpType::Conv2D, TensorUsage::IFM, padOfm, TensorUsage::Weights, convWeights,
        TensorUsage::Scales, convBias, TensorUsage::OFM, convOfm));
    Kernel kernel = Kernel::UnitKernel().WithSize({6, 6});
    ops.back()->SetKernel(std::make_unique<Kernel>(std::move(kernel)));

    auto graph = CreateGraph(ops);

    GraphOptimiserOptions options;
    const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

    optimiser.back()->Process(graph.get());

    std::vector<Operation *> allOps;
    graph->GetAllOperations(allOps);
    REQUIRE(allOps.size() == 1);
    REQUIRE(allOps[0]->Type() == OpType::Conv2D);
    auto &padding = allOps[0]->Kernel()->Padding();
    REQUIRE(padding.Top() == 1);
    REQUIRE(padding.Left() == 3);
    REQUIRE(padding.Bottom() == 4);
    REQUIRE(padding.Right() == 2);
    REQUIRE(padding.Near() == 0);
    REQUIRE(padding.Far() == 0);
}

TEST_CASE("test_graphir_optimiser - fuse rescale with reshape, before")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    std::vector<std::shared_ptr<Operation>> ops;
    auto input = CreateTensor("INPUT", Shape(1, 8, 2, 1), DataType::Int8);
    auto mulParam = CreateTensor("MUL_PARAM", Shape(1, 1), DataType::Int32, 1073741824);
    auto shiftParam = CreateTensor("SHIFT_PARAM", Shape(1, 1), DataType::Int8, 31);
    auto rescaleOfm = CreateTensor("RESCALE_OFM", Shape(1, 8, 2, 1), DataType::Int8);
    auto reshapeOfm = CreateTensor("RESHAPE_OFM", Shape(1, 4, 4, 1), DataType::Int8);
    auto absOfm = CreateTensor("ABS_OFM", Shape(1, 4, 4, 1), DataType::Int8);

    // Create a RESCALE-RESHAPE-ABS graph
    ops.push_back(CreateOperation(OpType::Rescale, TensorUsage::IFM, input, TensorUsage::Params0, mulParam,
        TensorUsage::Params1, shiftParam, TensorUsage::OFM, rescaleOfm));
    auto *rescaleAttr = ops.back()->Attribute<rescale_attr_t>();
    rescaleAttr->double_round = false;
    rescaleAttr->per_channel = false;
    rescaleAttr->scale32 = true;
    auto *signAttr = ops.back()->Attribute<sign_attr_t>();
    signAttr->input_unsigned = false;
    signAttr->output_unsigned = false;
    ops.push_back(CreateOperation(OpType::Reshape, TensorUsage::IFM, rescaleOfm, TensorUsage::OFM, reshapeOfm));
    ops.push_back(CreateOperation(OpType::Abs, TensorUsage::IFM, reshapeOfm, TensorUsage::OFM, absOfm));

    auto graph = CreateGraph(ops);

    GraphOptimiserOptions options;
    const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

    optimiser.back()->Process(graph.get());

    std::vector<Operation *> allOps;
    graph->GetAllOperations(allOps);
    REQUIRE(allOps.size() == 1);
    REQUIRE(allOps[0]->Type() == OpType::Abs);
    REQUIRE(allOps[0]->Input(TensorUsage::IFM)->SliceShape() == Shape(1, 4, 4, 1));
    REQUIRE(allOps[0]->Input(TensorUsage::IFM)->quantization.zeroPoints[0] == 0);
    REQUIRE(allOps[0]->Input(TensorUsage::IFM)->quantization.scales[0].scale == 1073741824);
    REQUIRE(allOps[0]->Input(TensorUsage::IFM)->quantization.scales[0].shift == 31);
    REQUIRE(allOps[0]->Output(TensorUsage::OFM)->SliceShape() == Shape(1, 4, 4, 1));
}

TEST_CASE("test_graphir_optimiser - fuse rescale with reshape, after")
{
    // Create arch
    auto arch = CreateArchDefault<ArchEthosU85>();
    std::string err = "noerror";
    arch->CheckConfiguration(err);
    REQUIRE(err == "noerror");

    std::vector<std::shared_ptr<Operation>> ops;
    auto input = CreateTensor("INPUT", Shape(1, 4, 4, 1), DataType::Int8);
    auto absOfm = CreateTensor("ABS_OFM", Shape(1, 4, 4, 1), DataType::Int8);
    auto reshapeOfm = CreateTensor("RESHAPE_OFM", Shape(1, 8, 2, 1), DataType::Int8);
    auto mulParam = CreateTensor("MUL_PARAM", Shape(1, 1), DataType::Int32, 1073741824);
    auto shiftParam = CreateTensor("SHIFT_PARAM", Shape(1, 1), DataType::Int8, 31);
    auto rescaleOfm = CreateTensor("RESCALE_OFM", Shape(1, 8, 2, 1), DataType::Int8);

    // Create a ABS-RESHAPE-RESCALE graph
    ops.push_back(CreateOperation(OpType::Abs, TensorUsage::IFM, input, TensorUsage::OFM, absOfm));
    ops.push_back(CreateOperation(OpType::Reshape, TensorUsage::IFM, absOfm, TensorUsage::OFM, reshapeOfm));
    ops.push_back(CreateOperation(OpType::Rescale, TensorUsage::IFM, reshapeOfm, TensorUsage::Params0, mulParam,
        TensorUsage::Params1, shiftParam, TensorUsage::OFM, rescaleOfm));
    auto *rescaleAttr = ops.back()->Attribute<rescale_attr_t>();
    rescaleAttr->double_round = false;
    rescaleAttr->per_channel = false;
    rescaleAttr->scale32 = true;
    auto *signAttr = ops.back()->Attribute<sign_attr_t>();
    signAttr->input_unsigned = false;
    signAttr->output_unsigned = false;

    auto graph = CreateGraph(ops);

    GraphOptimiserOptions options;
    const auto &optimiser = GraphOptimiser::MakeGraphOptimiser(graph->Notation(), arch.get(), options, nullptr);

    optimiser.back()->Process(graph.get());

    std::vector<Operation *> allOps;
    graph->GetAllOperations(allOps);
    REQUIRE(allOps.size() == 1);
    REQUIRE(allOps[0]->Type() == OpType::Abs);
    REQUIRE(allOps[0]->Input(TensorUsage::IFM)->SliceShape() == Shape(1, 4, 4, 1));
    REQUIRE(allOps[0]->Output(TensorUsage::OFM)->SliceShape() == Shape(1, 4, 4, 1));
    REQUIRE(allOps[0]->Output(TensorUsage::OFM)->quantization.zeroPoints[0] == 0);
    REQUIRE(allOps[0]->Output(TensorUsage::OFM)->quantization.scales[0].scale == 1073741824);
    REQUIRE(allOps[0]->Output(TensorUsage::OFM)->quantization.scales[0].shift == 31);
}

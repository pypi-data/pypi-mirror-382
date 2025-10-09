//
// SPDX-FileCopyrightText: Copyright 2021-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>
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

#include "graph_optimiser.hpp"

#include "common/logging.hpp"

#include "architecture/architecture.hpp"
#include "graph.hpp"
#include "graphir_optimiser.hpp"
#include "op_type.hpp"
#include "operation.hpp"
#include "optimiser_utils.hpp"
#include "tensor.hpp"
#include "tflite/tflite_supported_operators.hpp"
#include "tflite_graph_optimiser.hpp"
#include "tosa_graph_optimiser.hpp"

#include <cassert>
#include <iterator>
#include <memory>
#include <stack>
#include <string>
#include <unordered_set>
#include <vector>

#include "include/regor.h"

namespace regor
{

using namespace GraphOptimisation;

std::vector<std::unique_ptr<GraphOptimiser>> GraphOptimiser::MakeGraphOptimiser(
    GraphNotation notation, Architecture *arch, const GraphOptimiserOptions &options, OptimiserDatabase *db)
{
    std::vector<std::unique_ptr<GraphOptimiser>> graphOptimisers;

    switch ( notation )
    {
        case GraphNotation::TFLite:
        {
            std::unique_ptr<TfLiteSupportedOperators> supportedOps;
            arch->Call([&supportedOps, &arch](const std::string &target)
                { supportedOps = MakeSupportedOpsChecker(target, arch->Constraints()); });
            graphOptimisers.emplace_back(
                std::make_unique<TFLiteGraphOptimiser>(arch->Constraints(), std::move(supportedOps), options, db));
        }
        break;

        case GraphNotation::GraphAPI:
            graphOptimisers.emplace_back(std::make_unique<TosaGraphOptimiser>(arch->Constraints(), options, db));
            break;

        default:
            LOG_ERROR("Invalid graph notation");
            assert(false);
    }
    graphOptimisers.emplace_back(std::make_unique<GraphIrOptimiser>(arch->Constraints(), options, db));
    return graphOptimisers;
}


// Some debug functions
#if LOG_TRACE1_ON
Operation *GraphOptimiser::VisitOperatorLog(Graph *const graph, Operation *const operation)
{
    UNUSED(graph);
    if ( GraphOptimiser::Options().verboseGraph )
    {
        LOG_TRACE1("Rewrite operator visits: {0} (@{1})", OpTypeToString(operation->Type()), static_cast<void *>(operation));
        auto *ifmConn = operation->Input(TensorUsage::IFM0);
        LOG_TRACE1(" -- IFM shape: [{0}] read shape: [{2}] offset [{1}]",
            (ifmConn == nullptr ? "" : ifmConn->shape.ToString()), (ifmConn == nullptr ? "" : ifmConn->slice.offset.ToString()),
            (ifmConn == nullptr ? "" : ifmConn->slice.shape.ToString()));

        auto idx = 1;
        auto usage = MakeTensorUsage(TensorUsage::IFM, 1);
        ifmConn = operation->Input(usage);
        while ( ifmConn != nullptr )
        {
            LOG_TRACE1(", [{0}] read shape: [{2}] offset [{1}]", ifmConn->shape.ToString(),
                ifmConn->slice.offset.ToString(), ifmConn->slice.shape.ToString());
            usage = MakeTensorUsage(TensorUsage::IFM, ++idx);
            ifmConn = operation->Input(usage);
        }
        auto *ofmConn = operation->Output(TensorUsage::OFM);
        LOG_TRACE1(" - OFM shape: [{0}] write shape: [{2}] offset [{1}]\n",
            (ofmConn == nullptr ? "" : ofmConn->shape.ToString()), (ofmConn == nullptr ? "" : ofmConn->slice.offset.ToString()),
            (ofmConn == nullptr ? "" : ofmConn->slice.shape.ToString()));
    }
    return operation;
}

Tensor *GraphOptimiser::VisitTensorLog(Graph *const graph, Tensor *const tensor)
{
    UNUSED(graph);
    if ( GraphOptimiser::Options().verboseGraph )
    {
        LOG_TRACE1("Rewrite tensor visits: {0} (@{1}) -- Tensor shape: [{2}]\n", tensor->Name(),
            static_cast<void *>(tensor), tensor->StorageShape().ToString());
    }
    return tensor;
}
#endif

Operation *GraphOptimiser::RecordOperation(Graph *const graph, Operation *const operation)
{
    UNUSED(graph);
    if ( _db )
    {
        _db->SourceOp(operation);
    }
    return operation;
}

Operation *GraphOptimiser::RecordOptimisation(Graph *const graph, Operation *const operation)
{
    UNUSED(graph);
    // Remaining ops probably reference themselves
    if ( _db )
    {
        _db->AddOptimised(*operation, operation);
    }
    return operation;
}

Operation *GraphOptimiser::RemoveReshape(Graph *const graph, Operation *const operation)
{
    Operation *returnOp = operation;
    const OpType opType = operation->Type();
    if ( IsReshape(opType) )
    {
        auto *ifmConn = operation->Input(TensorUsage::IFM0);
        auto *ofmConn = operation->Output(TensorUsage::OFM);
        auto *ifm = ifmConn->tensor.get();
        auto *ofm = ofmConn->tensor.get();

        // Check if ifm/ofm are network ifm/ofm or constant
        bool isIfmConst = ifm->IsConstant();
        // Determine whether the tensors belong to the graph IO using the dedicated helpers on Graph
        bool isIfmSgIfm = graph->IsInput(ifm);
        bool isOfmSgOfm = graph->IsOutput(ofm);
        bool isIfmSgOfm = graph->IsOutput(ifm);

        // Check if ifm/ofm is produced/consumed by a CPU operation
        auto isPassthroughOp = [](const std::shared_ptr<Operation> &op) { return op->Type() == OpType::Passthrough; };
        const bool isOfmCpuIfm =
            std::find_if(ofm->Readers().begin(), ofm->Readers().end(), isPassthroughOp) != ofm->Readers().end();
        const bool isIfmCpuOfm =
            std::find_if(ifm->Writers().begin(), ifm->Writers().end(), isPassthroughOp) != ifm->Writers().end();

        // Inserts a copy op if needed before removing reshapes.
        if ( ((isIfmSgIfm || isIfmSgOfm || isIfmConst || isIfmCpuOfm) && (isOfmSgOfm || isOfmCpuIfm)) ||
             ((ifm->Readers().size() > 1) && (ifm->StorageShape() != ofm->StorageShape() || ifm->AxisOrder() != ofm->AxisOrder())) )
        {
            auto copyOp = InsertCopyOpAfterTensor(ifmConn->tensor, ifmConn->quantization);
            copyOp->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);

            // reset the ifm to reflect the reshape's new ifm
            ifmConn = operation->Input(TensorUsage::IFM0);
            ifm = ifmConn->tensor.get();
            returnOp = copyOp.get();
            RecordOptimisation(*operation, returnOp);
            // Reshape still needs to be removed.
        }

        // Remove the reshape and one of the tensors.
        if ( isOfmSgOfm || isOfmCpuIfm )
        {
            // The OFM is in graph outputs, do not remove this tensor.
            // Bypass by replacing ifm with ofm.
            // Set OFM as output for IFM producers
            ReplaceProducerOutput(ifm->Writers(), ifm, ofmConn->tensor);

            // Set OFM as input to other IFM consumers.
            ReplaceConsumerInput(operation, ifm->Readers(), ifm, ofmConn->tensor);
        }
        else
        {
            // Bypass by replacing ofm with ifm.
            // Set IFM as input to OFM consumers.
            ReplaceConsumerInput(nullptr, ofm->Readers(), ofm, ifmConn->tensor);
            assert(ifm->AxisOrder() == AxisOrder::Unknown || ifm->AxisOrder() == ofm->AxisOrder());

            // This is needed as we use the weight tensor, and not the tensor connection,
            // during weight encode. MLBEDSW-9267
            ifmConn->tensor->SetAxisOrder(ofm->AxisOrder());
            ifmConn->tensor->Reshape(ofm->StorageShape());
        }
        // Remove the reshape from ifm readers and ofm writers.
        // Note the Inputs/Outputs on operation should still be intact to not break the traversal.
        ifm->RemoveReader(operation->shared_from_this());
        ofm->RemoveWriter(operation->shared_from_this());
    }

    return returnOp;
}

void GraphOptimiser::RecordOptimisation(UniqueId fromId, const Operation *op)
{
    if ( _db )
    {
        _db->AddOptimised(fromId, op);
    }
}

void GraphOptimiser::PrintGraph(const Graph *graph, const std::string &label) const
{
    if ( graph != nullptr )
    {
        if ( !label.empty() )
        {
            LOG_PRINT("\n[ {0} ]\n", label);
        }
        std::vector<Operation *> ops;
        graph->GetAllOperations(ops);
        auto idx = 0;
        for ( const auto &op : ops )
        {
            OpType type = op->Type();
            // TODO: This uses the OFM tensor name to identify the operator
            std::string name = op->OFM() ? op->OFM()->Name() : "<unnamed>";
            LOG_PRINT("{0:<5} {1:<20} {2:<30}\n", idx, OpTypeToString(type), name);
            ++idx;
        }
        LOG_PRINT("\n");
    }
}

void GraphOptimiser::PrintQuantization(const Graph *graph, const std::string &label) const
{
    if ( graph != nullptr )
    {
        if ( !label.empty() )
        {
            LOG_PRINT("\n[ {0} ]\n", label);
        }
        std::vector<Operation *> ops;
        graph->GetAllOperations(ops);
        auto op_idx = 0;
        for ( const auto &op : ops )
        {
            OpType type = op->Type();
            std::string name = op->OFM() ? op->OFM()->Name() : "<unnamed>";
            LOG_PRINT("{0} {1} {2}\n", op_idx, OpTypeToString(type), name);

            int tensor_idx = 0;
            for ( const auto &v : op->Inputs() )
            {
                const auto &tens = v.tensor;
                std::string quantization_string = v.quantization.ToString();
                LOG_PRINT("    {0} {1:02} {2} {3} {4}\n", "Input", tensor_idx, DataTypeToString(tens->Type()),
                    quantization_string, tens->Name());
                tensor_idx++;
            }
            tensor_idx = 0;
            for ( const auto &v : op->Outputs() )
            {
                const auto &tens = v.tensor;
                std::string quantization_string = v.quantization.ToString();
                LOG_PRINT("    {0} {1:02} {2} {3} {4}\n", "Output", tensor_idx, DataTypeToString(tens->Type()),
                    quantization_string, tens->Name());
                tensor_idx++;
            }
            ++op_idx;
        }
        LOG_PRINT("\n");
    }
}

void GraphOptimiser::Process(Graph *graph)
{
    if ( _options.verboseGraph )
    {
        PrintGraph(graph, "Before Graph Optimisation");
    }
    OptimiseGraph(graph);
    if ( _options.verboseGraph )
    {
        PrintGraph(graph, "After Graph Optimization");
    }
    if ( _options.verboseQuantization )
    {
        PrintQuantization(graph, "Graph With Tensor Quantization");
    }
}

void GraphOptimiser::ParseGraphOptimiserOptions(GraphOptimiserOptions &opt, IniReader &reader)
{
    // Parse debug settings
    std::string key;
    while ( reader.Begin(key) )
    {
        if ( key == "verbose" )
        {
            opt.verboseGraph = reader.Get<bool>();
        }
        if ( key == "verbose_quantization" )
        {
            opt.verboseQuantization = reader.Get<bool>();
        }

        reader.End();
    }
}

OptimiserDatabase::OptimiserDatabase(Database *db) : _db(db)
{
    _sourceTable = _db->AddTable("source");
    _optTable = _db->AddTable("optimised");
    _groupTable = _db->AddTable("group");
    _cmdTable = _db->AddTable("queue", false);
    _streamTable = _db->AddTable("cmdstream");
    _db->AddColumns(_sourceTable, {"operator", "kernel_w", "kernel_h", "ofm_w", "ofm_h", "ofm_d", "ext_key"});
    _db->AddColumns(_optTable, {"source_id", "operator", "kernel_w", "kernel_h", "ofm_w", "ofm_h", "ofm_d"});
    _db->AddColumns(_groupTable, {"group_id"});
    _db->AddColumns(_cmdTable, {"offset", "cmdstream_id", "optimised_id", "scheduled_id"});
}

Database *OptimiserDatabase::Get()
{
    return _db;
}

int OptimiserDatabase::SourceId(UniqueId uid)
{
    // lookup op in optimised
    auto pos = _optimised.find(uid);
    if ( pos != std::end(_optimised) )
    {
        return std::get<0>(pos->second);
    }
    else if ( auto ptr = _source.find(uid); ptr != std::end(_source) )
    {
        // op is original-op
        return ptr->second;
    }
    return 0;
}

int OptimiserDatabase::OptimisedId(UniqueId uid)
{
    // lookup op in optimised
    auto pos = _optimised.find(uid);
    if ( pos != std::end(_optimised) )
    {
        return std::get<1>(pos->second);
    }
    return 0;
}

int OptimiserDatabase::SourceOp(const Operation *op, int ext_key)
{
    // Op may be a source op or originate from optimised ops in previous graph optimisation pass
    auto id = SourceId(*op);
    if ( id != 0 )
    {
        return id;
    }
    _sourceId++;
    _source.emplace(*op, _sourceId);

    auto k = op->Kernel()->Size();
    auto o = Shape::PadAxes(op->OFM()->StorageShape(), 3, 1);
    _db->AddRow(_sourceTable, _sourceId,
        {OpTypeToString(op->Type()), std::to_string(k.x), std::to_string(k.y), o ? std::to_string(o.Width()) : "",
            o ? std::to_string(o.Height()) : "", o ? std::to_string(o.Depth()) : "", std::to_string(ext_key)});
    return _sourceId;
}

void OptimiserDatabase::AddOptimised(UniqueId fromId, const Operation *to)
{
    assert(to);

    // Locate the source operation Id (if any)
    int sourceId = 0;
    if ( fromId != INVALID_UID )
    {
        // Look for source op in optimised list first and use that op's parent
        // (source replacement doesn't matter)
        auto pos = _optimised.find(fromId);
        if ( pos != _optimised.end() )
        {
            sourceId = std::get<0>(pos->second);
        }
        else
        {
            auto srcPos = _source.find(fromId);
            if ( srcPos != _source.end() )
            {
                sourceId = srcPos->second;
            }
        }
    }

    _optId++;
    _optimised[*to] = std::tuple<int, int>(sourceId, _optId);

    auto k = to->Kernel()->Size();
    Shape o = Shape::PadAxes(to->OFM()->StorageShape(), 3, 1);
    _db->AddRow(_optTable, _optId,
        {std::to_string(sourceId), OpTypeToString(to->Type()), std::to_string(k.x), std::to_string(k.y),
            o ? std::to_string(o.Width()) : "", o ? std::to_string(o.Height()) : "", o ? std::to_string(o.Depth()) : ""});
}

void OptimiserDatabase::AddSubOp(UniqueId primaryUid, UniqueId subOpUid)
{
    assert(primaryUid > 0 && subOpUid > 0);

    _db->AddRow(_groupTable, subOpUid, {std::to_string(primaryUid)});
}

void OptimiserDatabase::AddCommand(UniqueId opId, int stream, int cmdIndex, UniqueId schedId)
{
    auto optID = OptimisedId(opId);
    _db->AddRow(_cmdTable, 0, {std::to_string(4 * cmdIndex), std::to_string(stream), std::to_string(optID), std::to_string(schedId)});
}

int OptimiserDatabase::AddStream()
{
    _streamId++;
    _db->AddRow(_streamTable, _streamId, {});
    return _streamId;
}

}  // namespace regor

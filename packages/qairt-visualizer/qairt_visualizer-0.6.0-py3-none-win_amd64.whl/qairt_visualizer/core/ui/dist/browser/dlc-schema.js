
export const dlc = {};

dlc.v3 = dlc.v3 || {};

dlc.v3.Model = class Model {

    static decode(reader, position) {
        const $ = new dlc.v3.Model();
        $.unk1 = reader.int32_(position, 4, 0);
        $.nodes = reader.tables(position, 6, dlc.v3.Node);
        $.unk2 = reader.array(position, 8, Int32Array);
        $.unk3 = reader.array(position, 10, Int32Array);
        $.attributes = reader.tables(position, 12, dlc.v3.Attribute);
        return $;
    }
};

dlc.v3.Node = class Node {

    static decode(reader, position) {
        const $ = new dlc.v3.Node();
        $.index = reader.int32_(position, 4, 0);
        $.name = reader.string_(position, 6, null);
        $.type = reader.string_(position, 8, null);
        $.inputs = reader.strings_(position, 10);
        $.outputs = reader.strings_(position, 12);
        $.attributes = reader.tables(position, 14, dlc.v3.Attribute);
        return $;
    }
};

dlc.v3.Tensor = class Tensor {

    static decode(reader, position) {
        const $ = new dlc.v3.Tensor();
        $.name = reader.string_(position, 4, null);
        $.shape = reader.array(position, 6, Int32Array);
        $.data = reader.table(position, 8, dlc.v3.TensorData);
        $.attributes = reader.tables(position, 10, dlc.v3.Attribute);
        return $;
    }
};

dlc.v3.TensorData = class TensorData {

    static decode(reader, position) {
        const $ = new dlc.v3.TensorData();
        $.dtype = reader.uint8_(position, 4, 0);
        $.bytes = reader.array(position, 6, Uint8Array);
        $.floats = reader.array(position, 8, Float32Array);
        return $;
    }
};

dlc.v3.Attribute = class Attribute {

    static decode(reader, position) {
        const $ = new dlc.v3.Attribute();
        $.name = reader.string_(position, 4, null);
        $.type = reader.uint8_(position, 6, 0);
        $.bool_value = reader.bool_(position, 8, false);
        $.int32_value = reader.int32_(position, 10, 0);
        $.uint32_value = reader.uint32_(position, 12, 0);
        $.float32_value = reader.float32_(position, 14, 0);
        $.string_value = reader.string_(position, 16, null);
        $.unk6 = reader.array(position, 18, Int8Array);
        $.byte_list = reader.array(position, 20, Int8Array);
        $.int32_list = reader.array(position, 22, Int32Array);
        $.float32_list = reader.array(position, 24, Float32Array);
        $.unk10 = reader.array(position, 26, Int8Array);
        $.attributes = reader.tables(position, 28, dlc.v3.Attribute);
        return $;
    }
};

dlc.v3.Activation = {
    ReLU: 1,
    Sigmoid: 3
};

dlc.v3.ModelParameters = class ModelParameters {

    static decode(reader, position) {
        const $ = new dlc.v3.ModelParameters();
        $.nodes = reader.tables(position, 4, dlc.v3.NodeParameters);
        return $;
    }
};

dlc.v3.NodeParameters = class NodeParameters {

    static decode(reader, position) {
        const $ = new dlc.v3.NodeParameters();
        $.name = reader.string_(position, 4, null);
        $.weights = reader.tables(position, 6, dlc.v3.Tensor);
        return $;
    }
};

dlc.v4 = dlc.v4 || {};

dlc.v4.Model = class Model {

    static decode(reader, position) {
        const $ = new dlc.v4.Model();
        $.graphs = reader.tables(position, 4, dlc.v4.Graph);
        return $;
    }
};

dlc.v4.Graph = class Graph {

    static decode(reader, position) {
        const $ = new dlc.v4.Graph();
        $.name = reader.string_(position, 4, null);
        $.nodes = reader.tables(position, 6, dlc.v4.Node);
        $.tensors = reader.tables(position, 8, dlc.v4.Tensor);
        // QAIRT Netron: Identifying IO tensors and creating new node for the same
        $.tensors.forEach((tensor) => {
            const isInput = tensor.location === 0;
            const isOutput = tensor.location === 1;
            if (isInput || isOutput) {
                const newNode = new dlc.v4.Node();
                const name = tensor.name;
                newNode.name = name;
                newNode.inputs = [isInput ? name : ''];
                newNode.outputs = [isOutput ? name : ''];
                newNode.type = isInput ? 'Input' : 'Output';
                $.nodes.push(newNode);
            }
        });
        // QAIRT Netron END
        return $;
    }
};

dlc.v4.Node = class Node {

    static decode(reader, position) {
        const $ = new dlc.v4.Node();
        $.name = reader.string_(position, 4, null);
        $.type = reader.string_(position, 6, null);
        $.inputs = reader.strings_(position, 8);
        $.outputs = reader.strings_(position, 10);
        $.attributes = reader.tables(position, 12, dlc.v4.Attribute);
        return $;
    }
};

// QAIRT Netron: Fix property names and reader methods according to FlatBuffers schema: https://review.qualcomm.com/plugins/gitiles/zsnpe/ml/+/refs/heads/mainline/DnnSerializationV2/src/DlcV4/NetworkCommon.fbs
dlc.v4.Attribute = class Attribute {

    static decode(reader, position) {
        const $ = new dlc.v4.Attribute();
        $.name = reader.string_(position, 4, null);
        $.kind = reader.int32_(position, 6, 0);
        $.flag = reader.uint8_(position, 8, 0);
        $.value = reader.table(position, 10, dlc.v4.ScalarData);
        $.tensor = reader.table(position, 12, dlc.v4.Tensor);
        return $;
    }
};

dlc.v4.ScalarData = class ScalarData {

    static decode(reader, position) {
        const $ = new dlc.v4.ScalarData();
        $.kind = reader.uint32_(position, 4, 0);
        $.int = reader.int64_(position, 6, 0);
        $.float = reader.float64_(position, 8, 0);
        $.string = reader.string_(position, 10, null);
        return $;
    }
};

dlc.v4.Tensor = class Tensor {

    static decode(reader, position) {
        const $ = new dlc.v4.Tensor();
        $.unk1 = reader.uint32_(position, 4, 0);
        $.name = reader.string_(position, 6, null);
        $.location = reader.int32_(position, 8, 0);
        $.shape = reader.array(position, 10, Int32Array);
        $.unk2 = reader.int32_(position, 12, 0);
        $.quantizationData = reader.table(position, 14, dlc.v4.QuantizationData);
        $.dtype = reader.int32_(position, 16, 0);
        $.output_dtype = reader.int32_(position, 18, 0);
        $.unk6 = reader.uint8_(position, 20, 0);
        return $;
    }
};

dlc.v4.QuantizationData  = class QuantizationData  {

    static decode(reader, position) {
        const $ = new dlc.v4.QuantizationData();
        $.type = reader.uint32_(position, 4, 0);
        $.isOverriden = reader.bool(position, 6, false);
        $.qInfo = reader.table(position, 8, dlc.v4.FxpData);
        $.axisQInfo = reader.table(position, 10, dlc.v4.AxisFxpData);
        $.bq_info = reader.table(position, 12, dlc.v4.BQEncodingInfo);
        $.lpbq_info = reader.table(position, 14, dlc.v4.LPBQEncodingInfo);
        $.vector_info = reader.table(position, 16, dlc.v4.VectorEncodingInfo);
        return $;
    }
};

dlc.v4.FxpData = class FxpData {

    static decode(reader, position) {
        const $ = new dlc.v4.FxpData();
        $.bw = reader.uint32_(position, 4, 0);
        $.min = reader.float32_(position, 6, 0);
        $.max = reader.float32_(position, 8, 0);
        $.scale = reader.float32_(position, 10, 0);
        $.offset = reader.int32_(position, 12, 0);
        $.isSymmetric = reader.bool_(position, 14, false);
        return $;
    }
};

dlc.v4.AxisFxpData = class AxisFxpData {

    static decode(reader, position) {
        const $ = new dlc.v4.AxisFxpData();
        $.axis = reader.int32_(position, 4, 0);
        $.qInfo = reader.tables(position, 6, dlc.v4.FxpData);
        return $;
    }
};

dlc.v4.BQEncodingInfo = class BQEncodingInfo {

    static decode(reader, position) {
        const $ = new dlc.v4.BQEncodingInfo();
        $.axis = reader.int32_(position, 4, 0);
        $.block_axis = reader.int32_(position, 6, 0);
        $.block_size = reader.uint32_(position, 8, 0);
        $.bit_width = reader.uint32_(position, 10, 0);
        $.is_symmetric = reader.bool_(position, 12, false);
        $.is_stripped = reader.bool_(position, 14, false);
        $.scale_offset_data_position = reader.table(position, 16, dlc.v4.DataPosition);
        $.float_range_data_position = reader.table(position, 18, dlc.v4.DataPosition);
        return $;
    }
};

dlc.v4.LPBQEncodingInfo = class LPBQEncodingInfo {

    static decode(reader, position) {
        const $ = new dlc.v4.LPBQEncodingInfo();
        $.axis = reader.int32_(position, 4, 0);
        $.enc_infos = reader.tables(position, 6, dlc.v4.FxpData);
        $.num_blocks_per_axis = reader.uint32_(position, 8, 0);
        $.block_size = reader.uint32_(position, 10, 0);
        $.block_scale_bitwidth = reader.uint8_(position, 12, 0);
        return $;
    }
};

dlc.v4.VectorEncodingInfo = class VectorEncodingInfo {

    static decode(reader, position) {
        const $ = new dlc.v4.VectorEncodingInfo();
        $.axis = reader.int32_(position, 4, 0);
        $.enc_infos = reader.tables(position, 6, dlc.v4.FxpData);
        $.rows_per_block = reader.uint32_(position, 8, 0);
        $.columns_per_block = reader.uint32_(position, 10, 0);
        $.row_axis = reader.int8_(position, 12, 0);
        $.column_axis = reader.int8_(position, 14, 0);
        $.vector_dimension = reader.uint8_(position, 16, 0);
        $.vector_stride = reader.uint8_(position, 18, 0);
        $.index_bitwidth = reader.uint8_(position, 20, 0);
        return $;
    }
};
// QAIRT Netron END

dlc.v4.ModelParameters64 = class ModelParameters64 {

    static decode(reader, position) {
        const $ = new dlc.v4.ModelParameters64();
        $.buffers = reader.tables(position, 4, dlc.v4.Buffer);
        $.params = reader.array(position, 6, Uint8Array);
        return $;
    }
};

dlc.v4.ModelParameters = class ModelParameters {

    static decode(reader, position) {
        const $ = new dlc.v4.ModelParameters();
        $.graphs = reader.tables(position, 4, dlc.v4.GraphParameters);
        return $;
    }
};

dlc.v4.GraphParameters = class GraphParameters {

    static decode(reader, position) {
        const $ = new dlc.v4.GraphParameters();
        $.name = reader.string_(position, 4, null);
        $.tensors = reader.tables(position, 6, dlc.v4.TensorData);
        $.nodes = reader.tables(position, 8, dlc.v4.NodeParameters);
        return $;
    }
};

dlc.v4.NodeParameters = class NodeParameters {

    static decode(reader, position) {
        const $ = new dlc.v4.NodeParameters();
        $.tensors = reader.tables(position, 4, dlc.v4.TensorData);
        return $;
    }
};

dlc.v4.TensorData = class TensorData {

    static decode(reader, position) {
        const $ = new dlc.v4.TensorData();
        $.name = reader.string_(position, 4, null);
        $.bytes = reader.array(position, 6, Uint8Array);
        $.data_index = reader.int64_(position, 8, 0); // QAIRT Netron: Add data_index metadata describing the tensor's position within the Flatbuffer
        $.data_position = reader.table(position, 10, dlc.v4.DataPosition); // QAIRT Netron: Add data_position metadata describing the tensor's position in model.params.bin
        return $;
    }
};

// QAIRT Netron: Add DataPosition describing the file offset and size of the tensor data in model.params.bin
dlc.v4.DataPosition = class DataPosition {

    static decode(reader, position) {
        const $ = new dlc.v4.DataPosition();
        $.offset = Number(reader.int64_(position, 4, 0));
        $.size = Number(reader.int64_(position, 6, 0));
        return $;
    }
};
// QAIRT Netron END

dlc.v4.Buffer = class Buffer {

    static decode(reader, position) {
        const $ = new dlc.v4.Buffer();
        $.bytes = reader.array(position, 4, Uint8Array);
        return $;
    }
};


import * as flatbuffers from './flatbuffers.js';
import * as text from './text.js';

const dlc = {};

// QAIRT Netron: Define elementwise operations and padding size strategies mappings
dlc.ElementWiseNeuronOperations = {
    0: 'ELU',
    1: 'GELU',
    2: 'HARD_SIGMOID',
    3: 'HARD_SWISH',
    4: 'RELU',
    5: 'RELU_MIN_MAX',
    6: 'SIGMOID',
    7: 'SOFTPLUS',
    8: 'TANH'
};

dlc.EltwiseBinaryOperations = {
    0: 'ADD',
    1: 'AND',
    2: 'DIVIDE',
    3: 'EQUAL',
    4: 'FLOOR_DIV',
    5: 'FMOD',
    6: 'GREATER',
    7: 'GREATER_EQUAL',
    8: 'LESS',
    9: 'LESS_EQUAL',
    10: 'MAXIMUM',
    11: 'MINIMUM',
    12: 'MOD',
    13: 'MULTIPLY',
    14: 'NOT_EQUAL',
    15: 'OR',
    16: 'POWER',
    17: 'SQUARED_DIFFERENCE',
    18: 'SUBTRACT',
    19: 'XOR',
};

dlc.ElementWiseUnaryOperations = {
    0: 'ABS',
    1: 'ASIN',
    2: 'ATAN',
    3: 'CEIL',
    4: 'COS',
    5: 'EXP',
    6: 'FLOOR',
    7: 'LOG',
    8: 'NEG',
    9: 'NOT',
    10: 'RECIPROCAL',
    11: 'ROUND',
    12: 'RSQRT',
    13: 'SIGN',
    14: 'SIN',
    15: 'SQRT',
};

dlc.elementWiseOpMappings = {
    'ElementWiseNeuron': dlc.ElementWiseNeuronOperations,
    'Eltwise_Binary': dlc.EltwiseBinaryOperations,
    'ElementWiseUnary': dlc.ElementWiseUnaryOperations,
};

dlc.PaddingSizeStrategies = {
    0: 'implicit valid',
    1: 'implicit same begin',
    2: 'implicit same end',
    3: 'explicit righthanded',
    4: 'explicit',
    5: 'explicit floor',
    255: 'invalid',
};
// QAIRT Netron END

dlc.ModelFactory = class {

    async match(context) {
        const container = await dlc.Container.open(context);
        if (container) {
            return context.set('dlc', container);
        }
        return null;
    }

    async open(context) {
        dlc.schema = await context.require('./dlc-schema');
        dlc.schema = dlc.schema.dlc;
        await context.value.read();
        const metadata = await context.metadata('dlc-metadata.json');
        return new dlc.Model(metadata, context.value);
    }
};

dlc.Model = class {

    constructor(metadata, target) {
        this.format = target.format;
        this.metadata = [];
        if (target.metadata.size > 0) {
            const version = target.metadata.get('model-version');
            if (version) {
                this.version = version;
            }
            const converter = target.metadata.get('converter-command');
            if (converter) {
                const source = converter.split(' ').shift().trim();
                if (source.length > 0) {
                    const version = target.metadata.get('converter-version');
                    this.source = version ? `${source} v${version}` : source;
                }
            }
            const license = target.metadata.get('model-copyright');
            if (license && license !== 'N/A') {
                this.metadata.push(new dlc.Argument('license', license));
            }
        }
        for (const graph of target.graphs) {
            this.modules = [new dlc.Graph(metadata, target.version, graph)];
        }
    }
};

dlc.Graph = class {

    constructor(metadata, version, graph) {
        this.name = graph.name;
        this.inputs = [];
        this.outputs = [];
        const values = new Map();
        switch (version.major) {
            case 3: {
                for (const node of graph.nodes) {
                    for (const name of node.inputs) {
                        if (!values.has(name)) {
                            values.set(name, {});
                        }
                    }
                    for (const name of node.outputs) {
                        if (!values.has(name)) {
                            values.set(name, {});
                        }
                    }
                    let shapes = new Array(node.outputs.length);
                    for (const attribute of node.attributes) {
                        if (attribute.name === 'OutputDims' &&
                            Array.isArray(attribute.attributes) && attribute.attributes.length > 0) {
                            shapes = attribute.data;
                            break;
                        }
                    }
                    for (let i = 0; i < node.outputs.length; i++) {
                        const name = node.outputs[i];
                        const value = values.get(name);
                        if (!value.shape && i < shapes.length) {
                            value.shape = shapes[i];
                        }
                    }
                }
                break;
            }
            case 4: {
                for (const tensor of graph.tensors) {
                    values.set(tensor.name, tensor);
                }
                break;
            }
            default: {
                break;
            }
        }
        for (const [name, tensor] of values) {
            const type = tensor.shape ? new dlc.TensorType(tensor.dtype, tensor.shape) : null;
            const initializer = tensor.data && tensor.data ? new dlc.Tensor(tensor.name, type, tensor.data) : null;
            const value = new dlc.Value(name, type, initializer, tensor); // QAIRT Netron: Pass tensor object to dlc.Value
            values.set(name, value);
        }
        const value = (name) => {
            if (!values.has(name)) {
                values.set(name, new dlc.Value(name));
            }
            return values.get(name);
        };
        this.nodes = [];
        for (const node of graph.nodes) {
            if (node.type === 'Input') {
                this.inputs.push(new dlc.Argument(node.name, node.inputs.map((input) => value(input))));
                continue;
            }
            // QAIRT Netron: Added missing support for output nodes
            if (node.type === 'Output') {
                this.outputs.push(new dlc.Argument(node.name, node.outputs.map((output) => value(output))));
                continue;
            }
            // QAIRT Netron END
            this.nodes.push(new dlc.Node(metadata, version, node, value));
        }
    }
};

dlc.Argument = class {

    constructor(name, value, type) {
        this.name = name;
        this.value = value;
        this.type = type || null;
    }
};

dlc.Value = class {

    constructor(name, type, initializer, tensor) { // QAIRT Netron: Add tensor param
        if (typeof name !== 'string') {
            throw new dlc.Error(`Invalid value identifier '${JSON.stringify(name)}'.`);
        }
        this.name = name;
        this.type = type;
        this.initializer = initializer;
        // QAIRT Netron: Set quantization info if it exists on the tensor object
        const quantizationData = tensor?.quantizationData;
        const { qInfo, ...axisInfo } = quantizationData?.axisQInfo || {};
        const { enc_infos, ...lpbqInfo } = quantizationData?.lpbq_info || {};
        const encodingInfo = quantizationData?.qInfo || qInfo || enc_infos;
        const UNDEFINED_ENCODING_ENUM = 0x7FFFFFFF;
        if (quantizationData?.type !== UNDEFINED_ENCODING_ENUM) {
            this.qnnQuantization = {
                encodingType: quantizationData.type,
                encodingInfo,
                axisInfo,
                lpbqInfo,
            };
        }
        // QAIRT Netron END
    }
};

dlc.Node = class {

    constructor(metadata, version, obj, value) {
        this.type = metadata.type(obj.type);
        this.name = obj.name;
        this.inputs = [];
        this.outputs = [];
        this.attributes = [];
        const inputs = Array.isArray(obj.inputs) ? Array.from(obj.inputs).map((name) => value(name)) : [];
        if (version !== 3 && Array.isArray(this.type.inputs) && inputs.length === this.type.inputs.length) {
            for (let i = 0; i < inputs.length; i++) {
                const argument = new dlc.Argument(this.type.inputs[i].name, [inputs[i]]);
                this.inputs.push(argument);
            }
        } else if (inputs.length > 0) {
            const argument = new dlc.Argument(inputs.length === 1 ? 'input' : 'inputs', inputs);
            this.inputs.push(argument);
        }
        const outputs = Array.isArray(obj.outputs) ? Array.from(obj.outputs).map((name) => value(name)) : [];
        if (Array.isArray(this.type.outputs) && outputs.length === this.type.outputs.length) {
            for (let i = 0; i < outputs.length; i++) {
                const argument = new dlc.Argument(this.type.outputs[i].name, [outputs[i]]);
                this.outputs.push(argument);
            }
        } else if (outputs.length > 0) {
            const argument = new dlc.Argument(outputs.length === 1 ? 'output' : 'outputs', outputs);
            this.outputs.push(argument);
        }
        if (obj.attributes) {
            for (const attr of obj.attributes) {
                if (attr.name === 'OutputDims') {
                    continue;
                }
                const schema = metadata.attribute(obj.type, attr.name);
                let type = attr.type;
                switch (type) {
                    case 'tensor': {
                        const tensor = attr.data;
                        const type = new dlc.TensorType(tensor.dtype, tensor.shape);
                        value = new dlc.Tensor(tensor.name, type, tensor.data);
                        break;
                    }
                    default: {
                        value = attr.data;
                    }
                }
                if (schema && schema.type) {
                    type = schema.type;
                    value = dlc.Utility.enum(version, type, value);
                }
                const attribute = new dlc.Argument(attr.name, value, type);
                this.attributes.push(attribute);
            }
        }
        if (obj.weights) {
            for (const tensor of obj.weights) {
                const type = new dlc.TensorType(tensor.data.dtype, tensor.shape);
                const value = new dlc.Value('', type, new dlc.Tensor(tensor.name, type, tensor.data));
                this.inputs.push(new dlc.Argument(tensor.name, [value]));
            }
        }
    }
};

dlc.TensorType = class {

    constructor(dataType, shape) {
        this.dataType = dataType || '?';
        this.shape = new dlc.TensorShape(shape);
    }

    toString() {
        return this.dataType + this.shape.toString();
    }
};

dlc.TensorShape = class {

    constructor(dimensions) {
        this.dimensions = Array.from(dimensions);
    }

    toString() {
        if (Array.isArray(this.dimensions) && this.dimensions.length > 0) {
            return `[${this.dimensions.map((dimension) => dimension.toString()).join(',')}]`;
        }
        return '';
    }
};

dlc.Tensor = class {

    constructor(name, type, data) {
        this.name = name;
        this.type = type;
        if (data instanceof Uint8Array) {
            this.encoding = '<';
            this.values = data;
        } else {
            this.encoding = '|';
            switch (type.dataType) {
                case 'uint8': this.values = data.bytes; break;
                case 'float32': this.values = data.floats; break;
                default: throw new dlc.Error(`Unsupported tensor data type '${type.dataType}'.`);
            }
        }
    }
};

dlc.Container = class {

    static async open(context) {
        const entries = await context.peek('zip');
        if (entries instanceof Map) {
            const model = entries.get('model');
            const params = entries.get('model.params');
            const paramsBin = entries.get('model.params.bin');  // QAIRT Netron: Check for model.params.bin file which was added in DLC 4.1.0
            const metadata = entries.get('dlc.metadata');
            if (model) {
                const signature = dlc.Container._signature(model);
                if (signature && (signature.identifier === 'NETD' || signature.major === 2)) {
                    return new dlc.Container(context, model, params, paramsBin, metadata); // QAIRT Netron: Check for model.params.bin file which was added in DLC 4.1.0
                }
            }
            if (params) {
                const signature = dlc.Container._signature(params);
                if (signature && signature.identifier === 'NETP') {
                    return new dlc.Container(context, model, params, paramsBin, metadata); // QAIRT Netron: Check for model.params.bin file which was added in DLC 4.1.0
                }
            }
            return null;
        }
        const stream = context.stream;
        const signature = dlc.Container._signature(stream);
        switch (signature.identifier) {
            case 'NETD':
                return new dlc.Container(context, stream, undefined, undefined);
            case 'NETP':
            case 'NR64':
                return new dlc.Container(context, undefined, stream, undefined);
            default:
                return null;
        }
    }

    // QAIRT Netron: Store params bin data
    constructor(context, model, params, paramsBin, metadata) {
        this.context = context;
        this._model = model;
        this._params = params;
        this._paramsBin = paramsBin;
        this._metadata = metadata;
    }

    async read() {
        if (this._model === undefined) {
            this._model = await this._fetch('model');
        }
        if (this._params === undefined) {
            this._params = await this._fetch('model.params');
        }
        if (this._metadata === undefined) {
            this._metadata = await this._fetch('dlc.metadata');
        }
        delete this.context;
        this.graphs = [];
        this.metadata = new Map();
        if (this._model) {
            this.format = 'DLC';
            const stream = this._model;
            delete this._model;
            const signature = dlc.Container._signature(stream);
            if (signature.major === 2) {
                throw new dlc.Error("File contains undocumented DLC v2 data.");
            } else if (signature.identifier === 'NETD' && (signature.major === 3 || signature.major === undefined)) {
                this.version = { major: signature.major || 3, minor: signature.minor || 0 };
                this.graph = dlc.Container._model3(stream, signature.offset);
                this.graphs = [this.graph];
            } else if (signature.identifier === 'NETD' && signature.major === 4) {
                this.version = { major: signature.major, minor: signature.minor };
                this.graphs = dlc.Container._model4(stream);
            } else {
                const buffer = stream.peek(Math.min(stream.length, 16));
                const content = Array.from(buffer).map((c) => (c < 16 ? '0' : '') + c.toString(16)).join('');
                throw new dlc.Error(`File contains undocumented '${content}' data.`);
            }
        }
        if (this._params) {
            this.format = this.format || 'DLC Weights';
            const stream = this._params;
            delete this._params;
            const signature = dlc.Container._signature(stream);
            if (signature.major === 2) {
                throw new dlc.Error("File contains undocumented DLC v2 data.");
            } else if (signature.identifier === 'NETP' && (signature.major === 3 || signature.major === undefined)) {
                this.version = this.graphs.length > 0 ? this.version : { major: signature.major || 3, minor: signature.minor || 0 };
                this.graph = dlc.Container._params3(stream, signature, this.graph);
                this.graphs = [this.graph];
            } else if ((signature.identifier === 'NETP' || signature.identifier === 'NR64') && signature.major === 4) {
                dlc.Container._params4(stream, this.graphs, signature, this._paramsBin?.peek()); // QAIRT Netron: Pass params bin data
            } else {
                const buffer = stream.peek(Math.min(stream.length, 16));
                const content = Array.from(buffer).map((c) => (c < 16 ? '0' : '') + c.toString(16)).join('');
                throw new dlc.Error(`File contains undocumented '${content}' data.`);
            }
        }
        if (this._metadata) {
            const stream = this._metadata;
            delete this._metadata;
            const reader = text.Reader.open(stream);
            for (;;) {
                const line = reader.read('\n');
                if (line === undefined) {
                    break;
                }
                const index = line.indexOf('=');
                if (index === -1) {
                    break;
                }
                const key = line.substring(0, index);
                const value = line.substring(index + 1);
                this.metadata.set(key, value);
            }
        }
    }

    static _model3(stream, offset) {
        let model = null;
        try {
            const buffer = new Uint8Array(offset > 0 ? stream.peek().subarray(offset) : stream.peek());
            const reader = flatbuffers.BinaryReader.open(buffer);
            model = dlc.schema.v3.Model.decode(reader, reader.root);
        } catch (error) {
            const message = error && error.message ? error.message : error.toString();
            throw new dlc.Error(`File format is not dlc.v3.NETD (${message.replace(/\.$/, '')}).`);
        }
        model.tensors = [];
        const updateAttribute = (attr) => {
            switch (attr.type) {
                case 1: return ['boolean',   attr.bool_value];
                case 2: return ['int32',     attr.int32_value];
                case 3: return ['uint32',    attr.uint32_value];
                case 4: return ['float32',   attr.float32_value];
                case 5: return ['string',    attr.string_value];
                case 7: return ['byte[]',    Array.from(attr.byte_list)];
                case 8: return ['int32[]',   Array.from(attr.int32_list)];
                case 9: return ['float32[]', Array.from(attr.float32_list)];
                case 11: {
                    const obj = {};
                    let index = 0;
                    let list = true;
                    for (const attribute of attr.attributes) {
                        const name = attribute.name;
                        const [, data] = updateAttribute(attribute);
                        obj[name] = data;
                        list = list && index.toString() === attribute.name;
                        index++;
                    }
                    return list ? ['', Object.values(obj)] : ['', obj];
                }
                default:
                    throw new dlc.Error(`Unsupported attribute type '${attr.type}'.`);
            }
        };
        for (const node of model.nodes) {
            for (const attribute of node.attributes) {
                const [type, data] = updateAttribute(attribute);
                attribute.type = type;
                attribute.data = data;
            }
        }
        return model;
    }

    static _model4(stream) {
        let model = null;
        try {
            const buffer = new Uint8Array(stream.peek().subarray(8));
            const reader = flatbuffers.BinaryReader.open(buffer);
            model = dlc.schema.v4.Model.decode(reader, reader.root);
        } catch (error) {
            const message = error && error.message ? error.message : error.toString();
            throw new dlc.Error(`File format is not dlc.v4.NETD (${message.replace(/\.$/, '')}).`);
        }
        const dataType = (value) => {
            switch (value) {
                case 0x0008: return 'int8';
                case 0x0016: return 'int16';
                case 0x0032: return 'int32';
                case 0x0064: return 'int64';
                case 0x0108: return 'uint8';
                case 0x0116: return 'uint16';
                case 0x0132: return 'uint32';
                case 0x0164: return 'uint64';
                case 0x0216: return 'float16';
                case 0x0232: return 'float32';
                case 0x0304: return 'qint4';
                case 0x0308: return 'qint8';
                case 0x0316: return 'qint16';
                case 0x0332: return 'qint32';
                case 0x0404: return 'quint4';
                case 0x0408: return 'quint8';
                case 0x0416: return 'quint16';
                case 0x0432: return 'quint32';
                case 0x0508: return 'boolean';
                case 0x0608: return 'string';
                case 0x7fffffff: return 'undefined';
                default: throw new dlc.Error(`Unsupported data type '${JSON.stringify(value)}'.`);
            }
        };
        const updateTensor = (tensor) => {
            tensor.dtype = dataType(tensor.dtype);
            tensor.output_dtype = dataType(tensor.output_dtype);
        };
        for (const graph of model.graphs) {
            for (const node of graph.nodes) {
                for (const attribute of node.attributes || []) { // QAIRT Netron : Added or condition as I/O nodes will not have attributes
                    switch (attribute.kind) {
                        case 0: {
                            const value = attribute.value;
                            // QAIRT Netron: Modify attribute value property names according to the ScalarData table
                            switch (value.kind) {
                                case 0x7fffffff:
                                    attribute.data = value.string;
                                    attribute.type = 'string';
                                    break;
                                case 0x0032:
                                    attribute.data = value.int;
                                    break;
                                case 0x0108:
                                    attribute.data = value.int;
                                    attribute.type = 'int8';
                                    break;
                                case 0x0132:
                                    attribute.data = value.int;
                                    attribute.type = 'int32';
                                    break;
                                case 0x0232:
                                    attribute.data = value.float;
                                    attribute.type = 'float32';
                                    break;
                                case 0x0508:
                                    attribute.data = value.int !== 0;
                                    attribute.type = 'boolean';
                                    break;
                                case 0x0608:
                                    attribute.data = value.string;
                                    attribute.type = 'string';
                                    break;
                                default:
                                    throw new dlc.Error(`Unknown attribute value kind '${value.kind}'.`);
                            }
                            // QAIRT Netron END
                            break;
                        }
                        case 1: {
                            const tensor = attribute.tensor;
                            updateTensor(tensor);
                            attribute.type = 'tensor';
                            attribute.data = tensor;
                            break;
                        }
                        default: {
                            throw new dlc.Error(`Unknown attribute kind '${attribute.kind}'.`);
                        }
                    }
                    // QAIRT Netron: Added support for mapping of elementwise operation and padding size strategy parameters
                    if (attribute.name === 'operation') {
                        const elementWiseOp = dlc.elementWiseOpMappings[node.type];
                        if (elementWiseOp) {
                            attribute.data = elementWiseOp[Number(attribute.data)] || attribute.data;
                        }
                    } else if (attribute.name === 'padding_size_strategy') {
                        attribute.data = dlc.PaddingSizeStrategies[Number(attribute.data)] || attribute.data;
                    }
                    // QAIRT Netron END
                }
            }
            for (const tensor of graph.tensors) {
                updateTensor(tensor);
            }
        }
        return model.graphs;
    }

    static _params3(stream, signature, graph) {
        let params = null;
        try {
            const buffer = new Uint8Array(signature === 'NETP' ? stream.peek() : stream.peek().subarray(8));
            const reader = flatbuffers.BinaryReader.open(buffer);
            params = dlc.schema.v3.ModelParameters.decode(reader, reader.root);
        } catch (error) {
            const message = error && error.message ? error.message : error.toString();
            throw new dlc.Error(`File format is not dlc.v3.NETP (${message.replace(/\.$/, '')}).`);
        }
        if (!graph) {
            graph = new dlc.schema.v3.ModelParameters();
            graph.nodes = new Array(params.nodes.length);
            graph.tensors = [];
            for (let i = 0; i < graph.nodes.length; i++) {
                const node = new dlc.schema.v3.Node();
                node.type = 'Weights';
                node.name = params.nodes[i].name;
                node.inputs = [];
                node.outputs = [];
                node.attributes = [];
                graph.nodes[i] = node;
            }
        }
        const dataType = (value) => {
            switch (value) {
                case null: return '?';
                case 6: return 'uint8';
                case 9: return 'float32';
                default:
                    throw new dlc.Error(`Unsupported data type '${JSON.stringify(value)}'.`);
            }
        };
        const weights = new Map(params.nodes.map((node) => [node.name, node.weights]));
        for (const node of graph.nodes) {
            if (weights.has(node.name)) {
                const tensors = weights.get(node.name);
                for (const tensor of tensors) {
                    tensor.data.dtype = dataType(tensor.data.dtype);
                }
                node.weights = tensors;
            }
        }
        return graph;
    }

    // QAIRT Netron: Use params bin data
    static _params4(stream, graphs, signature, paramsBinBuffer) {
        let buffer = stream.peek().subarray(8);
        let buffers = null;
        if (signature.major === 4 && signature.identifier === 'NR64') {
            try {
                const reader = flatbuffers.BinaryReader.open(buffer);
                const nr64 = dlc.schema.v4.ModelParameters64.decode(reader, reader.root);
                buffers = nr64.buffers;
                buffer = nr64.params;
            } catch (error) {
                const message = error && error.message ? error.message : error.toString();
                throw new dlc.Error(`File format is not dlc.v4.NR64 (${message.replace(/\.$/, '')}).`);
            }
        }
        let params = null;
        try {
            const reader = flatbuffers.BinaryReader.open(buffer);
            params = dlc.schema.v4.ModelParameters.decode(reader, reader.root);
        } catch (error) {
            const message = error && error.message ? error.message : error.toString();
            throw new dlc.Error(`File format is not dlc.v4.NETP (${message.replace(/\.$/, '')}).`);
        }
        if (graphs.length === 0) {
            throw new dlc.Error('Model definition not available.');
        }
        const weights = new Map(params.graphs.map((graph) => [graph.name, graph]));
        for (const graph of graphs) {
            const params = weights.get(graph.name);
            const tensors = new Map(params.tensors.map((tensor) => [tensor.name, tensor]));
            graph.tensors.sort((a, b) => a.name.localeCompare(b.name));
            for (const tensor of graph.tensors) {
                if (tensor.location === 4) {
                    // QAIRT Netron: Use custom logic to get tensor data
                    tensor.data = this.getTensorData(tensors, tensor, paramsBinBuffer, buffers);
                }
            }
            for (let i = 0; i < graph.nodes.length; i++) {
                const node = graph.nodes[i];
                // QAIRT Netron: Added check for I/O nodes, as they will not have tensors and attributes
                const hasTensorsAndAttributes = params.nodes[i]?.tensors?.length && node.attributes?.length;
                if (hasTensorsAndAttributes) {
                    const tensors = new Map(params.nodes[i].tensors.map((tensor) => [tensor.name, tensor]));
                    for (const attribute of node.attributes) {
                        const tensor = attribute.tensor;
                        if (tensor) {
                            // QAIRT Netron: Use custom logic to get tensor data
                            tensor.data = this.getTensorData(tensors, tensor, paramsBinBuffer, buffers);
                        }
                    }
                }
            }
        }
    }

    // QAIRT Netron: Get tensor data depending on the DLC version
    static getTensorData(tensors, tensor, paramsBinBuffer, buffers) {
        if (!tensors.has(tensor.name)) {
            throw new dlc.Error(`Unknown tensor`);
        }
        const tensorData = tensors.get(tensor.name);
        if (paramsBinBuffer) {
            // Tensor data exists in model.params.bin (introduced in DLC 4.1.0)
            const { data_position } = tensorData;
            return paramsBinBuffer.subarray(data_position.offset, data_position.offset + data_position.size);
        } else if (buffers) {
            // Tensor data exists inside Flatbuffer
            return buffers[tensorData.data_index].bytes;
        }
        return tensorData.bytes;
    }
    // QAIRT Netron END

    async _fetch(name) {
        try {
            const context = await this.context.fetch(name);
            return context.stream;
        } catch {
            return null;
        }
    }

    static _signature(stream) {
        const signature = {};
        signature.identifier = '?';
        signature.offset = 0;
        if (stream) {
            const buffer = stream.peek(Math.min(stream.length, 16));
            if (buffer[0] === 0xD5 && buffer[1] === 0x0A) {
                delete signature.identifier;
                if (buffer[3] === 0x00 && buffer[5] === 0x00 && buffer[5] === 0x00 && buffer[6] === 0x00) {
                    signature.major = buffer[2] | buffer[3] << 8;
                    signature.minor = buffer[4] | buffer[5] << 8;
                    if (signature.major > 2) {
                        signature.identifier = '?';
                    }
                }
            }
            if (signature.identifier === '?') {
                const offset = signature.major === undefined ? 0 : 8;
                const reader = flatbuffers.BinaryReader.open(stream, offset);
                if (reader) {
                    signature.identifier = reader.identifier;
                    signature.offset = offset;
                }
            }
        }
        return signature;
    }
};

dlc.Utility = class {

    static enum(version, name, value) {
        switch (version) {
            case 3: version = 'v3'; break;
            case 4: version = 'v4'; break;
            default: version = '';
        }
        const schema = dlc.schema[version];
        if (schema && name) {
            const type = schema[name];
            if (type) {
                dlc.Utility[version] = dlc.Utility[version] || new Map();
                const enums = dlc.Utility[version];
                if (!enums.has(name)) {
                    const entries = new Map(Object.entries(type).map(([key, value]) => [value, key]));
                    enums.set(name, entries);
                }
                const values = enums.get(name);
                if (values.has(value)) {
                    return values.get(value);
                }
            }
        }
        return value;
    }
};

dlc.Error = class extends Error {

    constructor(message) {
        super(message);
        this.name = 'Error loading DLC model.';
    }
};

export const ModelFactory = dlc.ModelFactory;


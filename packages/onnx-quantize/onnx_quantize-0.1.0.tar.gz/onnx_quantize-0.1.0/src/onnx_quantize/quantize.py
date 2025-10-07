import dataclasses

import onnx
import onnx_ir as ir
import onnxscript

from onnx_quantize.calibrate import OP_TYPES_TO_QUANTIZE, calibrate_model, get_nodes_to_quantize
from onnx_quantize.core import QConfig
from onnx_quantize.qfunctions import qfunctions
from onnx_quantize.qrules import qrules


def _add_qconfig_to_nodes(ir_model, qconfig):
    nodes = get_nodes_to_quantize(ir_model, OP_TYPES_TO_QUANTIZE)

    for node in ir_model.graph:
        if node in nodes:
            # Store the qconfig in the node metadata
            node.meta["qconfig"] = dataclasses.asdict(qconfig)


def quantize(model: onnx.ModelProto, qconfig: QConfig) -> onnx.ModelProto:
    """Quantizes an ONNX model using calibration data.

    Args:
        model (onnx.ModelProto): The ONNX model to be quantized
        qconfig (QConfig): Configuration for quantization parameters.

    Returns:
        onnx.ModelProto: The quantized ONNX model.
    """
    # Convert to IR model
    ir_model = ir.from_proto(model)

    # Calibrate the model to compute quantization parameters
    if qconfig.is_static:
        ir_model = calibrate_model(ir_model, qconfig)

    _add_qconfig_to_nodes(ir_model, qconfig)

    # Apply quantization rules to rewrite the model
    ir_model = onnxscript.rewriter.rewrite(ir_model, qrules)
    ir_model.functions.update(qfunctions)

    return ir.to_proto(ir_model)

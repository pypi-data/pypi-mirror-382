"""Basic expression signatures for the fenic signature system.

This module registers function signatures for basic expressions, providing
centralized type validation and return type inference.
"""
from fenic.core._logical_plan.signatures.function_signature import (
    FunctionSignature,
    ReturnTypeStrategy,
)
from fenic.core._logical_plan.signatures.registry import FunctionRegistry
from fenic.core._logical_plan.signatures.type_signature import (
    ArrayOfAny,
    ArrayWithMatchingElement,
    VariadicAny,
    VariadicUniform,
)
from fenic.core.types.datatypes import BooleanType, IntegerType


def register_basic_signatures():
    """Register all basic expression signatures."""
    # Array functions
    FunctionRegistry.register(
        "array_size", FunctionSignature(function_name="array_size", type_signature=ArrayOfAny(),
                                        return_type=IntegerType))

    # Array construction - variadic uniform (all elements same type)
    FunctionRegistry.register("array", FunctionSignature(function_name="array",
                                                         type_signature=VariadicUniform(expected_min_args=1),
                                                         return_type=ReturnTypeStrategy.DYNAMIC))

    # Struct construction - variadic any (different types allowed)
    FunctionRegistry.register("struct",
                              FunctionSignature(function_name="struct", type_signature=VariadicAny(expected_min_args=1),
                                                return_type=ReturnTypeStrategy.DYNAMIC))

    # Coalesce - all arguments must be same type as first
    FunctionRegistry.register("coalesce", FunctionSignature(function_name="coalesce",
                                                            type_signature=VariadicUniform(expected_min_args=1),
                                                            return_type=ReturnTypeStrategy.SAME_AS_INPUT))

    # Array contains - array + matching element type
    FunctionRegistry.register("array_contains", FunctionSignature(function_name="array_contains",
                                                                  type_signature=ArrayWithMatchingElement(),
                                                                  return_type=BooleanType))

    # Greatest - all arguments must be same type as first
    FunctionRegistry.register("greatest", FunctionSignature(function_name="greatest",
                                                            type_signature=VariadicUniform(expected_min_args=2),
                                                            return_type=ReturnTypeStrategy.SAME_AS_INPUT))

    # Least - all arguments must be same type as first
    FunctionRegistry.register("least", FunctionSignature(function_name="least",
                                                            type_signature=VariadicUniform(expected_min_args=2),
                                                            return_type=ReturnTypeStrategy.SAME_AS_INPUT))

register_basic_signatures()

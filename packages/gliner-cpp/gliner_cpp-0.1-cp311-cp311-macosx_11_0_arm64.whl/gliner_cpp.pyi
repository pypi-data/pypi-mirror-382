"""
Pybind11 bindings for the GLiNER model
"""

from __future__ import annotations
import collections.abc
import typing

__all__: list[str] = ["Config", "Model", "ModelType", "SPAN_LEVEL", "TOKEN_LEVEL"]

class Config:
    model_type: ModelType
    def __init__(
        self,
        max_width: typing.SupportsInt,
        max_length: typing.SupportsInt,
        model_type: ModelType = ...,
    ) -> None:
        """
        Create a configuration object for GLiNER models.

        :param max_width: Maximum candidate span width considered during decoding.
        :param max_length: Maximum number of tokens processed per input sequence.
        :param model_type: Underlying model type; defaults to span-level inference.
        """

    @property
    def max_length(self) -> int: ...
    @max_length.setter
    def max_length(self, arg0: typing.SupportsInt) -> None: ...
    @property
    def max_width(self) -> int: ...
    @max_width.setter
    def max_width(self, arg0: typing.SupportsInt) -> None: ...

class Model:
    @typing.overload
    def __init__(self, model_path: str, tokenizer_path: str, config: Config) -> None:
        """
        Create a GLiNER model using the given ONNX model and tokenizer paths.
        """

    @typing.overload
    def __init__(
        self,
        model_path: str,
        tokenizer_path: str,
        config: Config,
        device_id: typing.SupportsInt,
    ) -> None:
        """Instantiate a GLiNER model on an explicit device.

        :param model_path: Filesystem path to the exported ONNX model.
        :param tokenizer_path: Filesystem path to the serialized tokenizer vocabulary.
        :param config: Configuration controlling inference behaviour.
        :param device_id: Non-negative indices select a CUDA device; negative values force CPU execution.
        """

    def inference(
        self,
        texts: collections.abc.Sequence[str],
        entities: collections.abc.Sequence[str],
        flat_ner: bool = True,
        threshold: typing.SupportsFloat = 0.5,
        multi_label: bool = False,
    ) -> list:
        """
        Run span prediction for a batch of texts.

        :param texts: Input documents as UTF-8 encoded strings.
        :param entities: Entity label descriptions that the model should detect.
        :param flat_ner: Whether to restrict to non-overlapping (flat) spans.
        :param threshold: Minimum probability required for a span to be returned.
        :param multi_label: Whether spans can emit multiple entity labels.
        :returns: A list of span dictionaries per input text.
        """

class ModelType:
    """
    Members:

      TOKEN_LEVEL

      SPAN_LEVEL
    """

    SPAN_LEVEL: typing.ClassVar[ModelType]  # value = <ModelType.SPAN_LEVEL: 1>
    TOKEN_LEVEL: typing.ClassVar[ModelType]  # value = <ModelType.TOKEN_LEVEL: 0>
    __members__: typing.ClassVar[
        dict[str, ModelType]
    ]  # value = {'TOKEN_LEVEL': <ModelType.TOKEN_LEVEL: 0>, 'SPAN_LEVEL': <ModelType.SPAN_LEVEL: 1>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

SPAN_LEVEL: ModelType  # value = <ModelType.SPAN_LEVEL: 1>
TOKEN_LEVEL: ModelType  # value = <ModelType.TOKEN_LEVEL: 0>

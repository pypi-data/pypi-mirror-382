import abc
from typing import IO, AnyStr


class BaseExporter(abc.ABC):
    """
    Abstract base class for data exporters in the colander data converter.

    This class defines the interface that all exporter implementations must follow.
    Subclasses are responsible for implementing the actual export logic for their
    specific format or destination.
    """

    @abc.abstractmethod
    def export(self, output: IO[AnyStr], **kwargs) -> None:
        """
        Export data to the specified output stream.

        This abstract method must be implemented by all subclasses to define
        how data should be exported to the given output stream. The method
        signature allows for flexible output destinations (files, streams, etc.)
        and customizable export behavior through keyword arguments.

        Args:
            output: The output stream where data will be written.
                Can be a file object, :py:class:`~io.StringIO`, :py:class:`~io.BytesIO`, or any
                object that implements the IO interface for either
                text or binary data.
            **kwargs: Variable keyword arguments that allow subclasses to accept
                 format-specific options. Common examples might include:

                 - encoding: Character encoding for text formats
                 - indent: Indentation level for structured formats like JSON
                 - delimiter: Field separator for delimited formats like CSV
                 - compression: Compression settings for binary formats

        Raises:
            NotImplementedError: Always raised by this abstract method to enforce implementation in subclasses.
        """
        raise NotImplementedError()

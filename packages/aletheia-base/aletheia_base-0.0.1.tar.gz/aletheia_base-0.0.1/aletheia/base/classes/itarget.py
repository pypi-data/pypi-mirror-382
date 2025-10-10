from abc import ABC, abstractmethod


class ITarget(ABC):
    """
    Defines an interface for implementing target operations.

    This abstract base class provides a contract for target objects that
    require authentication and operations such as creation and deletion.
    Classes inheriting from this interface must implement all the abstract
    methods to ensure compliance with the contract.
    """
    @abstractmethod
    async def authenticate(self, **kwargs: str) -> None:
        """
        An asynchronous abstract method that serves as a blueprint for
        authentication logic. Subclasses must provide their own implementation
        for this method. This method ensures that derived classes adhere to
        a common interface for authentication functionality.

        :return: None
        """
        pass  # pragma: no cover

    @abstractmethod
    async def create(self, **kwargs: str) -> None:
        """
        An abstract method that must be implemented in derived classes to define
        the behavior for creating an entity or performing a creation process.

        This method is a coroutine and must be awaited.

        :raises NotImplementedError: If the method is not implemented in the derived class.
        :return: The result of the creation process, defined by the implementation in the
            derived class.
        """
        pass  # pragma: no cover

    @abstractmethod
    async def delete(self, **kwargs: str) -> None:
        """
        Defines an abstract method that must be implemented in a concrete subclass to
        delete a specified resource or entity. This method is asynchronous and should
        be awaited when called.

        :raises NotImplementedError: If this method is not implemented in a subclass.

        :return: None
        :rtype: None
        """
        pass  # pragma: no cover

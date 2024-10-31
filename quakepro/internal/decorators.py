import inspect
from functools import wraps
from collections.abc import Callable

def sync_signature(attribute_name: str, method_name: str, cls: type) -> Callable:
    """
    A decorator that synchronizes the signature of a method with a target 
    method from a specified class and attribute.

    Parameters
    ----------
    attribute_name : str
        The name of the attribute containing the target method.
    method_name : str
        The name of the method in the target class whose signature will be 
        synced.
    cls : type
        The class from which the target method is retrieved.

    Returns
    -------
    Callable
        The decorated method with a signature synchronized with the target 
        method.
    """
    def decorator(method: Callable) -> Callable:
        """
        Decorates the method by synchronizing its signature with the specified 
        target method.

        Parameters
        ----------
        method : Callable
            The original method to be decorated.

        Returns
        -------
        Callable
            The wrapper function that filters keyword arguments and synchronizes 
            the method signature.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            """
            Wrapper function that filters the keyword arguments and calls the 
            target method.

            Parameters
            ----------
            self : any type
                The instance of the class that contains the decorated method.
            *args : any type
                Positional arguments passed to the method.
            **kwargs : any type
                Keyword arguments passed to the method. Only the valid ones for 
                the target method will be passed.

            Returns
            -------
            any type
                The result of calling the target method with the filtered keyword 
                arguments.
            """
            target_instance = getattr(self, attribute_name)
            target_method = getattr(target_instance, method_name)
            sig = inspect.signature(target_method)

            filtered_kwargs = {
                k: v for k, v in kwargs.items() if k in sig.parameters
            }

            return target_method(*args, **filtered_kwargs)

        target_method = getattr(cls, method_name)
        wrapper.__signature__ = inspect.signature(target_method)

        return wrapper

    return decorator

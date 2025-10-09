from bisslog import BasicUseCase, use_case


class UseCase3(BasicUseCase):
    """
    Use case 3 implementation.

    Parameters
    ----------
    args : tuple
        Positional arguments.
    kwargs : dict
        Keyword arguments.

    Returns
    -------
    dict
        A dictionary containing the result of the use case.
    """

    @use_case
    def custom_name(self, *args, **kwargs) -> dict:
        """use case 3 implementation"""
        return {"result": "Use case 3 executed successfully."}

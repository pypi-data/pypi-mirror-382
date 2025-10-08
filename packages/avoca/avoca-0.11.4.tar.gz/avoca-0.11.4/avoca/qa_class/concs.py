from avoca.qa_class.zscore import ExtremeValues


class ExtremeConcentrations(ExtremeValues):
    """Assigns QA flags to extreme concentrations.

    Subclass of :py:class:`ExtremeValues`.
    Some parameters are set to apply only to concentrations.

    """

    runtypes: list[str] = ["air"]

    _default_params = {
        "use_log_normal": True,
        "variable": "C",
    }

    def __init__(
        self,
        **kwargs,
    ):
        # Check that no default was given as kwarg
        for key in self._default_params:
            if key in kwargs:
                raise ValueError(
                    f"Parameter {key} cannot be set for {type(self).__name__}."
                )
            kwargs[key] = self._default_params[key]

        super().__init__(**kwargs)

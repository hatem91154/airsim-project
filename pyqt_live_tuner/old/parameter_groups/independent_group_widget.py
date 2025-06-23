from .parameter_group_widget import ParameterGroupWidget


class IndependentParameterGroup(ParameterGroupWidget):
    """
    A visually grouped set of parameters where each parameter acts independently.

    - No shared signal or data bundling
    - Good for UI organization only
    """

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

    def register_callback(self, callback):
        """
        Register a callback for all widgets in the group.

        Args:
            callback (function): A function that takes (name, value) as arguments.
        """
        for widget in self.widgets.values():
            widget.register_callback(callback)

    # No overrides — inherits add/get/set behavior from base

import maya.OpenMaya as OpenMaya1


class SuppressScriptEditorOutput:
    """
    Suppresses output to the scriptEditor
    """

    def __init__(self):
        self.callback_id = OpenMaya1.MCommandMessage.addCommandOutputFilterCallback(
            self.suppress
        )

    @staticmethod
    def suppress(_, __, filter_output, ___):
        """
        This is the callback function that gets called when Maya wants to
        print something suppressing the print
        """
        OpenMaya1.MScriptUtil.setBool(filter_output, True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpenMaya1.MMessage.removeCallback(self.callback_id)

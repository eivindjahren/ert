from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from ert import ErtScript

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

    from ert.config import ErtPlugin, WorkflowJob
    from ert.enkf_main import EnKFMain
    from ert.gui.ertnotifier import ErtNotifier
    from ert.storage import Ensemble, Storage


class Plugin:
    def __init__(
        self, ert: "EnKFMain", notifier: "ErtNotifier", workflow_job: "WorkflowJob"
    ):
        self.__ert = ert
        self.__notifier = notifier
        self.__workflow_job = workflow_job
        self.__parent_window: Optional[QWidget] = None

        script = self.__loadPlugin()
        self.__name = script.getName()
        self.__description = script.getDescription()

    def __loadPlugin(self) -> "ErtPlugin":
        script_obj = ErtScript.loadScriptFromFile(self.__workflow_job.script)
        script = script_obj(
            self.__ert,
            self.__notifier._storage,
            ensemble=self.__notifier.current_ensemble,
        )
        return script

    def getName(self) -> str:
        return self.__name

    def getDescription(self) -> str:
        return self.__description

    def getArguments(self) -> List[Any]:
        """
        Returns a list of arguments. Either from GUI or from arbitrary code.
        If the user for example cancels in the GUI a CancelPluginException is raised.
        """
        script = self.__loadPlugin()
        return script.getArguments(self.__parent_window)

    def setParentWindow(self, parent_window: Optional[QWidget]) -> None:
        self.__parent_window = parent_window

    def getParentWindow(self) -> Optional[QWidget]:
        return self.__parent_window

    def ert(self) -> EnKFMain:
        return self.__ert

    @property
    def storage(self) -> Optional[Storage]:
        return self.__notifier.storage

    @property
    def ensemble(self) -> Optional[Ensemble]:
        return self.__notifier.current_ensemble

    def getWorkflowJob(self) -> WorkflowJob:
        return self.__workflow_job

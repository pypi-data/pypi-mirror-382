from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerTimeDict


class CTriggerTime(CTrigger):
    """
    触发器时间
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = 0
        # 当前时间
        self.current_setting = ""
        # 当前时间的时间戳
        self.time = None

        self.var_map = CTriggerTimeDict.var_map

import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CAircraftDict
from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args


class CAircraft(CActiveUnit):
    """飞机"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 方位类型
        self.bearing_type = 0
        # 方位
        self.bearing = 0.0
        # 距离（转换为千米）
        self.distance = 0.0
        # 高低速交替航行
        self.sprint_and_drift = False
        # 载机按钮的文本描述
        self.dock_aircraft = ""
        # 类别
        self.category = 0
        # 悬停
        self.hover_speed = 0.0
        # 低速
        self.low_speed = 0.0
        # 巡航
        self.cruise_speed = 0.0
        # 军力
        self.military_speed = 0.0
        # 加速
        self.add_force_speed = 0.0
        # 机型（战斗机，多用途，加油机...)
        self.type: int = 0
        # 宿主单元对象
        self.current_host_unit = ""
        # 挂载方案的DBID
        self.loadout_db_id = 0
        # 挂载方案的GUid
        self.loadout_guid = ""
        # 获取当前行动状态
        self.air_ops_condition = 0
        # 完成准备时间
        self.finish_prepare_time = ""
        # 快速出动信息
        self.quick_turn_around_info = ""
        # 显示燃油信息
        self.fuel_state = ""
        # 期望高度
        self.desired_altitude = 0.0
        # 维护状态
        self.maintenance_level = 0
        self.fuel_consumption_cruise = 0.0
        self.abn_time = 0.0
        self.fuel_recs_max_quantity = 0
        # 当前油量
        self.current_fuel_quantity = 0
        # 是否快速出动
        self.quick_turnaround_enabled = False
        # 是否有空中加油能力
        self.air_refueling_capable = False
        # 加油队列header
        self.show_tanker_header = ""
        # 加油队列明细
        self.show_tanker = ""
        # 可受油探管加油
        self.probe_refuelling = False
        # 可输油管加油
        self.boom_refuelling = False
        # from dong:
        # 航路点名称
        self.way_point_name = ""
        # 航路点描述
        self.way_point_description = ""
        # 航路点剩余航行距离描述，示例：剩余航行距离: 23.8908公里
        self.way_point_dtg_description = ""
        # 航路点剩余航行时间描述，示例1：剩余航行时间： 8分19秒 (当前), 5分32秒 (期望)； 示例2：剩余航行时间： 43秒
        self.way_point_ttg_description = ""
        # 航路点需要燃油数描述，示例1：需要燃油量: 71.9公斤(当前), 53.7公斤(期望)；示例2：需要燃油量: 6.9公斤
        self.way_point_fuel_description = ""
        self.max_range = "0.0"
        self.air_ops_condition_str = ""  # 空中作战状态字符串
        self.base_component = ""  # 基地组件
        self.loadout_db_guid = ""  # 挂载配置数据库GUID
        self.way_guid = ""  # 航路GUID

        self.var_map = CAircraftDict.var_map

    @property
    def loadout_obj(self):
        return self.situation.loadout_dict[self.loadout_guid]

    @property
    def type_name(self) -> str:
        """战斗机/多用途飞机/..."""
        return CAircraftDict.Labels.type[self.type]

    @property
    def category_name(self) -> str:
        """固定翼/直升机/..."""
        return CAircraftDict.Labels.category[self.category]

    @property
    def air_ops_condition_name(self) -> str:
        """飞机状态：空中/停泊/..."""
        return CAircraftDict.Labels.air_ops_condition[self.air_ops_condition]

    @property
    def maintenance_level_name(self) -> str:
        """武器状态未知,或不考虑连发机关枪/武器状态已知,且考虑连发机关枪/..."""
        return CAircraftDict.Labels.maintenance_level[self.maintenance_level]

    @property
    def status_type(self) -> Literal["valid_to_fly", "in_air", "in_air_rtb", "wait_ready"]:
        """
        获取飞机状态

        Returns:
            - str:
                - 'valid_to_fly' - 在基地可马上部署飞行任务,
                - 'in_air' - 在空中可部署巡逻，进攻，航路规划,
                - 'in_air_rtb' - 在空中返航或降落,
                - 'wait_ready' - 其他
        """
        if self.air_ops_condition in (1, 2, 4, 8, 9, 18, 23, 24, 26):
            # 在基地可马上部署飞行任务
            return "valid_to_fly"
        elif self.air_ops_condition in (0, 13, 14, 15, 16, 19, 20, 21, 22):
            # 在空中可部署巡逻，进攻，航路规划
            return "in_air"
        elif self.air_ops_condition in (5, 10, 11, 17, 25):
            # 在空中返航或降落
            return "in_air_rtb"
        else:
            return "wait_ready"

    @property
    def way_point_dtg(self) -> float:
        """航路点剩余航行距离，单位：公里"""
        numbers = re.findall(r"\d+\.?\d*", self.way_point_dtg_description)
        return float(numbers[0]) if numbers else 0.0

    @property
    def way_point_ttg(self) -> int:
        """航路点剩余航行时间，单位：秒"""
        description = self.way_point_ttg_description
        if not description:
            return 0

        total_seconds = 0
        # 尝试匹配小时
        hour_match = re.search(r"(\d+)\s*时", description)
        if hour_match:
            total_seconds += int(hour_match.group(1)) * 3600

        # 尝试匹配分钟
        minute_match = re.search(r"(\d+)\s*分", description)
        if minute_match:
            total_seconds += int(minute_match.group(1)) * 60

        # 尝试匹配秒
        second_match = re.search(r"(\d+)\s*秒", description)
        if second_match:
            total_seconds += int(second_match.group(1))

        # 如果没有找到任何时间单位，尝试将整个字符串作为秒数解析
        if total_seconds == 0:
            numbers = re.findall(r"\d+", description)
            if numbers:
                total_seconds = int(numbers[0])

        return total_seconds

    @property
    def way_point_fuel(self) -> float:
        """航路点需要燃油数，单位：公斤"""
        numbers = re.findall(r"\d+\.?\d*", self.way_point_fuel_description)
        return float(numbers[0]) if numbers else 0.0

    # def get_valid_weapons(self):
    #     """
    #     获取飞机有效的武器，暂时不可用接口
    #     :return:
    #     """
    #     info = {}
    #     # mount.values 可能是不同的mount，mount_obj.strWeapon,说明mount_obj 是一个对象
    #     for mount_obj in self.mounts.values():
    #         if (
    #             mount_obj.strWeaponFireState == "就绪" or "秒" in mount_obj.strWeaponFireState
    #         ) and mount_obj.m_ComponentStatus <= 1:
    #             mount_weapons = parse_weapons_record(mount_obj.m_LoadRatio)
    #             for w_record in mount_weapons:
    #                 w_dbid = w_record["wpn_dbid"]
    #                 if db.check_weapon_attack(w_dbid):
    #                     if w_dbid in info:
    #                         info[w_dbid] += w_record["wpn_current"]
    #                     else:
    #                         info[w_dbid] = w_record["wpn_current"]
    #     if self.loadout_obj is not None:
    #         mount_weapons = parse_weapons_record(self.loadout_obj.load_ratio)
    #         for w_record in mount_weapons:
    #             w_dbid = w_record["wpn_dbid"]
    #             if db.check_weapon_attack(w_dbid):
    #                 if w_dbid in info:
    #                     info[w_dbid] += w_record["wpn_current"]
    #                 else:
    #                     info[w_dbid] = w_record["wpn_current"]
    #     return info

    async def get_summary_info(self) -> dict:
        """获取精简信息, 提炼信息进行决策

        Returns:
            dict: 精简信息
        """
        info_dict = {
            "type": "Aircraft",
            "name": self.name,
            "guid": self.guid,
            "db_id": self.db_id,
            "subtype": str(self.type),
            "facility_type_id": "",
            "proficiency": self.proficiency_level,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude_agl,
            "altitude_asl": self.altitude_asl,
            "heading": self.current_heading,
            "speed": self.current_speed,
            "throttle": self.current_throttle,
            "auto_detectable": self.auto_detectable,
            "active_unit_status": self.active_unit_status,
            "fuel_state": self.fuel_state,
            "weaponstate": -1,
            "mounts": await self.get_mounts(),
            "targeted_by": await self.get_ai_targets(),
            "pitch": self.pitch,
            "roll": self.roll,
            "yaw": self.current_heading,
            "loadout": self.loadout_obj,
            "fuel": self.current_fuel_quantity,
            "damage": self.damage_state,
            "sensors": await self.get_sensors(),
            "weapons_valid": await self.get_weapon_infos(),
        }
        return info_dict

    async def set_waypoint(self, latitude: float, longitude: float) -> bool:
        """
        设置飞机下一个航路点

        Args:
            - latitude: 纬度
            - longitude: 经度

        Returns:
            - bool: 设置是否成功
        """
        lua_str = (
            f"ScenEdit_SetUnit({{side= '{self.side}', guid='{self.guid}', course={{ {{ Description = ' ', TypeOf = "
            f"'ManualPlottedCourseWaypoint', longitude = {longitude}, latitude = {latitude} }} }} }})"
        )
        response = await self.mozi_server.send_and_recv(lua_str)
        return response.lua_success

    async def ops_single_out(self) -> bool:
        """
        设置在基地内飞机单机出动

        Returns:
            - bool: 设置是否成功
        """
        if self.host_active_unit:
            return await super().set_single_out()
        return False

    async def deploy_dipping_sonar(self) -> bool:
        """
        部署吊放声呐

        Returns:
            - bool: 设置是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_DeployDippingSonar('{self.guid}')")
        return response.lua_success

    async def quick_turnaround(self, set_quick_turnaround: bool, sorties_total: int) -> bool:
        """
        让指定飞机快速出动

        Args:
            - set_quick_turnaround: 是否快速出动
            - sorties_total: 出动架次总数

        Returns:
            - bool: 设置是否成功
        """
        lua = f"Hs_QuickTurnaround('{self.guid}',{str(set_quick_turnaround).lower()},{sorties_total})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    @validate_literal_args
    async def ok_ready_mission(self, enable_quick_turnaround: bool, combo_box: Literal[-1, 0]) -> bool:
        """
        飞机按对应的挂载方案所需准备时间完成出动准备

        Args:
            - enable_quick_turnaround (bool): 是否支持快速出动
            - combo_box (int): 快速出动值

        Returns:
            - bool: 设置是否成功
        """
        enable_quick_turnaround_str = str(enable_quick_turnaround).lower()
        loadout_db_guid = self.loadout_obj.guid
        lua_script = f"Hs_OKReadyMission('{self.guid}','{loadout_db_guid}',{enable_quick_turnaround_str},{combo_box})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def abort_launch(self) -> bool:
        """
        让正在出动中的飞机立即终止出动。

        Returns:
            - bool: 设置是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_ScenEdit_AirOpsAbortLaunch({{'{self.guid}'}})")
        return response.lua_success

    @validate_uuid4_args(["tanker_guid"])
    async def refuel(self, tanker_guid: str) -> bool:
        """
        命令单元多种方式寻找加油机（自动寻找加油机、指定加油机、
        指定加油任务执行单元）进行加油。它与 ScenEdit_RefuelUnit 功能相同，只是它
        的参数是单元或任务的 GUID、后者的参数是单元或任务的名称。

        Args:
            - tanker_guid: 加油机guid

        Returns:
            - bool: 设置是否成功
        """
        if tanker_guid == "":
            lua = f"Hs_ScenEdit_AirRefuel({{guid='{self.guid}'}})"
        else:
            lua = f"Hs_ScenEdit_AirRefuel({{guid='{self.guid}',tanker_guid = '{tanker_guid}'}})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def set_airborne_time(self, hour: int, minute: int, second: int) -> bool:
        """
        设置留空时间

        Args:
            - hour: 小时
            - minute: 分钟
            - second: 秒

        Returns:
            - bool: 设置是否成功
        """
        lua_script = f"Hs_SetAirborneTime('{self.guid}','{hour}','{minute}','{second}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def time_to_ready(self, time: str) -> bool:
        """
        设置飞机出动准备时间

        Args:
            - time: 出动准备时间

        Returns:
            - bool: 设置是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_ScenEdit_TimeToReady('{time}',{{'{self.guid}'}}")
        return response.lua_success

    @validate_literal_args
    async def ready_immediately(
        self,
        loadout_db_id: int,
        enable_quick_turnaround: bool,
        combo_box: Literal[-1, 0],
        immediately_go: bool,
        optional_weapon: bool,
        ignore_weapon: bool,
    ) -> bool:
        """
        飞机立即完成出动准备

        Args:
            - loadout_db_id: 挂载方案数据库dbid
            - enable_quick_turnaround: 是否支持快速出动
            - combo_box: 快速出动值
            - immediately_go: 是否立即出动
            - optional_weapon: 是否不含可选武器
            - ignore_weapon: 是否不忽略武器

        Returns:
            - bool: 设置是否成功
        """
        enable_quick_turnaround_str = str(enable_quick_turnaround).lower()
        immediately_go_str = str(immediately_go).lower()
        optional_weapon_str = str(optional_weapon).lower()
        ignore_weapon_str = str(ignore_weapon).lower()
        lua_script = f"Hs_ReadyImmediately('{self.guid}',{loadout_db_id},{enable_quick_turnaround_str},{combo_box},{immediately_go_str},{optional_weapon_str},{ignore_weapon_str})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

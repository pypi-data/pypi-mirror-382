from typing import Dict, Type

from lqs.transcode.cutter.cutter import *
import lqs.transcode.cutter.cutter as CutterClasses
import orjson

_custom_classes: Dict[str, Type[CustomClass]] = {
    # "lqs_cutter/toro.nav.inputs.IMU": bhc_navcon_imu,
    # "lqs_cutter/navcon_imu": navcon_imu,
    "toro.nav.inputs.IMU": bhc_navcon_imu,
    "navcon.imu": navcon_imu,
    "navcon_internal.health.heartbeat": navcon_reporter_heartbeat,
    "navcon.0.pose_filter.cal_data": navcon_pose_filter_calibration_data,
    # 'navcon.0.pose_filter.binary':navcon_pose_filter,
    "navcon.stats.temperature": navcon_temperature,
    "navcon_internal.0.img.metadata": navcon_image_metadata,
    "platform.heartbeat": navcon_heartbeat,
    "platform.gps": navcon_gps,
    "navcon.heartbeat": navcon_heartbeat,
    "navcon.0.localizer.cam_select": navcon_localizer_cam_select,
    "navcon_internal.0.autoexposure_status": navcon_autoexposure_status,
    "navcon.0.platform_response.speed_limit": navcon_speed_limit,
    "navcon.0.platform_request.speed_limit": navcon_speed_limit,
    "navcon_internal.camera_pose_success": navcon_camera_pose_success,
    "navcon_internal.img.docking_called_shot.1": navcon_image,
    "navcon_internal.img.called_shot.1": navcon_image,
    "navcon_internal.dock.called_shot": navcon_image,
    "navcon_internal.img.docking_called_shot.2": navcon_image,
    "navcon_internal.img.called_shot.0": navcon_image,
    "navcon_internal.img.called_shot.2": navcon_image,
    "navcon_internal.img.docking_called_shot.0": navcon_image,
    "navcon_internal.img.called_shot.3": navcon_image,
    "navcon_internal.img.docking_called_shot.3": navcon_image,
    "navcon_internal.localization_img.1": navcon_image,
    "navcon_internal.localization_img.2": navcon_image,
    "navcon_internal.localization_img.3": navcon_image,
    "navcon_internal.localization_img.0": navcon_image,
    "navcon.0.localizer.init_loc_info": navcon_init_localization_info,
    "navcon_internal.0.localizer_config": navcon_localizer_config,
    "navcon.gps": navcon_gps,
    "navcon.health.info": navcon_health_info,
    "events.encoder_stillness": navcon_event,
    "navcon.0.localizer.initialization_results": navcon_localizer_initialization_results,
    "navcon.0.telem.fsm_state": navcon_telemetry_state_change,
    # json_classes
    "navcon.0.pose_filter.json": StringifiedJson,
    "navcon_internal.stats.temperature.json": StringifiedJson,
    "navcon_internal.stats.memory.json": StringifiedJson,
    "navcon_internal.stats.trip.json": StringifiedJson,
    "navcon_internal.stats.cooling.json": StringifiedJson,
    "navcon_internal.stats.cpu.json": StringifiedJson,
    "navcon_internal.0.web_heartbeat.json": StringifiedJson,
    "navcon_internal.imu_debug.json": StringifiedJson,
    "navcon_internal.imu_timing.json": StringifiedJson,
    # new topics from Steve Landers
    "platform.wheelencoders": navcon_encoder_update,
    "navcon.0.pose_filter.binary": navcon_pose_filter,
    "navcon.0.pose_filter.binary.throttled": navcon_pose_filter,
    "navcon.0.pose_filter.docking.json": StringifiedJson,
    "navcon.0.pose_filter.docking.binary": navcon_pose_filter,
    "debug.hardware_id": StringifiedJson,
    "navcon.state.desired": navcon_desired_state,
    "navcon_internal.health.fault": navcon_fault_message,
    "navcon.called_shot": navcon_called_shot,
    "debug.unit_info": StringifiedJson,
    "debug.unit_config": StringifiedJson,
    "debug.application_config": StringifiedJson,
    "navcon.health.system": navcon_health,
    "debug.software_version": StringifiedJson,
    "navcon.0.localizer.safety_poses": navcon_safety_localization_poses,
}

wild_card_prefixes = {
    "navcon_internal.img.called_shot.*": navcon_called_shot,
    "cutter.v4lcam.img.*": navcon_image,
    "navcon_internal.localization_img.*": navcon_image,
}


def get_type_name_for_cutter(topic_name):
    type_name = _custom_classes.get(topic_name, None)
    if type_name:
        type_name = f"lqs_cutter/{type_name.__name__}"
    else:
        for wildcard_entry, cls in wild_card_prefixes.items():
            prefix = wildcard_entry.split("*")[0]
            if topic_name.startswith(prefix):
                type_name = f"lqs_cutter/{cls.__name__}"
                break
    return type_name


class CutterDecoder:
    def deserialize(self, type_name: str, payload: bytes):
        assert type_name.startswith("lqs_cutter/")
        type_name = type_name.removeprefix("lqs_cutter/")
        custom_class = getattr(CutterClasses, type_name)
        res = custom_class.deserialize(payload)
        return orjson.loads(orjson.dumps(res))

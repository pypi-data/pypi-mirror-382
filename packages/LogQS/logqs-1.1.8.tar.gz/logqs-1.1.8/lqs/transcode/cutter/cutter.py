from abc import ABC
import json
import struct
from enum import Enum, IntEnum

from lqs.transcode.cutter.fault_enums import parse_fault


def convert_bitflag_to_list_enums(bit_encoded_value, enum):
    res = []
    bits = bin(bit_encoded_value)[2:]
    bits = reversed(bits)
    for i, binary_val in enumerate(bits):
        if binary_val == "1":
            res.append(enum(i).name)
    return res


class DecodeCutter:
    def deserialize(*args, **kwargs):
        pass


class CustomClass(ABC):
    @classmethod
    def deserialize_cls(cls, payload: bytes):
        return cls(**cls.deserialize(payload))

    @classmethod
    def deserialize(cls, payload: bytes) -> dict:
        return NotImplemented


class StringifiedJson(CustomClass):
    @classmethod
    def deserialize(cls, payload: bytes) -> dict:
        return json.loads(payload)


class bhc_navcon_imu(CustomClass):
    def __init__(
        self,
        msg_ts,
        acc_x,
        acc_y,
        acc_z,
        gyr_x,
        gyr_y,
        gyr_z,
        temp,
        trusted,
    ):
        self.msg_ts = msg_ts
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.gyr_x = gyr_x
        self.gyr_y = gyr_y
        self.gyr_z = gyr_z
        self.temp = temp
        self.trusted = trusted

    @classmethod
    def deserialize(cls, payload: bytes):
        """struct bhc_navcon_imu {
            float32_t msg_ts;
            /**
             * acceleration raw sensor value.
             */
            float32_t acc_x;
            float32_t acc_y;
            float32_t acc_z;
            /**
             * rotation raw sensor value.
             */
            float32_t gyr_x;
            float32_t gyr_y;
            float32_t gyr_z;

            // temperature
            float32_t temp;

            uint8_t trusted;
            uint8_t pad[3];
        }"""
        (
            msg_ts,
            acc_x,
            acc_y,
            acc_z,
            gyr_x,
            gyr_y,
            gyr_z,
            temp,
            trusted,
            _,
            _,
            _,
        ) = struct.unpack("8f4B", payload)
        return dict(
            msg_ts=msg_ts,
            acc_x=acc_x,
            acc_y=acc_y,
            acc_z=acc_z,
            gyr_x=gyr_x,
            gyr_y=gyr_y,
            gyr_z=gyr_z,
            temp=temp,
            trusted=trusted,
        )


class navcon_imu(CustomClass):
    """struct navcon_imu {
        navcon_ns_ts_t msg_ts; // uint64_t
        /**
         * acceleration raw sensor value.
         */
        int16_t acc_x;
        int16_t acc_y;
        int16_t acc_z;
        /**
         * rotation raw sensor value.
         */
        int16_t gyr_x;
        int16_t gyr_y;
        int16_t gyr_z;
        /**
         * accel scale.
         * dividing each acceleration value by acc_scale results in units of g.
         */
        uint16_t acc_scale;
        /**
         * accel scale.
         * dividing each rotation value by gyr_scale results in units of deg/s.
         */
        uint16_t gyr_scale;
        /**
         * sensor-specific sample timestamp.
         */
        uint32_t sample_ts;
    }"""

    def __init__(
        self,
        msg_ts,
        acc_x,
        acc_y,
        acc_z,
        gyr_x,
        gyr_y,
        gyr_z,
        acc_scale,
        gyr_scale,
        sample_ts,
    ):
        self.msg_ts = msg_ts
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.gyr_x = gyr_x
        self.gyr_y = gyr_y
        self.gyr_z = gyr_z
        self.acc_scale = acc_scale
        self.gyr_scale = gyr_scale
        self.sample_ts = sample_ts

    @classmethod
    def deserialize(cls, payload: bytes):
        (
            msg_ts,
            acc_x,
            acc_y,
            acc_z,
            gyr_x,
            gyr_y,
            gyr_z,
            acc_scale,
            gyr_scale,
            sample_ts,
        ) = struct.unpack("QhhhhhhHHI", payload)
        return dict(
            msg_ts=msg_ts,
            acc_x=acc_x,
            acc_y=acc_y,
            acc_z=acc_z,
            gyr_x=gyr_x,
            gyr_y=gyr_y,
            gyr_z=gyr_z,
            acc_scale=acc_scale,
            gyr_scale=gyr_scale,
            sample_ts=sample_ts,
        )


class navcon_health_info(CustomClass):
    """struct navcon_health_info {
        navcon_ns_ts_t msg_ts;
        uint16_t msg_len;
        #define NAVCON_HEALTH_INFO_DATA_MAXLEN (1024)
        uint8_t pad_0[6];
        uint8_t data[0];
    }"""

    def __init__(
        self,
        msg_ts,
        msg_len,
        data,
    ):
        self.msg_ts = msg_ts
        self.msg_len = msg_len
        self.data = data

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        msg_len = struct.unpack("H", payload[8:10])[0]
        # pad_0 = struct.unpack("6B", payload[10:16])[0]
        assert msg_len == len(payload[16:])
        data = json.loads(payload[16:])
        return dict(
            msg_ts=msg_ts,
            msg_len=msg_len,
            data=data,
        )


class NavconEventType(Enum):
    NAVCON_EVENT_GENERIC = 0
    NAVCON_EVENT_ENCODER_STILLNESS = 1


class NavconPayloadEncoderStillness(Enum):
    NAVCON_PAYLOAD_ENCODER_STILLNESS_STATE_STILL = 0
    NAVCON_PAYLOAD_ENCODER_STILLNESS_STATE_NOT_STILL = 1


class NavconState(Enum):
    ERROR = 0
    STANDBY = 1
    TRAIN = 2
    POST = 3
    MAPBUILD = 4
    LOCALIZE = 5
    LOG_LITE = 6
    RTK_MAPBUILD = 7
    RTK_LOCALIZE = 8
    DOCKING = 9
    DEPRECATED_STOP_AND_STARE = 10
    POST_FAILURE = 11
    NAVIGATE = 12
    SPLINEBUILD = 13
    LOG_UPLOAD = 14
    SELF_LOCALIZE = 15
    CAMERA_CALIBRATION = 16
    GYROSCOPE_CALIBRATION = 17
    PLATFORM_TRAIN = 18
    LOCALIZE_INITIALIZE = 19
    PLATFORM_TRAIN_INITIALIZE = 20
    DEPRECATED_MAINTENANCE = 21


class NavconGpsFixMode(Enum):
    UNKNOWN = 0
    NO_FIX = 1
    MODE_2D_FIX = 2
    MODE_3D_FIX = 3


class NavconGPSSource(Enum):
    NAVCON_SOURCE_DURO = 0
    NAVCON_SOURCE_EXT_GPS = 1


class navcon_event(CustomClass):
    """struct navcon_event {
        navcon_ns_ts_t msg_ts;
        /** length of payload in bytes (i.e. excludes navcon_event structure size) */
        uint32_t payload_size;
        /** event type code, as defined in navcon_event_type_t. */
        uint32_t type;
        uint8_t payload[0];
    }"""

    def __init__(
        self,
        msg_ts,
        payload_size,
        type,
        payload,
    ):
        self.msg_ts = msg_ts
        self.payload_size = payload_size
        self.type = type
        self.payload = payload

    @classmethod
    def deserialize(cls, _payload: bytes):
        msg_ts = struct.unpack("Q", _payload[0:8])[0]
        payload_size = struct.unpack("I", _payload[8:12])[0]
        type = struct.unpack("I", _payload[12:16])[0]
        type = NavconEventType(type)
        payload = struct.unpack(f"{payload_size}B", _payload[16:])[0]
        if type == NavconEventType.NAVCON_EVENT_ENCODER_STILLNESS:
            payload = NavconPayloadEncoderStillness(payload)
        return dict(
            msg_ts=msg_ts,
            payload_size=payload_size,
            type=type.name,
            payload=payload.name,
        )


class navcon_telemetry_state_change(CustomClass):
    """struct navcon_telemetry_state_change {
        navcon_ns_ts_t msg_ts;
        navcon_ns_ts_t state_ts;
        navcon_state_rep src_state;
        navcon_state_rep target_state;
        uint8_t pad[14];
    }"""

    def __init__(self, msg_ts, state_ts, src_state, target_state):
        self.msg_ts = msg_ts
        self.state_ts = state_ts
        self.src_state = src_state
        self.target_state = target_state

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts, state_ts, src_state, target_state = struct.unpack("QQBB", payload[:18])
        src_state, target_state = NavconState(src_state), NavconState(target_state)
        _ = struct.unpack("14B", payload[18:])
        return dict(
            msg_ts=msg_ts,
            state_ts=state_ts,
            src_state=src_state.name,
            target_state=target_state.name,
        )


class navcon_gps(CustomClass):
    """struct navcon_gps {
        navcon_ns_ts_t msg_ts;
        float64_t lat;
        float64_t lon;
        float64_t height;
        /** 2-sigma uncertainty values, in meters, as reported in gpsd TPV. */
        float64_t lat_err;
        float64_t lon_err;
        float64_t height_err;
        uint32_t tow;
        uint16_t week;
        /**
         * gpsd TPV mode (gps fix status):
         *
         * 0 - no mode value yet seen
         * 1 - no fix
         * 2 - 2d fix
         * 3 - 3d fix
         */
        navcon_gps_fix_mode_rep mode;
        navcon_gps_source_rep source;
    }"""

    def __init__(
        self,
        msg_ts,
        lat,
        lon,
        height,
        lat_err,
        lon_err,
        height_err,
        tow,
        week,
        mode,
        source,
    ):
        self.msg_ts = msg_ts
        self.lat = lat
        self.lon = lon
        self.height = height
        self.lat_err = lat_err
        self.lon_err = lon_err
        self.height_err = height_err
        self.tow = tow
        self.week = week
        self.mode = mode
        self.source = source

    @classmethod
    def deserialize(cls, payload: bytes):
        (
            msg_ts,
            lat,
            lon,
            height,
            lat_err,
            lon_err,
            height_err,
            tow,
            week,
            mode,
            source,
        ) = struct.unpack("QddddddIHBB", payload)
        return dict(
            msg_ts=msg_ts,
            lat=lat,
            lon=lon,
            height=height,
            lat_err=lat_err,
            lon_err=lon_err,
            height_err=height_err,
            tow=tow,
            week=week,
            mode=mode,
            source=source,
        )


class NavconHeartbeatStatus(Enum):
    OK = 0
    NOT_OK = 1


class navcon_health_bit(Enum):
    CAM0 = 0
    CAM1 = 1
    CAM2 = 2
    CAM3 = 3
    CPU = 4
    DISK = 5
    DURO = 6
    GPS = 7
    IMU = 8
    PROCESS = 9
    RAM = 10
    WHEEL_ENCODERS = 11


class NavconHealthBit(Enum):
    """
    typedef enum {
        NAVCON_HEALTH_BIT_CAM0,
        NAVCON_HEALTH_BIT_CAM1,
        NAVCON_HEALTH_BIT_CAM2,
        NAVCON_HEALTH_BIT_CAM3,
        NAVCON_HEALTH_BIT_CPU,
        NAVCON_HEALTH_BIT_DISK,
        NAVCON_HEALTH_BIT_DURO,
        NAVCON_HEALTH_BIT_GPS,
        NAVCON_HEALTH_BIT_IMU,
        NAVCON_HEALTH_BIT_PROCESS,
        NAVCON_HEALTH_BIT_RAM,
        NAVCON_HEALTH_BIT_WHEEL_ENCODERS,

        _NAVCON_HEALTH_BIT_TOPIC_COUNT
    } navcon_health_bit_t;
    """

    CAM0 = 0
    CAM1 = 1
    CAM2 = 2
    CAM3 = 3
    CPU = 4
    DISK = 5
    DURO = 6
    GPS = 7
    IMU = 8
    PROCESS = 9
    RAM = 10
    WHEEL_ENCODERS = 11


class navcon_reporter_heartbeat(CustomClass):
    """struct navcon_reporter_heartbeat {
        navcon_ns_ts_t msg_ts;
        navcon_heartbeat_status_rep status;
        navcon_health_bit_rep reporter_id;
        uint8_t pad_0[6];
    }"""

    def __init__(self, msg_ts, status, reporter_id):
        self.msg_ts = msg_ts
        self.status = status
        self.reporter_id = reporter_id

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        status = struct.unpack("B", payload[8:9])[0]
        reporter_id = struct.unpack("B", payload[9:10])[0]
        # pad_0 = struct.unpack("6B", payload[10:16])[0]
        assert len(payload) == 16
        reporter_id = NavconHealthBit(reporter_id)
        status = NavconHeartbeatStatus(status)
        return dict(
            msg_ts=msg_ts,
            status=status.name,
            reporter_id=reporter_id.name,
        )


class navcon_heartbeat(CustomClass):
    """struct navcon_heartbeat {
     navcon_ns_ts_t      msg_ts;
     navcon_api_ver_t    api_version;
     navcon_state_rep    state;
     uint8_t             pad_0[3];
    }"""

    def __init__(self, msg_ts, api_version, state):
        self.msg_ts = msg_ts
        self.api_version = api_version
        self.state = state

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        api_version = struct.unpack("I", payload[8:12])[0]
        state = struct.unpack("B", payload[12:13])[0]
        state = NavconState(state)
        # pad_0 = struct.unpack("3B", payload[13:16])[0]
        assert len(payload) == 16
        return dict(
            msg_ts=msg_ts,
            api_version=api_version,
            state=state.name,
        )


class LocalizerConfig(Enum):
    DAYTIME_CONFIGURATION = 0
    NIGHTTIME_CONFIGURATION = 1


class navcon_localizer_config(CustomClass):
    """struct navcon_localizer_config {
    navcon_ns_ts_t msg_ts;
    /** Batch size */
    uint8_t batch_size;
    /** Configuration */
    localizer_config_rep configuration;
    /** padding to raster to 8char width */
    uint8_t pad_0[6];
    /** extra padding for message extension */
    uint8_t pad_1[16];
    }"""

    def __init__(self, msg_ts, batch_size, configuration):
        self.msg_ts = msg_ts
        self.batch_size = batch_size
        self.configuration = configuration

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        batch_size = struct.unpack("B", payload[8:9])[0]
        configuration = struct.unpack("B", payload[9:10])[0]
        configuration = LocalizerConfig(configuration)
        # pad_0 = struct.unpack("6B", payload[10:16])[0]
        # pad_1 = struct.unpack("16B", payload[16:])[0]
        assert len(payload) == 32
        return dict(
            msg_ts=msg_ts,
            batch_size=batch_size,
            configuration=configuration.name,
        )


class navcon_localizer_initialization_results(CustomClass):
    """struct navcon_localizer_initialization_results {
        navcon_ns_ts_t msg_ts;

        /**
         * Number of camera combinations.
         */
        uint8_t num_combinations;

        /**
         * Padding for message extension.
         */
        uint8_t padding[15];

        /**
         * Payload data. Payload size is num_combinations * sizeof(navcon_camera_pose_success).
         */
        uint8_t payload[0];
    }"""

    def __init__(
        self,
        msg_ts,
        num_combinations,
        payload,
    ):
        self.msg_ts = msg_ts
        self.num_combinations = num_combinations
        self.payload = payload

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        num_combinations = struct.unpack("B", payload[8:9])[0]
        # padding = struct.unpack("15B", payload[9:24])[0]
        _payload = []
        for i in range(num_combinations):
            start = 24 + (16 * i)
            end = start + 16
            _payload.append(
                navcon_camera_pose_success.deserialize(payload=payload[start:end])
            )
        return dict(
            msg_ts=msg_ts,
            num_combinations=num_combinations,
            payload=_payload,
        )


class ImageType(Enum):
    NULL = 0
    RGBG = 1
    RGB24 = 2
    JPG = 3
    UYVY = 4
    GREY8 = 5
    PPM = 6
    SRGGB8 = 7
    YUYV = 8
    NV12 = 9


class navcon_image(CustomClass):
    """struct navcon_image {
    navcon_ns_ts_t msg_ts;
    uint64_t sequence;
    uint16_t width;
    uint16_t height;
    /** this is a bitfield with one bit per camera, camera 0 == (1 << 0). */
    uint8_t cameras;
    uint8_t type;
    #define NAVCON_IMAGE_TYPE_NULL      (0)
    #define NAVCON_IMAGE_TYPE_RGBG      (1)
    #define NAVCON_IMAGE_TYPE_RGB24     (2)
    #define NAVCON_IMAGE_TYPE_JPG       (3)
    #define NAVCON_IMAGE_TYPE_UYVY      (4)
    #define NAVCON_IMAGE_TYPE_GREY8     (5)
    #define NAVCON_IMAGE_TYPE_PPM       (6)
    #define NAVCON_IMAGE_TYPE_SRGGB8    (7)
    #define NAVCON_IMAGE_TYPE_YUYV      (8)
    #define NAVCON_IMAGE_TYPE_NV12      (9)
    uint8_t pad_0[2];
    /**
        * data consists of length-encoded image blobs, ordered camera 0 -> 3,
        * populated according to the cameras bitfield.
        *
        * ex: cameras == 0x5
        *     data: [ cam 0 img size (as uint32_t) ][ cam 0 data ][ cam 2 img size (as uint32_t) ][ cam 2 data ]
        */
    uint8_t data[0];
    }"""

    def __init__(self, msg_ts, sequence, width, height, cameras, type, data):
        self.msg_ts = msg_ts
        self.sequence = sequence
        self.width = width
        self.height = height
        self.cameras = cameras
        self.type = type
        self.data = data

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        sequence = struct.unpack("Q", payload[8:16])[0]
        width = struct.unpack("H", payload[16:18])[0]
        height = struct.unpack("H", payload[18:20])[0]
        cameras: int = struct.unpack("B", payload[20:21])[0]
        type = ImageType(struct.unpack("B", payload[21:22])[0])
        # pad_0 = struct.unpack("2B", payload[22:24])[0]

        images = []
        start = 0
        num_cameras = cameras.bit_count()
        data = payload[24:]
        for i in range(num_cameras):
            img_size = struct.unpack("I", data[start : start + 4])[0]
            start += 4
            img_data = list(
                struct.unpack(f"{img_size}B", data[start : start + img_size])
            )
            start += img_size
            images.append(img_data)
        assert len(data) == start
        return dict(
            msg_ts=msg_ts,
            sequence=sequence,
            width=width,
            height=height,
            cameras=cameras,
            type=type.name,
            data=images,
        )


class navcon_camera_pose_success(CustomClass):
    """struct navcon_camera_pose_success {
    navcon_ns_ts_t msg_ts;

    /**
        * A bitfield representing the cameras which cameras were used to produce the pose.
        * Value of 0 represents unknown camera usage.
        */
    uint8_t cams;

    /**
        * 0 if pose was invalid, 1 if valid (successful localization).
        */
    uint8_t valid;

    /**
        * Padding for message extension
        */
    uint8_t pad_1[6];
    }"""

    def __init__(self, msg_ts, cams, valid):
        self.msg_ts = msg_ts
        self.cams = cams
        self.valid = valid

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        cams = struct.unpack("B", payload[8:9])[0]
        valid = struct.unpack("B", payload[9:10])[0]
        # pad_1 = struct.unpack("6B", payload[10:16])[0]
        assert len(payload) == 16
        return dict(
            msg_ts=msg_ts,
            cams=cams,
            valid=valid,
        )


class navcon_init_localization_info(CustomClass):
    """struct navcon_init_localization_info {
        /**
         * navcon timestamp for this message.
         */
        navcon_ns_ts_t msg_ts;

        /**
         * The id of the corresponding called shot message which preceded this
         * message in the stream.
         */
        navcon_called_shot_id_t shot_id;

        /**
         * Number of initial localization attempts.
         */
        uint32_t num_init_loc_attempts;

        /**
         * Total number of keyframes available to localize against.
         */
        uint64_t total_kfs;

        /**
         * Number of keyframes NAVCON has attempted to localize against during initialization.
         * The ratio "kfs_attempted_localization / total_kfs" gives a useful measure for determining
         * when to abort localization due to failed initilization.
         */
        uint64_t kfs_attempted_localization;
    }"""

    def __init__(
        self,
        msg_ts,
        shot_id,
        num_init_loc_attempts,
        total_kfs,
        kfs_attempted_localization,
    ):
        self.msg_ts = msg_ts
        self.shot_id = shot_id
        self.num_init_loc_attempts = num_init_loc_attempts
        self.total_kfs = total_kfs
        self.kfs_attempted_localization = kfs_attempted_localization

    @classmethod
    def deserialize(cls, payload: bytes):
        (
            msg_ts,
            shot_id,
            num_init_loc_attempts,
            total_kfs,
            kfs_attempted_localization,
        ) = struct.unpack("QIIQQ", payload)
        return dict(
            msg_ts=msg_ts,
            shot_id=shot_id,
            num_init_loc_attempts=num_init_loc_attempts,
            total_kfs=total_kfs,
            kfs_attempted_localization=kfs_attempted_localization,
        )


class AutoexposureState(Enum):
    AUTOEXPOSURE_STANDBY = 0
    AUTOEXPOSURE_WAITING_FOR_RESPONSE = 1
    AUTOEXPOSURE_STOP_AND_STARE = 2


class navcon_autoexposure_status(CustomClass):
    """struct navcon_autoexposure_status {
    navcon_ns_ts_t msg_ts;
    /** Current autoexposure status */
    autoexposure_state_rep state;
    uint8_t pad_0[7];
    /** extra padding for message extension */
    uint8_t pad_1[48];
    }"""

    def __init__(self, msg_ts, state):
        self.msg_ts = msg_ts
        self.state = state

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        state = struct.unpack("B", payload[8:9])[0]
        state = AutoexposureState(state)
        # pad_0 = struct.unpack("7B", payload[9:16])[0]
        # pad_1 = struct.unpack("48B", payload[16:64])[0]
        assert len(payload) == 64
        return dict(
            msg_ts=msg_ts,
            state=state.name,
        )


class navcon_vec3d(CustomClass):
    """struct navcon_vec3d {
        float64_t x;
        float64_t y;
        float64_t z;
    } ;
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def deserialize(cls, payload: bytes):
        x, y, z = struct.unpack("3d", payload)
        return dict(
            x=x,
            y=y,
            z=z,
        )


class cross_axis_params(CustomClass):
    """struct cross_axis_params
    {
        float64_t xy, xz, yz, yx, zx, zy;
    };"""

    def __init__(self, xy, xz, yz, yx, zx, zy):
        self.xy, xz, yz, yx, zx, zy = xy, xz, yz, yx, zx, zy

    @classmethod
    def deserialize(cls, payload: bytes):
        xy, xz, yz, yx, zx, zy = struct.unpack("6d", payload)
        return dict(xy=xy, xz=xz, yz=yz, yx=yx, zx=zx, zy=zy)


class navcon_pose_filter_calibration_data(CustomClass):
    """struct navcon_pose_filter_calibration_data {
    navcon_ns_ts_t msg_ts;

    navcon_vec3d gyro_bias;
    navcon_vec3d accel_bias;

    float64_t left_wheel_scale;
    float64_t right_wheel_scale;
    float64_t map_scale;

    navcon_vec3d gyro_scale;
    navcon_vec3d accel_scale;

    cross_axis_params gyro_cross_axis;
    cross_axis_params accel_cross_axis;

    #define NAVCON_PROTOCOL_POSE_FILTER_CALIBRATION_DATA_SIZE_BEFORE_23_02_2021 (sizeof(struct navcon_pose_filter_calibration_data) - sizeof(double)*18)
    }"""

    def __init__(
        self,
        msg_ts,
        gyro_bias,
        accel_bias,
        left_wheel_scale,
        right_wheel_scale,
        map_scale,
        gyro_scale,
        accel_scale,
        gyro_cross_axis,
        accel_cross_axis,
    ):
        self.msg_ts = msg_ts
        self.gyro_bias = gyro_bias
        self.accel_bias = accel_bias
        self.left_wheel_scale = left_wheel_scale
        self.right_wheel_scale = right_wheel_scale
        self.map_scale = map_scale
        self.gyro_scale = gyro_scale
        self.accel_scale = accel_scale
        self.gyro_cross_axis = gyro_cross_axis
        self.accel_cross_axis = accel_cross_axis

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        gyro_bias = navcon_vec3d.deserialize(payload[8:32])
        accel_bias = navcon_vec3d.deserialize(payload[32:56])
        left_wheel_scale = struct.unpack("d", payload[56:64])[0]
        right_wheel_scale = struct.unpack("d", payload[64:72])[0]
        map_scale = struct.unpack("d", payload[72:80])[0]
        gyro_scale = navcon_vec3d.deserialize(payload[80:104])
        accel_scale = navcon_vec3d.deserialize(payload[104:128])
        gyro_cross_axis = cross_axis_params.deserialize(payload[128:176])
        accel_cross_axis = cross_axis_params.deserialize(payload[176:])
        return dict(
            msg_ts=msg_ts,
            gyro_bias=gyro_bias,
            accel_bias=accel_bias,
            left_wheel_scale=left_wheel_scale,
            right_wheel_scale=right_wheel_scale,
            map_scale=map_scale,
            gyro_scale=gyro_scale,
            accel_scale=accel_scale,
            gyro_cross_axis=gyro_cross_axis,
            accel_cross_axis=accel_cross_axis,
        )


class NavconTempsensor(Enum):
    BOARD = 0
    CPU = 1
    GPU = 2
    IMU = 3
    _NAVCON_TEMPSENSOR_COUNT = 4


class navcon_temperature(CustomClass):
    """struct navcon_temperature {
    navcon_ns_ts_t msg_ts;
    float32_t celsius;
    navcon_tempsensor_rep sensor;
    uint8_t pad0[3];
    }"""

    def __init__(self, msg_ts, celsius, sensor):
        self.msg_ts = msg_ts
        self.celsius = celsius
        self.sensor = sensor

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        celsius = struct.unpack("f", payload[8:12])[0]
        sensor = struct.unpack("B", payload[12:13])[0]
        sensor = NavconTempsensor(sensor)
        # pad0 = struct.unpack("3B", payload[13:16])[0]
        assert len(payload) == 16
        return dict(
            msg_ts=msg_ts,
            celsius=celsius,
            sensor=sensor.name,
        )


class navcon_speed_limit(CustomClass):
    """struct navcon_speed_limit {
    navcon_ns_ts_t msg_ts;
    uint32_t id;
    /** Speed limit in mm/s */
    uint16_t speed_limit;
    uint8_t pad_0[2];
    }"""

    def __init__(self, msg_ts, id, speed_limit):
        self.msg_ts = msg_ts
        self.id = id
        self.speed_limit = speed_limit

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        id = struct.unpack("I", payload[8:12])[0]
        speed_limit = struct.unpack("H", payload[12:14])[0]
        # pad_0 = struct.unpack("2B", payload[14:16])[0]
        assert len(payload) == 16
        return dict(
            msg_ts=msg_ts,
            id=id,
            speed_limit=speed_limit,
        )


class navcon_image_metadata(CustomClass):
    """struct navcon_image_metadata {
    /**
    * navcon timestamp for this message.
    */
    navcon_ns_ts_t msg_ts;
    /**
    * navcon timestamp corresponding to the time at which the described image
    * was captured.
    */
    navcon_ns_ts_t capture_ts;
    /**
    * sequence number for the described image.
    */
    uint64_t sequence;
    /**
    * auto exposure control intensity value which was in use
    * while capturing the described image.
    *
    * this value will be 0.0 if aec was disabled during the capture.
    */
    float64_t aec_intensity;
    /**
    * exposure time which was in use while capturing the described image.
    */
    uint32_t exp_time_us;
    /**
    * gain which was in use while capturing the described image.
    * gain units are determined by the camera config message.
    */
    uint32_t gain;
    /**
    * camera index for the described camera.
    */
    uint8_t cam_idx;
    uint8_t pad_0[7];
    }"""

    def __init__(
        self,
        msg_ts,
        capture_ts,
        sequence,
        aec_intensity,
        exp_time_us,
        gain,
        cam_idx,
    ):
        self.msg_ts = msg_ts
        self.capture_ts = capture_ts
        self.sequence = sequence
        self.aec_intensity = aec_intensity
        self.exp_time_us = exp_time_us
        self.gain = gain
        self.cam_idx = cam_idx

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts, capture_ts, sequence = struct.unpack("3Q", payload[:24])
        aec_intensity = struct.unpack("d", payload[24:32])[0]
        exp_time_us = struct.unpack("I", payload[32:36])[0]
        gain = struct.unpack("I", payload[36:40])[0]
        cam_idx = struct.unpack("B", payload[40:41])[0]
        # pad_0 = struct.unpack("7B", payload[41:48])[0]
        assert len(payload) == 48
        return dict(
            msg_ts=msg_ts,
            capture_ts=capture_ts,
            sequence=sequence,
            aec_intensity=aec_intensity,
            exp_time_us=exp_time_us,
            gain=gain,
            cam_idx=cam_idx,
        )


class navcon_localizer_cam_select(CustomClass):
    """struct navcon_localizer_cam_select {
    navcon_ns_ts_t msg_ts;

    /**
    * A bit defining manual (1) or automatic (0) camera selection for localization.
    * If manual is selected, it will continually use those same cameras until the next
    * manual selection, or until automatic mode is turned back on.
    */
    uint8_t manual;

    /**
    * A bitfield representing the cameras which should be used for localization.
    */
    uint8_t cams;

    /**
    * A bitfield representing the cameras which should be used for localization next.
    */
    uint8_t next_cams;

    /**
    * Padding for message extension.
    */
    uint8_t pad_0[13];
    }"""

    def __init__(self, msg_ts, manual, cams, next_cams):
        self.msg_ts = msg_ts
        self.manual = manual
        self.cams = cams
        self.next_cams = next_cams

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        manual = struct.unpack("B", payload[8:9])[0]
        cams = struct.unpack("B", payload[9:10])[0]
        next_cams = struct.unpack("B", payload[10:11])[0]
        # pad_0 = struct.unpack("13B", payload[11:24])[0]
        assert len(payload) == 24
        return dict(
            msg_ts=msg_ts,
            manual=manual,
            cams=cams,
            next_cams=next_cams,
        )


class navcon_encoder_update(CustomClass):
    """struct navcon_encoder_update {
        navcon_ns_ts_t msg_ts;
        navcon_encoder_tick_t left_ticks;
        navcon_encoder_tick_t right_ticks;
    }"""

    def __init__(self, msg_ts, left_ticks, right_ticks):
        self.msg_ts = msg_ts
        self.left_ticks = left_ticks
        self.right_ticks = right_ticks

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts, left_ticks, right_ticks = struct.unpack("Qii", payload)
        return dict(
            msg_ts=msg_ts,
            left_ticks=left_ticks,
            right_ticks=right_ticks,
        )


class navcon_telemetry_version(CustomClass):
    """struct navcon_telemetry_version {
    navcon_ns_ts_t msg_ts;
    uint64_t unit_id;
    uint32_t api_ver;
    uint32_t sw_ver;
    uint8_t pad[8];
    }"""

    def __init__(self, msg_ts, unit_id, api_ver, sw_ver):
        self.msg_ts = msg_ts
        self.unit_id = unit_id
        self.api_ver = api_ver
        self.sw_ver = sw_ver

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        unit_id = struct.unpack("Q", payload[8:16])[0]
        api_ver = struct.unpack("I", payload[16:20])[0]
        sw_ver = struct.unpack("I", payload[20:24])[0]
        # pad=struct.unpack('8B', payload[24:32])[0]
        assert len(payload) == 32
        return dict(
            msg_ts=msg_ts,
            unit_id=unit_id,
            api_ver=api_ver,
            sw_ver=sw_ver,
        )


class navcon_timestamp_correlation(CustomClass):
    """struct navcon_timestamp_correlation {
        /**
         * The value of the navcon reference clock at the time just before this message
         * was constructed.
         */
        navcon_ns_ts_t msg_ts;
        /**
         * The value of the navcon system clock at the time just before this message
         * was constructed.
         *
         * This represents nanoseconds since the system time epoch, and is subject
         * to ntp adjustments, and is not guaranteed to be monotonic.
         */
        navcon_ns_ts_t sys_ts;
    }"""

    def __init__(self, msg_ts, sys_ts):
        self.msg_ts = msg_ts
        self.sys_ts = sys_ts

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts, sys_ts = struct.unpack("QQ", payload)
        return dict(
            msg_ts=msg_ts,
            sys_ts=sys_ts,
        )


class DonutEvent(Enum):
    """
    typedef enum {
        DONUT_EVENT_NONE,
        DONUT_EVENT_BUMP,
        DONUT_EVENT_OUTSIDEBOUNDARY
    } donut_event_t;
    """

    NONE = 0
    BUMP = 1
    OUTSIDEBOUNDARY = 2


class navcon_donut_status(CustomClass):
    """struct navcon_donut_status {
        navcon_ns_ts_t msg_ts;
        uint64_t pose_filter_tov;
        float distance_to_boundary;
        donut_event_rep event;
        uint8_t pad[3];
    }"""

    def __init__(self, msg_ts, pose_filter_tov, distance_to_boundary, event):
        self.msg_ts = msg_ts
        self.pose_filter_tov = pose_filter_tov
        self.distance_to_boundary = distance_to_boundary
        self.event = event

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        pose_filter_tov = struct.unpack("Q", payload[8:16])[0]
        distance_to_boundary = struct.unpack("f", payload[16:20])[0]
        event = struct.unpack("B", payload[20:21])[0]
        event = DonutEvent(event)
        # pad = struct.unpack("3B", payload[21:24])[0]
        assert len(payload) == 24
        return dict(
            msg_ts=msg_ts,
            pose_filter_tov=pose_filter_tov,
            distance_to_boundary=distance_to_boundary,
            event=event,
        )


class navcon_pose_std_dev(CustomClass):
    """
    typedef struct {
    /**
     * position, in nacon map frame.
     */
    navcon_vec3d position;
    /**
     * orientation, in angle-axis form.
     */
        navcon_vec3d orientation_aa;
    } navcon_pose_6d;
    """

    def __init__(self, position, orientation_aa):
        self.position = position
        self.orientation_aa = orientation_aa

    @classmethod
    def deserialize(cls, payload: bytes):
        position = navcon_vec3d.deserialize(payload[:24])
        orientation_aa = navcon_vec3d.deserialize(payload[24:])
        return dict(
            position=position,
            orientation_aa=orientation_aa,
        )


class navcon_pose_6d(navcon_pose_std_dev):
    pass


class pos_cov_off_diag(CustomClass):
    """typedef struct {
        float64_t xy, xz, yz;
    } pos_cov_off_diag;"""

    def __init__(self, xy, xz, yz):
        (self.xy, xz, yz,) = (
            xy,
            xz,
            yz,
        )

    @classmethod
    def deserialize(cls, payload: bytes):
        xy, xz, yz = struct.unpack("3d", payload)
        return dict(
            xy=xy,
            xz=xz,
            yz=yz,
        )


class NavconPoseFilterSensorUpdateBit(IntEnum):
    """
    typedef enum {
        NAVCON_POSE_FILTER_SENSOR_UPDATE_BIT_ENCODER = 0,
        NAVCON_POSE_FILTER_SENSOR_UPDATE_BIT_GPS,
        NAVCON_POSE_FILTER_SENSOR_UPDATE_BIT_CALLED_SHOT,
        NAVCON_POSE_FILTER_SENSOR_UPDATE_BIT_IMU,
        NAVCON_POSE_FILTER_SENSOR_UPDATE_BIT_DOCKING_CALLED_SHOT
    } navcon_pose_filter_sensor_update_bit_t;
    """

    ENCODER = 0
    GPS = 1
    CALLED_SHOT = 2
    IMU = 3
    DOCKING_CALLED_SHOT = 4


class NavconPoseFilterErrorBit(IntEnum):
    """
    typedef enum {
        NAVCON_POSE_FILTER_ERROR_BIT_LATE_MESSAGE = 0,
        NAVCON_POSE_FILTER_ERROR_BIT_FUTURE_MESSAGE,
        NAVCON_POSE_FILTER_ERROR_BIT_IMU_GAP,
        NAVCON_POSE_FILTER_ERROR_BIT_ENCODER_GAP
    } navcon_pose_filter_error_bit_t;
    """

    LATE_MESSAGE = 0
    FUTURE_MESSAGE = 1
    IMU_GAP = 2
    ENCODER_GAP = 3


class navcon_pose_filter(CustomClass):
    """struct navcon_pose_filter {
    navcon_ns_ts_t msg_ts;

    navcon_vec3d position;
    navcon_vec3d orient_aa;
    navcon_vec3d pos_std_dev;
    navcon_vec3d orient_std_dev;
    navcon_vec3d velocity;
    navcon_vec3d ang_velocity;

    #define NAVCON_PROTOCOL_POSE_FILTER_MAGIC   ((uint32_t)0x0dadf33d)

    /**
        * magic value for primitive validity/corruption detection.
        * set to NAVCON_PROTOCOL_POSE_FILTER_MAGIC.
        */
    uint32_t magic;

    navcon_pose_filter_sensor_update_flag_rep sensor_update_flags;
    navcon_map_id_t map_id;

    navcon_pose_filter_error_flag_rep error_flags;
    uint8_t pad_0[1];

    pos_cov_off_diag pos_cov;

    #define NAVCON_PROTOCOL_POSE_FILTER_SIZE_BEFORE_30_04_2020 (sizeof(struct navcon_pose_filter) - sizeof(pos_cov_off_diag))
    }"""

    def __init__(
        self,
        msg_ts,
        position,
        orient_aa,
        pos_std_dev,
        orient_std_dev,
        velocity,
        ang_velocity,
        magic,
        sensor_update_flags,
        map_id,
        error_flags,
        pos_cov,
    ):
        self.msg_ts = msg_ts
        self.position = position
        self.orient_aa = orient_aa
        self.pos_std_dev = pos_std_dev
        self.orient_std_dev = orient_std_dev
        self.velocity = velocity
        self.ang_velocity = ang_velocity
        self.magic = magic
        self.sensor_update_flags = sensor_update_flags
        self.map_id = map_id
        self.error_flags = error_flags
        self.pos_cov = pos_cov

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        position = navcon_vec3d.deserialize(payload[8:32])
        orient_aa = navcon_vec3d.deserialize(payload[32:56])
        pos_std_dev = navcon_vec3d.deserialize(payload[56:80])
        orient_std_dev = navcon_vec3d.deserialize(payload[80:104])
        velocity = navcon_vec3d.deserialize(payload[104:128])
        ang_velocity = navcon_vec3d.deserialize(payload[128:152])
        magic = struct.unpack("I", payload[152:156])[0]
        assert magic == 0x0DADF33D

        sensor_update_flags = struct.unpack("B", payload[156:157])[0]
        sensor_update_flags = convert_bitflag_to_list_enums(
            bit_encoded_value=sensor_update_flags, enum=NavconPoseFilterSensorUpdateBit
        )
        map_id = struct.unpack("B", payload[157:158])[0]
        error_flags = struct.unpack("B", payload[158:159])[0]
        error_flags = convert_bitflag_to_list_enums(
            bit_encoded_value=error_flags, enum=NavconPoseFilterErrorBit
        )
        # pad_0 = struct.unpack("1B", payload[159:160])[0]
        pos_cov = pos_cov_off_diag.deserialize(payload=payload[160:])
        assert len(payload) == 184
        return dict(
            msg_ts=msg_ts,
            position=position,
            orient_aa=orient_aa,
            pos_std_dev=pos_std_dev,
            orient_std_dev=orient_std_dev,
            velocity=velocity,
            ang_velocity=ang_velocity,
            magic=magic,
            sensor_update_flags=sensor_update_flags,
            map_id=map_id,
            error_flags=error_flags,
            pos_cov=pos_cov,
        )


class navcon_cov_6d_upper_triangle(CustomClass):
    """struct navcon_cov_6d_upper_triangle
    {
    /**
    * square root of the pose covariance.
    */
    float64_t data[21];
    }"""

    def __init__(self, data):
        self.data = data

    @classmethod
    def deserialize(cls, payload: bytes):
        data = list(struct.unpack("21d", payload[0:168]))
        assert len(payload) == 168
        return dict(
            data=data,
        )


class NavconCalledShotType(Enum):
    """
    typedef enum {
        NAVCON_CALLED_SHOT_TYPE_CALL,
        NAVCON_CALLED_SHOT_TYPE_MATCH_POSE,
        NAVCON_CALLED_SHOT_TYPE_TRACK_POSE,
        NAVCON_CALLED_SHOT_TYPE_DOCK_POSE,
        NAVCON_CALLED_SHOT_TYPE_CANCEL
    } navcon_called_shot_type_t;
    """

    CALL = 0
    MATCH_POSE = 1
    TRACK_POSE = 2
    DOCK_POSE = 3
    CANCEL = 4


class navcon_called_shot(CustomClass):
    """
    Note a called shot pose is the complete
    version of a called shot. If the shot_id
    is not call or cancel, all the members after
    type are valid

    struct navcon_called_shot_pose {
    navcon_ns_ts_t msg_ts;
    navcon_called_shot_id_t shot_id;
    navcon_called_shot_type_rep type;
    navcon_map_id_t map_id;

    /*
     * Flag (i.e. 0 = false, 1 = true) to indicate whether a safety check message
     * is sent with this called shot pose. The safety check message
     * (navcon_safety_localization_poses) will share the same shot_id.
     */
    uint8_t associated_safety_check;

    uint8_t pad_0[1];

    /**
     * Pose in navcon map frame.
     */
    navcon_pose_6d pose;
    /**
     * Pose uncertainty (standard deviation), in meters.
     */
    union {
        navcon_cov_6d_upper_triangle covariance;
        navcon_pose_std_dev old_std_dev;
    };

    /**
     * A bitfield representing the cameras which cameras were used to produce the pose.
     * Value of 0 represents unknown camera usage.
     */
    uint8_t cams;

    /**
     * Padding for message extension
     */
    uint8_t pad_1[7];
    }"""

    def __init__(
        self,
        msg_ts,
        shot_id,
        type,
        map_id,
        associated_safety_check,
        pose,
        covariance,
        cams,
    ):
        self.msg_ts = msg_ts
        self.shot_id = shot_id
        self.type = type
        self.map_id = map_id
        self.associated_safety_check = associated_safety_check
        self.pose = pose
        self.covariance = covariance
        self.cams = cams

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        shot_id = struct.unpack("I", payload[8:12])[0]
        type = struct.unpack("B", payload[12:13])[0]
        type = NavconCalledShotType(type)

        if type == NavconCalledShotType.CALL or type == NavconCalledShotType.CANCEL:
            assert len(payload) == 16
            return dict(
                msg_ts=msg_ts,
                shot_id=shot_id,
                type=type,
            )
        else:
            map_id = struct.unpack("B", payload[13:14])[0]
            associated_safety_check = struct.unpack("B", payload[14:15])[0] == 1
            pose = navcon_pose_6d.deserialize(payload[16:64])
            covariance = navcon_cov_6d_upper_triangle.deserialize(payload[64:232])
            cams = struct.unpack("B", payload[232:233])[0]
            assert len(payload) == 240
            return dict(
                msg_ts=msg_ts,
                shot_id=shot_id,
                type=type,
                map_id=map_id,
                associated_safety_check=associated_safety_check,
                pose=pose,
                covariance=covariance,
                cams=cams,
            )


class navcon_safety_localization_poses(CustomClass):
    """struct navcon_safety_localization_poses {
    /**
        * navcon timestamp for this message.
        */
    navcon_ns_ts_t msg_ts;

    /**
        * The id of the corresponding called shot message which preceded this
        * message in the stream.
        */
    navcon_called_shot_id_t shot_id;

    uint8_t pad_0[12];

    /**
        * Localization sequence id.
        */
    uint64_t localization_sequence;

    /**
        * Mainline pose in navcon map frame.
        */
    navcon_pose_6d mainline_pose;

    /**
        * Mainline pose covariance.
        */
    navcon_cov_6d_upper_triangle mainline_covariance;

    /**
        * Safety pose in navcon map frame.
        */
    navcon_pose_6d safety_pose;

    /**
        * Safety pose covariance.
        */
    navcon_cov_6d_upper_triangle safety_covariance;
    }"""

    def __init__(
        self,
        msg_ts,
        shot_id,
        localization_sequence,
        mainline_pose,
        mainline_covariance,
        safety_pose,
        safety_covariance,
    ):
        self.msg_ts = msg_ts
        self.shot_id = shot_id
        self.localization_sequence = localization_sequence
        self.mainline_pose = mainline_pose
        self.mainline_covariance = mainline_covariance
        self.safety_pose = safety_pose
        self.safety_covariance = safety_covariance

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        shot_id = struct.unpack("I", payload[8:12])[0]
        # pad_0 = struct.unpack("12B", payload[12:24])[0]
        localization_sequence = struct.unpack("Q", payload[24:32])[0]
        mainline_pose = navcon_pose_6d.deserialize(payload[32:80])
        mainline_covariance = navcon_cov_6d_upper_triangle.deserialize(payload[80:248])
        safety_pose = navcon_pose_6d.deserialize(payload[248:296])
        safety_covariance = navcon_cov_6d_upper_triangle.deserialize(payload[296:464])
        assert len(payload) == 464
        return dict(
            msg_ts=msg_ts,
            shot_id=shot_id,
            localization_sequence=localization_sequence,
            mainline_pose=mainline_pose,
            mainline_covariance=mainline_covariance,
            safety_pose=safety_pose,
            safety_covariance=safety_covariance,
        )


class navcon_fault_message(CustomClass):
    """struct navcon_fault_message {
    navcon_ns_ts_t msg_ts;
    uint16_t fault_count;
    #define NAVCON_FAULT_MSG_MAXCOUNT (128)
    uint8_t pad_0[6];
    navcon_fault_code_rep faults[0];
    }"""

    def __init__(self, msg_ts, fault_count, faults):
        self.msg_ts = msg_ts
        self.fault_count = fault_count
        self.faults = faults

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        fault_count = struct.unpack("H", payload[8:10])[0]
        # pad_0 = struct.unpack("6B", payload[10:16])[0]
        faults = []
        temp = struct.unpack(f"{fault_count}I", payload[16:])
        for fault in temp:

            faults.append(parse_fault(fault=fault))

        # faults=struct.unpack('6B', payload[16:16])[0]
        return dict(
            msg_ts=msg_ts,
            fault_count=fault_count,
            faults=faults,
        )


class NavconStateSender(Enum):
    """
    typedef enum {
        NAVCON_STATE_SENDER_UNKNOWN,
        NAVCON_STATE_SENDER_BHC,
        NAVCON_STATE_SENDER_NAVCON_NAVCONMSG,
        NAVCON_STATE_SENDER_NAVCON_DEBUG_MONITOR,
        NAVCON_STATE_SENDER_NAVCON_FRAMEWORK_STATE,

        _NAVCON_STATE_SENDER_COUNT
    } navcon_state_sender_t;
    """

    UNKNOWN = 0
    BHC = 1
    NAVCON_NAVCONMSG = 2
    NAVCON_DEBUG_MONITOR = 3
    NAVCON_FRAMEWORK_STATE = 4


class navcon_payload_desired_state(CustomClass):
    """struct navcon_payload_desired_state {
    uint8_t client_id;
    uint8_t pad[3];
    }"""

    def __init__(self, client_id):
        self.client_id = client_id

    @classmethod
    def deserialize(cls, payload: bytes):
        client_id = struct.unpack("B", payload[0:1])[0]
        # pad=struct.unpack('3B', payload[1:4])[0]
        assert len(payload) == 4
        return dict(
            client_id=client_id,
        )


class navcon_desired_state(CustomClass):
    """struct navcon_desired_state {
    navcon_ns_ts_t msg_ts;
    navcon_state_rep state;
    navcon_state_sender_rep sender;
    uint8_t pad_0[2];
    uint32_t payload_size;
    uint8_t payload[0];
    }"""

    def __init__(self, msg_ts, state, sender, payload_size, payload):
        self.msg_ts = msg_ts
        self.state = state
        self.sender = sender
        self.payload_size = payload_size
        self.payload = payload

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        state = struct.unpack("B", payload[8:9])[0]
        state = NavconState(state)
        sender = struct.unpack("B", payload[9:10])[0]
        sender = NavconStateSender(sender)
        # pad_0=struct.unpack('2B', payload[10:12])[0]
        payload_size = struct.unpack("I", payload[12:16])[0]
        # _payload = struct.unpack(f"{payload_size}B", payload[16:])
        _payload = payload[16:]
        res = []
        for i in range(0, len(_payload), 4):
            res.append(navcon_payload_desired_state.deserialize(_payload[i : i + 4]))  # type: ignore
        return dict(
            msg_ts=msg_ts,
            state=state.name,
            sender=sender.name,
            payload_size=payload_size,
            payload=res,
        )


class navcon_health(CustomClass):
    """struct navcon_health {
    navcon_ns_ts_t msg_ts;
    /**
        * A bitfield where each bit corresponds to a component as defined in
        * navcon_health_bit_t.
        */
    navcon_health_flag_rep health_flags;
    uint8_t pad_0[6];
    }"""

    def __init__(self, msg_ts, health_flags):
        self.msg_ts = msg_ts
        self.health_flags = health_flags

    @classmethod
    def deserialize(cls, payload: bytes):
        msg_ts = struct.unpack("Q", payload[0:8])[0]
        health_flags = struct.unpack("H", payload[8:10])[0]
        health_flags = convert_bitflag_to_list_enums(
            bit_encoded_value=health_flags, enum=NavconHealthBit
        )
        # pad_0=struct.unpack('6B', payload[10:16])[0]
        assert len(payload) == 16, f"Expected 16 actual {len(payload)}"
        return dict(
            msg_ts=msg_ts,
            health_flags=health_flags,
        )

from enum import Enum


class NavconFaultCameraCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_CAMERA_NO_COMMS,
        _NAVCON_FAULT_CAMERA_FAULT_COUNT
    } navcon_fault_camera_code_t;
    """

    NAVCON_FAULT_CAMERA_NO_COMMS = 0


class NavconFaultDiskCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_DISK_FREE_CAPACITY,
        NAVCON_FAULT_DISK_NO_DRIVE,
        _NAVCON_FAULT_DISK_FAULT_COUNT
    } navcon_fault_disk_code_t;
    """

    NAVCON_FAULT_DISK_FREE_CAPACITY = 0
    NAVCON_FAULT_DISK_NO_DRIVE = 1


class NavconFaultDuroCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_DURO_NO_COMMS,
        NAVCON_FAULT_DURO_NO_RTK,
        NAVCON_FAULT_DURO_INS_MISSING,
        _NAVCON_FAULT_DURO_FAULT_COUNT
    } navcon_fault_duro_code_t;
    """

    NAVCON_FAULT_DURO_NO_COMMS = 0
    NAVCON_FAULT_DURO_NO_RTK = 1
    NAVCON_FAULT_DURO_INS_MISSING = 2


class NavconFaultEncodersCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_ENCODERS_NO_COMMS,
        _NAVCON_FAULT_ENCODERS_FAULT_COUNT
    } navcon_fault_encoders_code_t;
    """

    NAVCON_FAULT_ENCODERS_NO_COMMS = 0


class NavconFaultGpsCode(Enum):
    """

    typedef enum {
        NAVCON_FAULT_GPS_NO_COMMS,
        NAVCON_FAULT_GPS_NOT_ENOUGH_SATS,
        NAVCON_FAULT_GPS_NO_3D_FIX,
        _NAVCON_FAULT_GPS_FAULT_COUNT
    } navcon_fault_gps_code_t;
    """

    NAVCON_FAULT_GPS_NO_COMMS = 0
    NAVCON_FAULT_GPS_NOT_ENOUGH_SATS = 1
    NAVCON_FAULT_GPS_NO_3D_FIX = 2


class NavconFaultImuCode(Enum):
    """

    typedef enum {
        NAVCON_FAULT_IMU_NO_COMMS,
        _NAVCON_FAULT_IMU_FAULT_COUNT
    } navcon_fault_imu_code_t;
    """

    NAVCON_FAULT_IMU_NO_COMMS = 0


class NavconFaultLightingCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_LIGHTING_PWM_DISABLED,
        _NAVCON_FAULT_LIGHTING_FAULT_COUNT
    } navcon_fault_lighting_code_t;
    """

    NAVCON_FAULT_LIGHTING_PWM_DISABLED = 0


class NavconFaultProcessCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_PROCESS_FRAMEWORK_UNHEALTHY,
        _NAVCON_FAULT_PROCESS_FAULT_COUNT
    } navcon_fault_process_code_t;
    """

    NAVCON_FAULT_PROCESS_FRAMEWORK_UNHEALTHY = 0


class NavconFaultSystemCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_SYSTEM_TIME_SYNC,
        NAVCON_FAULT_SYSTEM_FPGA_NOT_PROGRAMMED,
        NAVCON_FAULT_SYSTEM_LOW_AVAILABLE_MEMORY,
        NAVCON_FAULT_SYSTEM_OVER_TEMPERATURE,
        NAVCON_FAULT_SYSTEM_LOW_AVAILABLE_SWAP,
        _NAVCON_FAULT_SYSTEM_FAULT_COUNT
    } navcon_fault_system_code_t;
    """

    NAVCON_FAULT_SYSTEM_TIME_SYNC = 0
    NAVCON_FAULT_SYSTEM_FPGA_NOT_PROGRAMMED = 1
    NAVCON_FAULT_SYSTEM_LOW_AVAILABLE_MEMORY = 2
    NAVCON_FAULT_SYSTEM_OVER_TEMPERATURE = 3
    NAVCON_FAULT_SYSTEM_LOW_AVAILABLE_SWAP = 4


class NavconFaultWirelessCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_WIRELESS_INTERFACE_DOWN,
        _NAVCON_FAULT_WIRELESS_FAULT_COUNT
    } navcon_fault_wireless_code_t;
    """

    NAVCON_FAULT_WIRELESS_INTERFACE_DOWN = 0


class NavconFaultConfigCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_CONFIG_APP_CONFIG_INVALID,
        NAVCON_FAULT_CONFIG_UNIT_CONFIG_INVALID,
        NAVCON_FAULT_CONFIG_UNIT_CONFIG_EMPTY,
        NAVCON_FAULT_CONFIG_UNIT_CONFIG_INTRINSICS_MISMATCH,
        _NAVCON_FAULT_CONFIG_FAULT_COUNT
    } navcon_fault_config_code_t;
    """

    NAVCON_FAULT_CONFIG_APP_CONFIG_INVALID = 0
    NAVCON_FAULT_CONFIG_UNIT_CONFIG_INVALID = 1
    NAVCON_FAULT_CONFIG_UNIT_CONFIG_EMPTY = 2
    NAVCON_FAULT_CONFIG_UNIT_CONFIG_INTRINSICS_MISMATCH = 3


class NavconFaultDockingCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_DOCKING_NO_DETECTIONS,
        NAVCON_FAULT_DOCKING_TOO_FAR_FROM_DOCK,
        _NAVCON_FAULT_DOCKING_FAULT_COUNT
    } navcon_fault_docking_code_t;
    """

    NAVCON_FAULT_DOCKING_NO_DETECTIONS = 0
    NAVCON_FAULT_DOCKING_TOO_FAR_FROM_DOCK = 1


class NavconFaultLocalizationCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_LOCALIZATION_INIT_FAILURE,
        _NAVCON_FAULT_LOCALIZATION_FAULT_COUNT
    } navcon_fault_localization_code_t;
    """

    NAVCON_FAULT_LOCALIZATION_INIT_FAILURE = 0


class NavconFaultDatabaseCode(Enum):
    """
    typedef enum {
        NAVCON_FAULT_DATABASE_UNREADABLE,
        _NAVCON_FAULT_DATABASE_FAULT_COUNT
    } navcon_fault_database_code_t;
    """

    NAVCON_FAULT_DATABASE_UNREADABLE = 0


class NavconFaultReporterId(Enum):
    """
    typedef enum {
        /* camera IDs are expected to remain together, s.t.
         * CAMERA_0 + 1 == CAMERA_1, etc. */
        NAVCON_FAULT_REPORTER_ID_CAMERA_0,
        NAVCON_FAULT_REPORTER_ID_CAMERA_1,
        NAVCON_FAULT_REPORTER_ID_CAMERA_2,
        NAVCON_FAULT_REPORTER_ID_CAMERA_3,
        /* 4 */
        NAVCON_FAULT_REPORTER_ID_CUTTER,
        NAVCON_FAULT_REPORTER_ID_DISK,
        NAVCON_FAULT_REPORTER_ID_DURO,
        NAVCON_FAULT_REPORTER_ID_ENCODERS,
        /* 8 */
        NAVCON_FAULT_REPORTER_ID_GPS,
        NAVCON_FAULT_REPORTER_ID_IMU,
        NAVCON_FAULT_REPORTER_ID_LIGHTING,
        NAVCON_FAULT_REPORTER_ID_SYSTEM,
        /* 12 */
        NAVCON_FAULT_REPORTER_ID_WIRELESS,
        NAVCON_FAULT_REPORTER_ID_CONFIG,
        NAVCON_FAULT_REPORTER_ID_DATABASE,
        NAVCON_FAULT_REPORTER_ID_DOCKING,
        /* 16 */
        NAVCON_FAULT_REPORTER_ID_LOCALIZATION,
        _NAVCON_FAULT_REPORTER_COUNT
    } navcon_fault_reporter_id_t
    """

    CAMERA_0 = 0
    CAMERA_1 = 1
    CAMERA_2 = 2
    CAMERA_3 = 3
    CUTTER = 4
    DISK = 5
    DURO = 6
    ENCODERS = 7
    GPS = 8
    IMU = 9
    LIGHTING = 10
    SYSTEM = 11
    WIRELESS = 12
    CONFIG = 13
    DATABASE = 14
    DOCKING = 15
    LOCALIZATION = 16


def convert_bitflag_to_list_enums(bit_encoded_value, enum):
    res = []
    bits = bin(bit_encoded_value)[2:]
    bits = reversed(bits)
    for i, binary_val in enumerate(bits):
        if binary_val == "1":
            res.append(enum(i).name)
    return res


def parse_fault(fault):
    fault_reporter_id = NavconFaultReporterId(fault & 0xFF)
    bit_encoded_value = fault >> 8
    match fault_reporter_id:
        case (
            NavconFaultReporterId.CAMERA_0
            | NavconFaultReporterId.CAMERA_1
            | NavconFaultReporterId.CAMERA_2
            | NavconFaultReporterId.CAMERA_3
        ):
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultCameraCode
            )
        case NavconFaultReporterId.CUTTER:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultProcessCode
            )
        case NavconFaultReporterId.DISK:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultDiskCode
            )
        case NavconFaultReporterId.DURO:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultDuroCode
            )
        case NavconFaultReporterId.ENCODERS:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultEncodersCode
            )
        case NavconFaultReporterId.GPS:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultGpsCode
            )
        case NavconFaultReporterId.IMU:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultImuCode
            )
        case NavconFaultReporterId.LIGHTING:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultLightingCode
            )
        case NavconFaultReporterId.SYSTEM:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultSystemCode
            )
        case NavconFaultReporterId.WIRELESS:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultWirelessCode
            )
        case NavconFaultReporterId.CONFIG:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultConfigCode
            )
        case NavconFaultReporterId.DATABASE:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultDatabaseCode
            )
        case NavconFaultReporterId.DOCKING:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultDockingCode
            )
        case NavconFaultReporterId.LOCALIZATION:
            return convert_bitflag_to_list_enums(
                bit_encoded_value, enum=NavconFaultLocalizationCode
            )
        case _:
            raise Exception(
                f"Invalid fault_reporter_id:{fault_reporter_id}, bit_encoded_value:{bit_encoded_value}, fault:{fault}"
            )

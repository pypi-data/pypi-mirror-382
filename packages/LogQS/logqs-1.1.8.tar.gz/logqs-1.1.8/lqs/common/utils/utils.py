import io
import os
import inspect
import logging
import random
import time
import base64
import struct
from functools import partial
from typing import Optional, Union

import av
import s3path
import bz2
import lz4.frame
import lz4.block
import zstandard
import numpy as np
import DracoPy as draco
from PIL import Image as ImagePIL
from PIL import ImageDraw
from mcap.data_stream import ReadDataStream
from mcap.records import Chunk
from pythonjsonlogger import jsonlogger


class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        return msg, kwargs

    def log(self, level, msg, *args, **kwargs):
        """
        Override the default 'log' method to inject custom contextual information into the LogRecord.
        """
        if self.isEnabledFor(level):
            frame = inspect.currentframe()
            # the frame is two levels up
            stack_info = inspect.getouterframes(frame)[3][0]
            if stack_info:
                # Extracting filename, line number, and function name from the frame
                filename = stack_info.f_code.co_filename
                lineno = stack_info.f_lineno
                func_name = stack_info.f_code.co_name
                record = self.logger.makeRecord(
                    self.logger.name,
                    level,
                    filename,
                    lineno,
                    msg,
                    args,
                    None,
                    func_name,
                    extra=self.extra,
                )
                self.logger.handle(record)


def get_logger(
    name,
    level: Optional[str] = None,
    log_to_file: bool = False,
    json_logging: bool = False,
    correlation_id: str | None = None,
):
    log_level = level or os.environ.get("LOG_LEVEL", "INFO")
    if isinstance(log_level, str):
        log_level = log_level.upper()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    # logger.propagate = False
    if logger.hasHandlers():
        return ContextLoggerAdapter(logger, {"correlation_id": correlation_id})
    correlation_id_str = "%(correlation_id)s:" if correlation_id else ""
    if json_logging:
        formatter = jsonlogger.JsonFormatter(
            f"%(asctime)s %(levelname)s {correlation_id_str} %(name)s %(filename)s %(funcName)s %(lineno)s %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        formatter = logging.Formatter(
            f"%(asctime)s  (%(levelname)s - %(name)s): {correlation_id_str} %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if log_to_file:
            handler = logging.FileHandler("lqs.log")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    return ContextLoggerAdapter(logger, {"correlation_id": correlation_id})


def attempt_with_retries(
    func,
    fargs=None,
    fkwargs=None,
    exceptions=Exception,
    tries=3,
    delay=1.0,
    max_delay=None,
    backoff=2,
    jitter=0,
    message=None,
    logging_func=None,
):
    args = fargs if fargs else list()
    kwargs = fkwargs if fkwargs else dict()
    f = partial(func, *args, **kwargs)
    _tries, _delay = tries, delay
    attempt = 1
    while _tries:
        try:
            return f()
        except exceptions as e:
            _tries -= 1
            if not _tries:
                raise

            if logging_func is not None:
                if message is None:
                    warning_message = f"Failed on attempt {attempt}: {e}; retrying in {_delay} seconds..."
                else:
                    warning_message = f'Failed "{message}" on attempt {attempt}: {e}; retrying in {_delay} seconds...'
                logging_func(warning_message)

            attempt += 1
            time.sleep(_delay)
            _delay *= backoff
            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter
            if max_delay is not None:
                _delay = min(_delay, max_delay)


def get_relative_object_path(object_key: str, source: str):
    if source is None:
        return object_key
    if not object_key.endswith("/"):
        object_key = object_key.rsplit("/", 1)[0] + "/"
    return str(s3path.PureS3Path(object_key + source))


def decompress_chunk_bytes(chunk_bytes, chunk_compression, chunk_length=None):
    if chunk_compression == "bz2":
        decompressed_bytes = bz2.decompress(chunk_bytes)
    elif chunk_compression == "lz4":
        decompressed_bytes = lz4.frame.decompress(chunk_bytes)
    elif chunk_compression == "zstd_mcap":
        chunk = ModifiedChunk.read(ReadDataStream(io.BytesIO(chunk_bytes)))
        return zstandard.decompress(chunk.data, chunk.uncompressed_size)
    elif chunk_compression == "zstd":
        decompressed_bytes = zstandard.decompress(chunk_bytes)
    elif chunk_compression == "lz4_block":
        if chunk_length is None:
            raise ValueError("Must specify chunk_length when decompressing lz4_block")
        decompressed_bytes = lz4.block.decompress(chunk_bytes, chunk_length)
    elif chunk_compression in [None, "none", ""]:
        decompressed_bytes = chunk_bytes
    elif chunk_compression == "mp4":
        decompressed_bytes = chunk_bytes
    else:
        raise ValueError(f"Unknown chunk compression type: {chunk_compression}")
    return decompressed_bytes


# Image

image_type_names = [
    "sensor_msgs/Image",
    "sensor_msgs/CompressedImage",
    "stereo_msgs/DisparityImage",
    "sensor_msgs/msg/Image",
    "sensor_msgs/msg/CompressedImage",
    "stereo_msgs/msg/DisparityImage",
    "ark::image::Image",
    "logqs.image",
    "logqs.inference.depth-estimation",
    "logqs.inference.image-to-image",
    "lqs_cutter/navcon_image",
]


def image_to_base64(
    image: ImagePIL.Image, format: str = "WEBP", format_params: dict = {}
) -> str:
    buffered_img = io.BytesIO()
    image.save(buffered_img, format=format, **format_params)
    return base64.b64encode(buffered_img.getvalue()).decode("utf-8")


def get_complete_segmentation_image(output, meta):
    image_size = (
        meta["image"]["width"],
        meta["image"]["height"],
    )
    img = ImagePIL.new("RGB", image_size, (0, 0, 0))
    for segmentation in output:
        mask_data = base64.b64decode(segmentation["mask"])
        mask = ImagePIL.open(io.BytesIO(mask_data)).convert("L")

        label = segmentation.get("label")
        if label is None:
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        else:
            color = int(hash(label) % 0xFFFFFF)
            color = (
                color & 0xFF,
                (color >> 8) & 0xFF,
                (color >> 16) & 0xFF,
            )
        draw = ImageDraw.Draw(img)
        draw.bitmap((0, 0), mask, fill=color)
    return img


def convert_avc1_to_annexb(data, filter_parameter_sets=True):
    # Wrap data in a memoryview and cache its length.
    mv = memoryview(data)
    mv_len = len(mv)
    offset = 0
    annexb = bytearray()
    start_code = b"\x00\x00\x00\x01"

    while offset + 4 <= mv_len:
        nal_length = struct.unpack_from(">I", mv, offset)[0]
        offset += 4
        # Validate NAL length.
        if nal_length <= 0 or offset + nal_length > mv_len:
            break
        # Avoid parameter set duplication.
        nal_unit = mv[offset : offset + nal_length].tobytes()
        offset += nal_length
        nal_type = nal_unit[0] & 0x1F
        if filter_parameter_sets and nal_type in (7, 8):
            continue
        annexb.extend(start_code)
        annexb.extend(nal_unit)
    return bytes(annexb)


def convert_hvc1_to_annexb(data):
    mv = memoryview(data)
    total_len = len(mv)
    offset = 0
    result = bytearray()
    start_code = b"\x00\x00\x00\x01"

    while offset + 4 <= total_len:
        nal_length = struct.unpack_from(">I", mv, offset)[0]
        offset += 4
        if nal_length <= 0 or offset + nal_length > total_len:
            break
        result.extend(start_code)
        result.extend(mv[offset : offset + nal_length])
        offset += nal_length
    return bytes(result)


def generate_image_from_frames(extradata, frames, frame_data, encoding):
    # Create the decoder and set extradata.
    codec = av.codec.CodecContext.create(encoding, "r")
    codec.extradata = extradata

    # Precompute start_offset and wrap frame_data in a memoryview.
    start_offset = frames[0][2]
    fd_mv = memoryview(frame_data)
    fd_len = len(fd_mv)
    converter = convert_hvc1_to_annexb if encoding == "hevc" else convert_avc1_to_annexb

    decoded_frames = None
    for frame in frames:
        # Compute slice boundaries once.
        offset_in_frame = frame[2] - start_offset
        size = frame[1]
        # Check bounds.
        if fd_len < offset_in_frame + size:
            break
        # Slice out the NAL unit data.
        nal_data = fd_mv[offset_in_frame : offset_in_frame + size]
        # Call the converter; if nal_data is already a memoryview, let the converter wrap it.
        frame_annexb = converter(nal_data)
        packet = av.Packet(frame_annexb)
        decoded_frames = codec.decode(packet)
    # We expect a single decoded frame.
    assert (
        decoded_frames is not None and len(decoded_frames) == 1
    ), f"Delta frame decoding failed: {len(decoded_frames) if decoded_frames else 0} frames decoded, expected 1"
    decoded_frame = decoded_frames[0]
    image = decoded_frame.to_image()
    return image


def get_record_image_lqs(record_data, **kwargs) -> ImagePIL.Image:
    if "frames" in kwargs:
        # if we've passed in frame information, then this is a video frame
        frames = kwargs["frames"]
        encoding = kwargs["encoding"]

        extradata = kwargs.get("extradata", None)
        if isinstance(extradata, str):
            extradata = base64.b64decode(extradata)

        frame_data = record_data
        if isinstance(frame_data, str):
            frame_data = base64.b64decode(frame_data)

        img = generate_image_from_frames(extradata, frames, frame_data, encoding)
    elif isinstance(record_data, str):
        # if the record data is a string, it is a base64 encoded image
        try:
            image_data = base64.b64decode(record_data)
        except Exception as e:
            raise Exception(f"Failed to decode record data: {e}")
        try:
            img = ImagePIL.open(io.BytesIO(image_data))
        except Exception as e:
            raise Exception(f"Failed to open image: {e}")
    else:
        meta = record_data.get("meta")
        if meta:
            pipeline = meta.get("pipeline")
            if pipeline:
                task = pipeline.get("task")
                if task is None:
                    raise Exception(
                        "Expected to find 'task' in record data's 'meta.pipeline' field."
                    )
                if task == "depth-estimation":
                    image_data = base64.b64decode(record_data["output"]["depth"])
                    img = ImagePIL.open(io.BytesIO(image_data))
                elif task == "image-segmentation":
                    img = get_complete_segmentation_image(
                        output=record_data["output"], meta=meta
                    )
                elif task == "image-to-image":
                    image_data = base64.b64decode(record_data["output"])
                    img = ImagePIL.open(io.BytesIO(image_data))
                else:
                    raise Exception(
                        f"Task '{task}' not supported for image generation."
                    )
            else:
                raise Exception(
                    "Expected to find 'pipeline' in record data's 'meta' field."
                )
        else:
            raise Exception("Expected to find 'meta' in record data.")
    return img


def normalize_disparity_image(
    image: ImagePIL.Image, min_clip=74, max_clip=2592, **kwargs
):
    pixels = np.asarray(image)
    pixels = np.clip(pixels, min_clip, max_clip)
    pixels = ((pixels - min_clip) / (max_clip - min_clip)) * 255.0
    return ImagePIL.fromarray(pixels).convert("L")


def get_record_image_ros(record_data, renormalize=True, **kwargs) -> ImagePIL.Image:
    img_modes = {
        "16UC1": "I;16",
        "mono8": "L",
        "mono16": "I;16",
        "32FC1": "F",
        "8UC1": "L",
        "8UC3": "RGB",
        "rgb8": "RGB",
        "bgr8": "RGB",
        "rgba8": "RGBA",
        "bgra8": "RGBA",
        "bayer_rggb": "L",
        "bayer_rggb8": "L",
        "bayer_gbrg": "L",
        "bayer_gbrg8": "L",
        "bayer_grbg": "L",
        "bayer_grbg8": "L",
        "bayer_bggr": "L",
        "bayer_bggr8": "L",
        "yuv422": "YCbCr",
        "yuv411": "YCbCr",
    }

    record_image_format = record_data.get("format", None)
    if record_image_format is None:
        encoding = record_data.get("encoding", None)
        if not encoding:
            return None

        mode = img_modes[encoding]
        img = ImagePIL.frombuffer(
            mode,
            (record_data["width"], record_data["height"]),
            bytes(record_data["data"]),
            "raw",
            mode,
            0,
            1,
        )
        if encoding == "bgr8":
            b, g, r = img.split()
            img = ImagePIL.merge("RGB", (r, g, b))
        elif encoding == "bgra8":
            b, g, r, a = img.split()
            img = ImagePIL.merge("RGBA", (r, g, b, a))
        elif encoding in ["mono16", "16UC1", "32FC1"] and renormalize:
            if kwargs.get("normalize_disparity"):
                img = normalize_disparity_image(img, **kwargs)
            pixels = np.asarray(img)
            pixel_max = np.max(pixels)
            pixel_range = pixel_max - np.min(pixels)
            if pixel_range == 0:
                pixels = np.zeros_like(pixels)
            else:
                pixels = ((pixels - np.min(pixels)) / pixel_range) * 255.0
            img = ImagePIL.fromarray(pixels)
            img = img.convert("L")
    else:
        if record_data["format"] == "h264":
            import av

            codec = av.CodecContext.create("h264", "r")
            packets = av.packet.Packet(bytes(record_data["data"]))
            img = codec.decode(packets)[0].to_image()
        else:
            img = ImagePIL.open(io.BytesIO(record_data["data"]))
    return img


def get_record_image_ark(record_data, renormalize=True, **kwargs) -> ImagePIL.Image:
    data = bytes(record_data["data"])
    image_format = record_data["data_format"]
    image_format_mapping = {
        42: "BayerRg10",
        44: "BayerRg12",
        43: "BayerRg16",
        41: "BayerRg8",
        31: "Bgr",
        33: "Bgra",
        51: "DepthZ16",
        21: "Grey",
        81: "H264",
        2: "Jpeg",
        1: "MotionJpeg",
        71: "Nv12",
        32: "Rgb",
        34: "Rgba",
        0: "Unset",
        27: "Uv8",
        26: "Yuv420",
        25: "Yuyv",
    }
    if image_format in image_format_mapping:
        image_format = image_format_mapping[image_format]
    else:
        raise NotImplementedError(f"Message type {image_format} not supported.")
    image_format = image_format.lower()

    if image_format == "depthz16":
        ark_img = np.frombuffer(data, dtype=np.float16)

        if renormalize:
            pixel_range = np.max(ark_img) - np.min(ark_img)
            if pixel_range != 0:
                ark_img = ((ark_img - np.min(ark_img)) / pixel_range) * 65535.0

        ark_img = ark_img.astype(np.uint16)
        data = ark_img
        image_mode = "I;16"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
        pixels = np.asarray(img)
        pixel_range = np.max(pixels) - np.min(pixels)
        if pixel_range == 0:
            pixels = np.zeros_like(pixels)
        else:
            pixels = ((pixels - np.min(pixels)) / pixel_range) * 255.0
        img = ImagePIL.fromarray(pixels)
        img = img.convert("L")
    elif image_format == "grey":
        image_mode = "L"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
    elif image_format == "rgb" or image_format == "bgr":
        image_mode = "RGB"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
        if image_format == "bgr":
            b, g, r = img.split()
            img = ImagePIL.merge("RGB", (r, g, b))
    elif image_format == "rgba" or image_format == "bgra":
        image_mode = "RGBA"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
        if image_format == "bgra":
            b, g, r, a = img.split()
            img = ImagePIL.merge("RGBA", (r, g, b, a))
    elif image_format == "jpeg":
        img = ImagePIL.open(io.BytesIO(bytes(record_data["data"])))
    else:
        if image_format == "h264":
            import av

            codec = av.CodecContext.create("h264", "r")
            packets = av.packet.Packet(record_data.data)
            img = codec.decode(packets)[0].to_image()
            # this may not work
        elif image_format.lower() == "nv12":
            width = record_data["width"]
            height = record_data["height"]
            data = record_data["data"]
            Y_size = width * height
            UV_size = (
                Y_size // 2
            )  # There are half as many UV samples as Y samples in NV12

            # Separate Y, U, and V values
            Y = np.array(data[:Y_size], dtype=np.uint8).reshape((height, width))
            UV = np.array(data[Y_size : Y_size + UV_size], dtype=np.uint8).reshape(
                (height // 2, width)
            )

            # Deinterleave U and V components
            U = UV[:, ::2]
            V = UV[:, 1::2]

            # Up-sample U and V components to match Y's dimension
            U_upsampled = np.repeat(np.repeat(U, 2, axis=0), 2, axis=1)
            V_upsampled = np.repeat(np.repeat(V, 2, axis=0), 2, axis=1)

            # Stack the YUV components together to form the YUV image
            YUV = np.stack((Y, U_upsampled, V_upsampled), axis=-1).astype(np.uint8)

            # Convert YUV to RGB
            rgb_image = ImagePIL.fromarray(YUV, "YCbCr").convert("RGB")

            # Save image as png
            img = rgb_image
        else:
            raise NotImplementedError(
                f"Message type {image_format} not supported for image conversion."
            )
    return img


def get_record_image_cutter(record_data, renormalize=True, **kwargs) -> ImagePIL.Image:
    image_format = record_data["type"]
    images_data = record_data["data"][0]
    if image_format != "JPG":
        raise NotImplementedError(
            f"Message type {image_format} not supported for image conversion."
        )
    img = ImagePIL.open(io.BytesIO(bytes(images_data)))
    return img


def get_record_image(
    record_data,
    max_size: Optional[int] = None,
    format: str = "WEBP",
    format_params: dict = {},
    renormalize: bool = True,
    resample=ImagePIL.Resampling.NEAREST,
    reset_position: bool = True,
    return_bytes: bool = False,
    **kwargs,
) -> Union[ImagePIL.Image, io.BytesIO, None]:
    if isinstance(record_data, bytes):
        img = get_record_image_lqs(
            record_data=record_data, renormalize=renormalize, **kwargs
        )
    else:
        _format = record_data.get("format", None)
        _encoding = record_data.get("encoding", None)
        _data_format = record_data.get("data_format", None)
        _image = record_data.get("image", None)
        if record_data.get("type") and record_data.get("cameras"):
            img = get_record_image_cutter(
                record_data=record_data, renormalize=renormalize, **kwargs
            )
        elif _encoding is not None:
            # ROS sensor_msgs/Image
            img = get_record_image_ros(
                record_data=record_data, renormalize=renormalize, **kwargs
            )
        elif _format is not None:
            # ROS sensor_msgs/CompressedImage
            img = get_record_image_ros(
                record_data=record_data, renormalize=renormalize, **kwargs
            )
        elif _data_format is not None:
            # ARK ark::image::Image
            img = get_record_image_ark(
                record_data=record_data, renormalize=renormalize, **kwargs
            )
        elif _image is not None:
            # ROS stereo_msgs/DisparityImage
            img = get_record_image_ros(
                record_data=_image, renormalize=renormalize, **kwargs
            )
        else:
            # we default to LQS image formats
            img = get_record_image_lqs(
                record_data=record_data, renormalize=renormalize, **kwargs
            )

    if max_size is not None:
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), resample=resample)

    if return_bytes:
        buffered_img = io.BytesIO()
        img.save(buffered_img, format=format, **format_params)
        if reset_position:
            buffered_img.seek(0)
        return buffered_img
    else:
        return img


# Point Cloud

point_cloud_type_names = [
    "sensor_msgs/PointCloud2",
    "sensor_msgs/msg/PointCloud2",
]


def jet_colormap(values, normalize=True):
    if normalize:
        values = (values - np.min(values)) / (np.max(values) - np.min(values))
    four_values = 4 * values
    red = np.minimum(four_values - 1.5, -four_values + 4.5)
    green = np.minimum(four_values - 0.5, -four_values + 3.5)
    blue = np.minimum(four_values + 0.5, -four_values + 2.5)
    colors = np.stack(
        [
            255 * np.clip(red, 0, 1),
            255 * np.clip(green, 0, 1),
            255 * np.clip(blue, 0, 1),
        ],
        axis=-1,
    )
    return colors.astype(np.uint8)


def voxel_downsample(positions, colors, max_points, voxel_size=1.0):
    # Calculate voxel indices for each point
    voxel_indices = np.floor(positions / voxel_size).astype(int)

    # Create a structured array to associate positions with their voxel
    dtype = [("x", int), ("y", int), ("z", int)]
    structured_voxel_indices = np.array(
        list(zip(voxel_indices[:, 0], voxel_indices[:, 1], voxel_indices[:, 2])),
        dtype=dtype,
    )

    # Find unique voxels and the indices of points in those voxels
    unique_voxels, inverse_indices, voxel_counts = np.unique(
        structured_voxel_indices, return_inverse=True, return_counts=True, axis=0
    )

    # Calculate sampling probabilities inversely proportional to voxel density
    sampling_probabilities = 1.0 / voxel_counts[inverse_indices]
    sampling_probabilities /= sampling_probabilities.sum()

    # Sample points based on calculated probabilities
    selected_indices = np.random.choice(
        np.arange(len(positions)),
        size=min(max_points, len(positions)),
        replace=False,
        p=sampling_probabilities,
    )

    return (
        positions[selected_indices],
        colors[selected_indices] if colors is not None else None,
    )


def process_pointcloud_record_data(
    record_data,
    max_points=None,
    random_sample=True,
    voxel_size=10.0,
    use_colormap=False,
    max_radius=None,
    force_colors=True,
    forced_color=[255, 0, 0],
    **kwargs,
):
    fields = record_data["fields"]
    valid_fields = ["x", "y", "z", "rgb", "intensity"]
    fields = [f for f in record_data["fields"] if f["name"] in valid_fields]
    if len(fields) == 0:
        if len(record_data["data"]) > 0:
            raise ValueError(
                "No fields found in point cloud data with non-zero data length."
            )
        return [], []

    assert [f["name"] for f in fields[:3]] == [
        "x",
        "y",
        "z",
    ], f"Expected fields to be ['x', 'y', 'z'], but got {fields[:3]}"

    point_cloud_data = bytes(record_data["data"])
    dtype_map = {
        1: np.int8,
        2: np.uint8,
        3: np.int16,
        4: np.uint16,
        5: np.int32,
        6: np.uint32,
        7: np.float32,
        8: np.float64,
    }
    dtype_list = []
    current_offset = 0
    for field in fields:
        field_name = field["name"]
        field_type = dtype_map[field["datatype"]]
        field_offset = field["offset"]
        # Check if there is padding needed
        if field_offset > current_offset:
            padding_size = field_offset - current_offset
            dtype_list.append(("padding" + str(current_offset), np.uint8, padding_size))
        dtype_list.append((field_name, field_type))
        current_offset = field_offset + np.dtype(field_type).itemsize

    if current_offset < record_data["point_step"]:
        padding_size = record_data["point_step"] - current_offset
        dtype_list.append(("padding" + str(current_offset), np.uint8, padding_size))

    dtype = np.dtype(dtype_list)
    all_data = np.frombuffer(point_cloud_data, dtype=dtype)

    # Access positions directly via field names, assuming the first three fields are x, y, z
    positions = np.vstack([all_data["x"], all_data["y"], all_data["z"]]).T

    colors = None
    if len(fields) > 3 and fields[3]["name"] == "rgb":
        # Extract and process RGB colors directly from the structured array
        rgb_ints = all_data["rgb"].view(
            np.uint32
        )  # Assuming 'rgb' is stored as floats and can be viewed as uint32
        red = (rgb_ints >> 16) & 255
        green = (rgb_ints >> 8) & 255
        blue = rgb_ints & 255
        colors = np.vstack([red, green, blue]).T.astype(np.uint8)
    elif len(fields) > 3 and fields[3]["name"] == "intensity":
        # Process intensity data if needed
        colors = all_data["intensity"].astype(
            np.uint8
        )  # Assuming 'intensity' directly gives the desired data
        if use_colormap:
            colors = jet_colormap(colors)
        else:
            colors = np.stack([colors] * 3, axis=-1)

    if max_radius is not None:
        indices = np.linalg.norm(positions, axis=1) < max_radius
        positions = positions[indices]
        if colors is not None:
            colors = colors[indices]

    if max_points and len(positions) > max_points:
        if random_sample:
            indices = np.random.choice(len(positions), max_points, replace=False)
            positions = positions[indices]
            if colors is not None:
                colors = colors[indices]
        else:
            positions, colors = voxel_downsample(
                positions, colors, max_points, voxel_size=voxel_size
            )

    if colors is None and force_colors:
        if use_colormap:
            colors = jet_colormap(np.linalg.norm(positions, axis=1), normalize=True)
        else:
            colors = np.full((len(positions), 3), forced_color, dtype=np.uint8)

    return positions, colors


def encode_to_draco(
    positions,
    quant_bits=11,
    compression=7,
    remove_dups=True,
    colors=None,
    max_points=None,
):
    if len(positions) == 0:
        raise ValueError("Empty positions array for encoding to Draco.")

    draco_binary = draco.encode(
        positions,
        faces=None,
        quantization_bits=quant_bits,
        compression_level=0,
        quantization_range=-1,
        quantization_origin=None,
        create_metadata=False,
        preserve_order=False,
        colors=None if remove_dups else colors,
        tex_coord=None,
    )
    if remove_dups:
        _draco_points = draco.decode(draco_binary).points
        _, unique_indices = np.unique(_draco_points, axis=0, return_index=True)
        if max_points is not None and len(unique_indices) > max_points:
            unique_indices = np.random.choice(unique_indices, max_points, replace=False)

        _draco_points = _draco_points[unique_indices]
        if colors is not None:
            colors = colors[unique_indices]

        draco_binary = draco.encode(
            _draco_points,
            faces=None,
            quantization_bits=quant_bits,
            compression_level=compression,
            quantization_range=-1,
            quantization_origin=None,
            create_metadata=False,
            preserve_order=False,
            colors=colors,
            tex_coord=None,
        )
    return draco_binary


def decode_draco(draco_binary):
    return draco.decode(draco_binary).points, draco.decode(draco_binary).colors


# MCAP


class ModifiedChunk(Chunk):
    _chunk_start_offset: int
    _chunk_length: int

    def __init__(self, **kwargs):
        self._chunk_start_offset = kwargs.pop("_chunk_start_offset")
        self._chunk_length = kwargs.pop("_chunk_length")
        super().__init__(**kwargs)

    @staticmethod
    def read(stream: ReadDataStream):
        _chunk_start_offset = stream.count
        message_start_time = stream.read8()
        message_end_time = stream.read8()
        uncompressed_size = stream.read8()
        uncompressed_crc = stream.read4()
        compression_length = stream.read4()
        compression = str(stream.read(compression_length), "utf-8")
        data_length = stream.read8()
        if compression != "zstd":
            _chunk_start_offset = stream.count
            _chunk_length = data_length
        else:
            # we need to modify the chunk_length
            _chunk_length = (stream.count - _chunk_start_offset) + data_length
        data = stream.read(data_length)
        return ModifiedChunk(
            compression=compression,
            data=data,
            message_end_time=message_end_time,
            message_start_time=message_start_time,
            uncompressed_crc=uncompressed_crc,
            uncompressed_size=uncompressed_size,
            _chunk_start_offset=_chunk_start_offset,
            _chunk_length=_chunk_length,
        )

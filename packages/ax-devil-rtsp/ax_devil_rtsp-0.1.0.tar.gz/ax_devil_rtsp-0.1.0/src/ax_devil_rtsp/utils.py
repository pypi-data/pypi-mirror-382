import xml.etree.ElementTree as ET
import re
from typing import Dict, Any
import urllib.parse

from .logging import get_logger

logger = get_logger("utils")


def parse_axis_scene_metadata_xml(xml_data: bytes) -> dict:
    """
    Parse ONVIF Scene metadata XML and extract relevant information.

    Args:
        xml_data: Raw XML bytes data

    Returns:
        dict: Parsed Scene metadata information
    """
    try:
        try:
            xml_text = xml_data.decode('utf-8')
        except UnicodeDecodeError:
            xml_text = xml_data.decode('utf-8', errors='ignore')

        root = ET.fromstring(xml_text)
        result: Dict[str, Any] = {
            'objects': [],
            'utc_time': None,
            'raw_xml': xml_text
        }

        ns = {
            "tt": "http://www.onvif.org/ver10/schema",
            "bd": "http://www.onvif.org/ver20/analytics/humanbody"
        }

        # Extract objects
        for obj in root.findall('.//tt:Object', ns):
            obj_id = obj.get('ObjectId')
            type_elem = obj.find('.//tt:Type', ns)
            if type_elem is not None:
                result['objects'].append({
                    'id': obj_id,
                    'type': type_elem.text
                })

        # Extract frame time
        for frame in root.findall('.//tt:Frame', ns):
            utc_time = frame.get('UtcTime')
            if utc_time:
                result['utc_time'] = utc_time
                break

        return result

    except ET.ParseError as e:
        logger.error("XML Parse Error: %s", e)
        return {
            'objects': [],
            'utc_time': None,
            'raw_xml': xml_text
        }


def _parse_caps_string(caps_str: str) -> Dict[str, Any]:
    """
    Parse a GStreamer caps/structure string of the form:
      "video/x-raw,format=(string)RGB,width=(int)640,framerate=(fraction)30/1"
    into a dict: {"format": "RGB", "width": 640, "framerate": "30/1", ...}.
    Respects GStreamer’s escape for commas (\\,).
    """
    # Split on commas not preceded by a backslash
    # negative lookbehind :contentReference[oaicite:1]{index=1}
    parts = re.split(r'(?<!\\),\s*', caps_str)
    result: Dict[str, Any] = {}
    for part in parts:
        # Match key=(type)value
        m = re.match(r'([^=]+)=\(([^)]+)\)(.*)', part)
        if not m:
            continue
        key, type_, raw_val = m.groups()
        # Unescape any '\,' back to ','
        val = raw_val.strip().strip('"').replace(r'\,', ',')
        # Convert to native type
        if type_ in ("int", "uint", "guint", "gint"):
            result[key] = int(val)
        elif type_ in ("double", "float"):
            result[key] = float(val)
        elif type_ == "boolean":
            result[key] = val.lower() == "true"
        else:
            # string, fraction, guint64, etc. kept as string
            result[key] = val
    return result


def parse_session_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given raw metadata as delivered by VideoGStreamerClient:
      {
        "stream_name": "...",
        "caps": "...",
        "structure": "...",
        "sdes": { ... }           # optional
      }
    returns a dict with:
      - stream_name (str)
      - caps (raw string)
      - caps_parsed (Dict[str,Any])
      - structure (raw string)
      - structure_parsed (Dict[str,Any])
      - sdes (if present, copied through)
    """
    parsed: Dict[str, Any] = {}
    # Copy over the simple field
    parsed["stream_name"] = raw.get("stream_name")

    # Parse both caps and structure
    for field in ("caps", "structure"):
        text = raw.get(field)
        if isinstance(text, str):
            parsed[field] = text
            parsed[f"{field}_parsed"] = _parse_caps_string(text)

    # Pass through SDES if present
    if "sdes" in raw:
        parsed["sdes"] = raw["sdes"]
    return parsed


def build_axis_rtsp_url(
    ip: str,
    username: str,
    password: str,
    video_source: int,
    get_video_data: bool,
    get_application_data: bool,
    rtp_ext: bool,
    resolution: str = None,  # Will let the device decide what the resolution should be
) -> str:
    """
    Build an RTSP URL for Axis cameras.
    """
    if not ip:
        raise ValueError("No IP address provided.")
    if not get_video_data and not get_application_data:
        raise ValueError(
            "At least one of get_video_data or get_application_data must be True.")
    cred = f"{username}:{password}@" if username or password else ""
    url = f"rtsp://{cred}{ip}/axis-media/media.amp"
    params = {}
    if not get_video_data:
        params["video"] = "0"
        params["audio"] = "0"
    if rtp_ext:
        params["onvifreplayext"] = "1"
    if get_video_data and resolution is not None:
        params["resolution"] = resolution
    if get_application_data:
        params["analytics"] = "polygon"
    params["camera"] = str(video_source)
    if params:
        query_string = urllib.parse.urlencode(params)
        url += "?" + query_string
    return url

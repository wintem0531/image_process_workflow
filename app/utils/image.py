"""图像工具函数"""
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from typing import Optional


def image_to_base64(image: np.ndarray, format: str = "JPEG", quality: int = 85) -> str:
    """
    将numpy图像转换为Base64字符串

    Args:
        image: numpy图像数组
        format: 图像格式（JPEG/PNG）
        quality: JPEG质量（1-100）

    Returns:
        Base64字符串
    """
    if image is None:
        return ""

    # 确保是BGR格式（OpenCV默认）
    if len(image.shape) == 2:
        # 灰度图转RGB
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif len(image.shape) == 3 and image.shape[2] == 3:
        # BGR转RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 转换为PIL Image
    pil_image = Image.fromarray(image)

    # 转换为Base64
    buffer = BytesIO()
    pil_image.save(buffer, format=format, quality=quality)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{format.lower()};base64,{img_str}"


def image_to_thumbnail(image: np.ndarray, max_size: int = 200) -> str:
    """
    生成缩略图Base64

    Args:
        image: numpy图像数组
        max_size: 最大尺寸

    Returns:
        缩略图Base64字符串
    """
    if image is None:
        return ""

    h, w = image.shape[:2]
    if h > max_size or w > max_size:
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        thumbnail = cv2.resize(image, (new_w, new_h))
    else:
        thumbnail = image

    return image_to_base64(thumbnail, format="JPEG", quality=70)


def base64_to_image(base64_str: str) -> Optional[np.ndarray]:
    """
    将Base64字符串转换为numpy图像

    Args:
        base64_str: Base64字符串（可包含data URI前缀）

    Returns:
        numpy图像数组
    """
    if not base64_str:
        return None

    # 移除data URI前缀
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]

    # 解码
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


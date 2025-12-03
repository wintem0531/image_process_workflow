"""文件上传路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import shutil

router = APIRouter()

os.makedirs("uploads", exist_ok=True)


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    # 生成唯一ID
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    file_path = os.path.join("uploads", f"{file_id}{file_ext}")

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "path": f"/uploads/{file_id}{file_ext}",
        "size": os.path.getsize(file_path),
    }


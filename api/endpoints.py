from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import base64
from core.segmenter import Segmenter
import traceback

router = APIRouter()


@router.post("/segment")
async def segment(file: UploadFile = File(...)):
    # Validate input
    if not file.filename.endswith(('.nii.gz')):
        raise HTTPException(status_code=400, detail="Invalid file format")

    try:
        segmenter = Segmenter(file)
        img, filename, minima = segmenter.run_segmentation()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    response_data = {
        "filename": img,
        "file": file_to_base64(filename),
        "minima": minima,
        # "volume": ,  # Todo
        # "preview_img":  # Todo
    }
    return JSONResponse(content=response_data)


def file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

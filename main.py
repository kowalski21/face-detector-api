import os
from typing import Union
from fastapi import FastAPI
from typing import Annotated
from deepface import DeepFace
from deepface.modules import verification
from fastapi import FastAPI, File, UploadFile, HTTPException, status
import shutil
from tempfile import NamedTemporaryFile
from fastapi.middleware.cors import CORSMiddleware


def save_file_to_temp(upload_file: UploadFile) -> str:
    try:
        with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            shutil.copyfileobj(upload_file.file, temp_file)
            return temp_file.name
    except Exception as e:
        raise RuntimeError(f"Failed to save file: {str(e)}")


def remove_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Failed to remove file: {str(e)}")


app = FastAPI()

# Add CORS middleware with more specific configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/home")
def home_route():
    return {"home": "welcome"}


@app.post("/face/verify")
def verify_face(main_face: UploadFile, other_face: UploadFile):
    main_face_path = ""
    other_face_path = ""
    try:
        # Save the uploaded files to the filesystem
        main_face_path = save_file_to_temp(main_face)
        other_face_path = save_file_to_temp(other_face)

        # Verify the faces using the saved file paths
        result = verification.verify(
            main_face_path, other_face_path, enforce_detection=False
        )
        return {"verified": result["verified"], "status": "success"}
        # print(result)

    except Exception as e:
        print(e)
        # return {"verified": False, "status": "failed"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )

    finally:
        # Remove the temporary files
        remove_file(main_face_path)
        remove_file(other_face_path)

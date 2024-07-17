import os
from fastapi import FastAPI, File, UploadFile, Header
from fastapi.staticfiles import StaticFiles
from wordtoxml import convert
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.mount("/html", StaticFiles(directory="output", html = True), name="HTML OUTPUT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        file_location = os.path.join("input", file.filename)
        with open(file_location, 'wb') as f:
            f.write(contents)
        res = convert(file.filename)
        with open(os.path.join("output", res), 'r') as f:
            return {"xml": f.read()}
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return f"{origin}/html/{res}"

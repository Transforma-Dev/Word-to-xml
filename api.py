import traceback
import os
from fastapi import FastAPI, File, UploadFile, Header
from fastapi.staticfiles import StaticFiles
from wordtoxml import convert
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.mount("/image", StaticFiles(directory="image", html = True), name="images")

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
        client_name = "TSP"
        res = convert(file.filename, client_name)
        with open(os.path.join("output", res), 'r') as f:
            return {"xml": f.read()}
    except Exception as e:
        print(traceback.format_exc())
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return f"{origin}/html/{res}"

@app.get("/get/{fileId}")
def read_root(fileId: str):
    fPath = os.path.join("output", f'{fileId}.xml')
    if os.path.exists(fPath):
        with open(fPath, 'r') as f:
            return {"xml": f.read()}
    else:
        return {"message": "File not exists"}

@app.get("/get")
def read_root():
    all_files = os.listdir("output")
    out = []
    for f in all_files:
        if f.endswith(".xml"):
            out.append(f.replace(".xml", ""))
    return {"files": out}
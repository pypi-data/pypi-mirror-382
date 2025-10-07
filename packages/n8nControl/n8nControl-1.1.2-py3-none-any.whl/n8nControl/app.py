from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
from dotenv import load_dotenv
from n8nControl.n8nManagement import N8nManagement

load_dotenv()
app = FastAPI()
n8n = N8nManagement()

@app.post('/import-workflow')
async def import_workflow(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file part")
        if file.filename == '':
            raise HTTPException(status_code=400, detail="No selected file")

        save_path = f"/root/{file.filename}"
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        result = n8n.import_workflow(save_path)
        return JSONResponse(result.__dict__)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get('/export-workflow')
def export_workflow_route():
    try:
        result = n8n.export_workflow()
        return FileResponse(
            path=result["filePath"],
            filename=result["filename"],
            media_type='application/json'
        )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)}, status_code=500
        )

def main():
    print("N8nManagement initialized")
    port = int(os.getenv("PORT", 9000))
    uvicorn.run("n8nControl.app:app", host="localhost", port=port, reload=False)

# Cho phép chạy trực tiếp bằng python app.py
if __name__ == "__main__":
    main()
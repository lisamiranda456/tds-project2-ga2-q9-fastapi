import os
import csv
import base64
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GITHUB_CSV_URL = "https://api.github.com/repos/danielrayappa2210/TDS-Project-2---datastore/contents/q-fastapi.csv"

app = FastAPI()

@app.get("/api")
async def get_students(class_id: list[str] = Query(None, alias="class")):
    headers = {}
    if ACCESS_TOKEN:
        headers["Authorization"] = f"token {ACCESS_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(GITHUB_CSV_URL, headers=headers)
    
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching CSV from GitHub")
    
    content = resp.json().get("content")
    if not content:
        raise HTTPException(status_code=500, detail="No content found in GitHub response")

    try:
        decoded = base64.b64decode(content).decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)
        students = [
            {"studentId": int(row["studentId"]), "class": row["class"].strip()}
            for row in reader if row["studentId"].isdigit()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if class_id is None:
        return {"students": students}

    filtered_students = [
        student for student in students if student["class"].lower() in [c.lower() for c in class_id]
    ]

    if not filtered_students:
        raise HTTPException(status_code=404, detail="No students found for the provided classes")

    response = JSONResponse(content={"students": filtered_students})
    response.headers.update({
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
    
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

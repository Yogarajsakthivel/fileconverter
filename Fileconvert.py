from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pypandoc
from io import BytesIO
import pandas as pd
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
origins = [
    "http://localhost:3000",  # Add your frontend origin here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_image(input_image: BytesIO, target_format: str) -> BytesIO:
    try:
        image = Image.open(input_image)

        # Convert RGBA to RGB if the image mode is RGBA
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        output_image = BytesIO()
        image.save(output_image, format=target_format)
        output_image.seek(0)
        return output_image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_to_pdf(input_file: BytesIO) -> BytesIO:
    try:
        document = Document(input_file)
        output_pdf = BytesIO()
        c = canvas.Canvas(output_pdf, pagesize=letter)
        for paragraph in document.paragraphs:
            text = paragraph.text
            c.drawString(100, 750, text)
        c.save()
        output_pdf.seek(0)
        return output_pdf
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_to_docx(input_file: BytesIO, output_format: str) -> BytesIO:
    try:
        input_content = input_file.read().decode('utf-8')
        output_file = BytesIO()
        pypandoc.convert_text(input_content, output_format, format='md', outputfile=output_file)
        output_file.seek(0)
        return output_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_to_csv(input_file: BytesIO) -> BytesIO:
    try:
        df = pd.read_excel(input_file)
        output_csv = BytesIO()
        df.to_csv(output_csv, index=False)
        output_csv.seek(0)
        return output_csv
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_to_xls(input_file: BytesIO) -> BytesIO:
    try:
        df = pd.read_csv(input_file)
        output_xls = BytesIO()
        with pd.ExcelWriter(output_xls, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output_xls.seek(0)
        return output_xls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-jpg/")
async def convert_to_jpg(file: UploadFile = File(...)):
    try:
        input_image = BytesIO(await file.read())
        converted_image = convert_image(input_image, "JPEG")

        return Response(content=converted_image.getvalue(), media_type="image/jpeg", headers={"Content-Disposition": "attachment;filename=converted.jpg"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-png/")
async def convert_to_png(file: UploadFile = File(...)):
    try:
        input_image = BytesIO(await file.read())
        converted_image = convert_image(input_image, "PNG")

        return Response(content=converted_image.getvalue(), media_type="image/png", headers={"Content-Disposition": "attachment;filename=converted.png"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-pdf/")
async def convert_to_pdf_endpoint(file: UploadFile = File(...)):
    try:
        input_file = BytesIO(await file.read())
        converted_pdf = convert_to_pdf(input_file)

        return Response(content=converted_pdf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=converted.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-docx/")
async def convert_to_docx_endpoint(file: UploadFile = File(...)):
    try:
        input_file = BytesIO(await file.read())
        converted_docx = convert_to_docx(input_file, "docx")

        return Response(content=converted_docx.getvalue(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": "attachment;filename=converted.docx"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-csv/")
async def convert_to_csv_endpoint(file: UploadFile = File(...)):
    try:
        input_file = BytesIO(await file.read())
        converted_csv = convert_to_csv(input_file)

        return Response(content=converted_csv.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment;filename=converted.csv"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-xls/")
async def convert_to_xls_endpoint(file: UploadFile = File(...)):
    try:
        input_file = BytesIO(await file.read())
        converted_xls = convert_to_xls(input_file)

        return Response(content=converted_xls.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment;filename=converted.xlsx"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
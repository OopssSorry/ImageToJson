class Config:
    secret      = None          # str | None    - default: None
    debug       = False         # bool          - default: False
    min_width   = 8            # int           - default: 8
    min_height  = 8            # int           - default: 8
    max_width   = 400           # int           - default: 800
    max_height  = 400           # int           - default: 800
    

# Start
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from PIL import Image
from io import BytesIO
import requests
import uvicorn
import math

app = FastAPI(docs_url="/",title="ImageToJson",description="Me: https://fbi.bio/oopss_sorry",openapi_url="/openapi",redoc_url="/redoc",swagger_ui_oauth2_redirect_url="/oauth2",version="beta:gay:2")

def verify_secret(secret: str = None):
    if Config.secret==None or secret == Config.secret:
        return True
    return False

def process_image(image, width, height):
    # Resize the image
    image_resized = image.resize([width, height])

    # Prepare the output data structure
    image_data = {}
    for y in range(image_resized.height):
        row_data = {}
        for x in range(image_resized.width):
            pixel = image_resized.getpixel([x, y])
            rgb = None
            if isinstance(pixel, int):
                rgb = (pixel, pixel, pixel)
            else:
                rgb = pixel
            hex_color = "{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
            row_data[x] = str(hex_color)
        image_data[height-y] = row_data


@app.get("/status")
async def status():
    return PlainTextResponse("success")

@app.get("/process-url")
async def process_url(
    source: str = Query(..., description="URL of the image to process", max_length=128),
    width: int = Query(..., description="Desired width of the image",ge=Config.min_width or 8, le=Config.max_width or 800),
    height: int = Query(..., description="Desired height of the image",ge=Config.min_height or 8, le=Config.max_height or 800),
    secret: str = Query(None, description="Secret key"),
):
    # Check secret
    if not verify_secret(secret=secret):
        return HTTPException(status_code=401, detail="Unauthorized access")
    try:
        # Fetch the image from the URL
        response = requests.get(source)
        response.raise_for_status()
        
        # Open image from url
        image = Image.open(BytesIO(response.content))
        image_data = process_image(image)
        
        return JSONResponse(image_data,status_code=200)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return HTTPException(status_code=400, detail="Error fetching image")
    except Exception as e:
        print(f"Error fetching image: {e}")
        return HTTPException(status_code=500, detail="Error processing image")

@app.get("/process-file")
async def process_file(
    file: UploadFile = File(None),
    width: int = Query(..., description="Desired width of the image",ge=Config.min_width or 8, le=Config.max_width or 800),
    height: int = Query(..., description="Desired height of the image",ge=Config.min_height or 8, le=Config.max_height or 800),
    secret: str = Query(None, description="Secret key"),
):
    # Check secret
    if not verify_secret(secret=secret):
        return HTTPException(status_code=401, detail="Unauthorized access")
    try:
        # Open the uploaded image
        image = Image.open(file.file)
        image_data = process_image(image)
        
        return JSONResponse(image_data,status_code=200)
    except Exception as e:
        print(f"Error fetching image: {e}")
        return HTTPException(status_code=500, detail="Error processing image")

if __name__ == "__main__":
    print("Server enabled!")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=(Config.debug==True and "debug") or "critical")
class Config:
    secret      = None          # str | None    - default: None
    debug       = True         # bool          - default: True
    min_width   = 24            # int           - default: 24
    min_height  = 24            # int           - default: 24
    max_width   = 576           # int           - default: 576
    max_height  = 576           # int           - default: 576
    

# Start
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from PIL import Image
from io import BytesIO
import requests
import uvicorn

app = FastAPI(docs_url="/",title="ImageToJson",description="Me: https://fbi.bio/oopss_sorry",openapi_url="/openapi",redoc_url="/redoc",swagger_ui_oauth2_redirect_url="/oauth2",version="beta:gay:1")

def verify_secret(secret: str = None):
    if Config.secret==None or secret == Config.secret:
        return True
    return False

@app.get("/status")
async def status():
    return PlainTextResponse("success")

@app.get("/process-image")
async def process_image(
    source: str = Query(..., description="URL of the image to process", max_length=128),
    width: int = Query(..., description="Desired width of the image",ge=Config.min_width or 24, le=Config.max_width or 576),
    height: int = Query(..., description="Desired height of the image",ge=Config.min_height or 24, le=Config.max_height or 576),
    secret: str = None
):
    # Check secret
    if not verify_secret(secret=secret):
        return HTTPException(status_code=401, detail="Unauthorized access")
    try:
        # Fetch the image from the URL
        response = requests.get(source)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

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

        return JSONResponse(image_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return HTTPException(status_code=400, detail="Error fetching image")
    except Exception as e:
        print(f"Error fetching image: {e}")
        return HTTPException(status_code=500, detail="Error processing image")

if __name__ == "__main__":
    print("Server enabled!")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=(Config.debug==True and "debug") or "critical")

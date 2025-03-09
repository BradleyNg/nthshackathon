GEMINI_API_KEY = ""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import vertexai
from vertexai.preview.vision_models import Image, ImageCaptioningModel, ImageQnAModel
import google.generativeai as genai
import uvicorn
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from serpapi import GoogleSearch

PROJECT_ID = ""  
LOCATION = ""  

textThing = ""

vertexai.init(project=PROJECT_ID, location=LOCATION)
image_captioning_model = ImageCaptioningModel.from_pretrained("imagetext@001")
image_qna_model = ImageQnAModel.from_pretrained("imagetext@001")

genai.configure(api_key=GEMINI_API_KEY)

def gemini_ask_question(image_path, question, context=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        
        input_data = [question, {"mime_type": "image/jpeg", "data": image_bytes}]
        if context:
            input_data.insert(0, context)
        
        response = model.generate_content(input_data)
        return response.text if response and hasattr(response, "text") else "No valid response from Gemini"
    except Exception as e:
        return f"Gemini API error: {str(e)}"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

@app.post("/caption_image")
async def caption_image(file: UploadFile = File(...)):
    global textThing
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    
    image = Image.load_from_file(file_location)
    
    captions = image_captioning_model.get_captions(image=image)
    
    # Define questions for QA
    questions = [
        "What model of device is shown in the image to be broken? Give the exact model of the device and walk through the reasons why it is this model.",
        "What part(s) seem to be broken with this device? Explain why the part seems to be broken and what indications gave it away."
    ]
    
    qa_responses = []
    gemini_responses = []
    
    for question in questions:
        response = image_qna_model.ask_question(image=image, question=question, number_of_results=1)
        qa_responses.append({"question": question, "answers": response})
        
        gemini_answer = gemini_ask_question(file_location, question)
        gemini_responses.append({"question": question, "answers": gemini_answer})
    
    # Generate repair and maintenance advice based on gathered responses
    advice_question = "Based on the following information, provide advice on how to fix the problem and tips for maintaining the device:"
    context_data = json.dumps({"captions": captions, "qa_responses": qa_responses, "gemini_responses": gemini_responses})
    advice_response = gemini_ask_question(file_location, advice_question, context=context_data)
    
    # Generate a list of replacement parts
    parts_question = "Based on the following information, provide a list of necessary replacement parts for repair. (no explanation or anything required just the replacement part itself)"
    parts_response = gemini_ask_question(file_location, parts_question, context_data)
    
    os.remove(file_location)
    print({
        "captions": captions,
        "qa_responses": qa_responses,
        "gemini_responses": gemini_responses,
        "advice": advice_response,
        "replacement_parts": parts_response
    })

    textThing = str(parts_response)
    print(textThing)
    return {
        "captions": captions,
        "qa_responses": qa_responses,
        "gemini_responses": gemini_responses,
        "advice": advice_response,
        "replacement_parts": parts_response
    }

@app.get("/thing/")
async def thing():
    return textThing


@app.get("/amazon/")
async def amazonQuerier(keyword :str):

    params = {
    "engine": "google_shopping",
    "q": keyword,
    "api_key": ""
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    return results["shopping_results"]

    # elements = []
    # # Set up the WebDriver (Make sure to specify the path to your chromedriver if necessary)
    # driver = webdriver.Chrome()

    # # Open Amazon search results page
    # search_query = "laptop"  # Change this to any search term
    # url = f"https://www.amazon.com/s?k={search_query}"
    # driver.get(url)
    # time.sleep(3)
    # divs = driver.find_elements(By.XPATH, "//div[@class='puisg-row']")
    # if divs == None:
    #     print("No DIVS found")
    #     return
    # else:
    #     for idx, div in enumerate(divs):
    #         data = {}
    #         content = div.find_element(By.CLASS_NAME,"puis-list-col-right")
    #         if content == None:
    #             print("No Content found continueing...")
    #             continue
    #         title = content.find_element(By.CSS_SELECTOR,"h2")
    #         if title == None:
    #             print("No title found continueing..")
    #             continue
    #         stars = content.find_element(By.CLASS_NAME,"a-icon-alt")
    #         if stars == None:
    #             print("No stars found continueing..")
    #             continue
    #         price = content.find_element(By.CSS_SELECTOR,"span.a-offscreen")
    #         if price == None:
    #             print("No price found continueing..")
    #             continue
    #         image = div.find_element(By.CSS_SELECTOR,"img")
    #         if image == None:
    #             print("No image found continuing...")
    #             continue
    #         data["title"] = title.get_attribute("text")
    #         data["stars"] = stars.get_attribute("text")
    #         data["price"] = price.get_attribute("text")
    #         data["thumbnailImage"] = image.get_attribute("src")
    #         data["keyword"] = keyword
    #         elements.append(data)

    # driver.quit()

    # elements = []
    # # url = requests.get("https://www.amazon.com/s?k=iphone+15+battery")
    # # soup = BeautifulSoup(url.content, 'html.parser')
    # # divs = soup.findAll(class_="puisg-row")
    # if divs == None:
    #     print("No DIVS found")
    #     return
    # else:
    #     for div in divs:
    #         data = {}
    #         content = div.find(class_="puis-list-col-right")
    #         if content == None:
    #             print("No Content found continueing...")
    #             continue
    #         title = content.find("h2")
    #         if title == None:
    #             print("No title found continueing..")
    #             continue
    #         stars = content.find(class_="a-icon-alt")
    #         if stars == None:
    #             print("No stars found continueing..")
    #             continue
    #         price = content.find("span",class_=".a-offscreen")
    #         if price == None:
    #             print("No price found continueing..")
    #             continue
    #         image = div.find("img")
    #         if image == None:
    #             print("No image found continuing...")
    #             continue
    #         data["title"] = title.text
    #         data["stars"] = stars.text
    #         data["price"] = price.text
    #         data["thumbnailImage"] = image["src"]
    #         data["keyword"] = keyword
    #         elements.append(data)
    #     return elements

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

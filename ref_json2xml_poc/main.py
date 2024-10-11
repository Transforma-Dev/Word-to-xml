# from googleapi import google
# num_page = 3
import re
import time
import requests
import json
import google.generativeai as genai
from pydantic import BaseModel     #AIzaSyCHmvQi4G7jWTWy6ojYCt67lIxPt36w-Mo
genai.configure(api_key="AIzaSyDwVIc-eIlO-AJyuhxz8Pgl3TFMyBGokDw")
from fastapi import FastAPI
from typing import List, Union
from threading import Thread, Lock
from queue import Queue
import time
import random
import calendar
import index

# def TSP_ref(id, xml_text, style):
app = FastAPI()
DEBUG = True

def debug(message):
    if DEBUG:
        print(message)

def doi_metadata_api(doi_url):
    # print(doi_url)
    try:
        url = doi_url
        headers = {
            # "Accept": "application/json"
            "Accept": "application/vnd.citationstyles.csl+json"
        }

        response = requests.get(url, headers=headers, timeout=10)
        print(response)
        if response.status_code == 200:
            metadata = json.loads(response.text)
            metadata["user_doi"] = doi_url
            return metadata
        else:
            print(f"Error retrieving DOI metadata for DOI {doi_url}: {response.status_code}")
            return None
    except Exception as e:
        print(e)
        return False

def clean_up_doi(doi):
    doi = doi.strip().lower()
    if doi.endswith(".") or doi.endswith(","):
        doi = doi[:-1]
    if "doi:" in doi:
        doi = doi.replace("doi:", "")
    if "org:" in doi:
        doi = doi.replace("org:", "org/")
    if not doi.startswith("doi.org") and not doi.startswith("http"):
        doi = "doi.org/"+doi
    if doi.startswith("doi.org"):
        doi = "https://"+doi
    return doi

def find_doi_in_reference(reference):
    words = reference.split(" ")
    ref = None
    for word in words:
        if "doi" in word.lower() and len(word) > 5:
            ref = word
        elif re.match("\d{2}\.\d{3,}\/", word):
            ref = word
    if ref != None:
        return clean_up_doi(word)
    return False

def ask_google(reference):
    for i in range(3):
        try:
            generation_config=genai.types.GenerationConfig(temperature=0)
            model = genai.GenerativeModel('gemini-pro', generation_config=generation_config)
            prompt = f"""Parse the below references text in detailed csl-JSON format and also search for DOI in google and add key "doi_url" in the result wherever applicable and give result in JSON Format.
            {reference}
            """
            response = model.generate_content(prompt)
            response = response.text.replace('```JSON', '')
            return json.loads(response.replace('`', ''))
        except Exception as e:
            print(e)
            print(response.text) if response else ''
            continue
    return False

def ask_crossref(reference):
    error_email = "vapt@transforma.in"
    url = f"https://api.crossref.org/works?filter=has-full-text:true&mailto={error_email}&query={reference}&select=DOI,score&rows=1&sort=score"
    response = requests.get(url)
    if response.status_code == 200:
        metadata = json.loads(response.text)
        if metadata["message"]["items"][0]["score"] > 100:
            return "http://doi.org/" + metadata["message"]["items"][0]["DOI"]
    return False

def ask_duckduckgo(reference):
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        for r in ddgs.text(f"{reference}", region='in-en', safesearch='off', max_results=3, backend='html'):
            print(r)

def get_doi_metadata(reference):
    doi_in_reference = find_doi_in_reference(reference)
    if doi_in_reference:
        debug("DOI Found in Reference")
        return doi_metadata_api(doi_in_reference)
    cross_ref = ask_crossref(reference)
    if cross_ref:
        debug("DOI Found in Crossref")
        return doi_metadata_api(cross_ref)
    return False

# r = get_doi_metadata("https://dx.doi.org/10.3389/fpsyg.2017.01578")
# print(json.dumps(r))
class Reference(BaseModel):
    id: str
    reference: str
    style: str

class Item(BaseModel):
    references: List[Reference]

# Define the worker function for threads
def worker(work_queue, lock, output_queue):
    while True:
        # Acquire lock before accessing the queue
        lock.acquire()
        if not work_queue or len(work_queue) == 0:
            # Queue is empty, break the loop
            lock.release()
            break
        # print(type(work_queue))
        # Get the next work item from the queue
        work_item = work_queue.pop(0)
        lock.release()
        # Do the work and capture the output
        output = process_reference(work_item)
        # Place the output in the output queue
        output_queue.put(output)

def process_reference(reference):
    res = {"id": reference.id}
    doi_metadata = get_doi_metadata(reference.reference)
    if doi_metadata:
        res["doi_metadata"] = doi_metadata
    else:
        debug("DOI Found in Google")
        parsed = ask_google(reference.reference)
        res["parsed"] = parsed
        res["doi_metadata"] = False
        # res["style"] = reference["style"]
    return res

def process_requests(references):

    # Create a shared lock, work queue, and a queue to store outputs
    lock = Lock()
    work_queue = references
    output_queue = Queue()

    # Define the number of threads
    num_threads = 4

    # Create and start worker threads
    threads = []
    for i in range(num_threads):
        thread = Thread(target=worker, args=(work_queue, lock, output_queue))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Print the collected results from the output queue
    # print("All work completed. Results:")
    output = []
    while not output_queue.empty():
        output.append(output_queue.get())
    return output

def preprocess(res):
    
    if not res:
        return ""
    doi = res[0]["doi_metadata"]

    if doi:
        ref = res[0]["doi_metadata"]
    else:
        ref = res[0]["parsed"]

    page_value = ref.get("page") or ref.get("first-page")
    # print(page_value)
    #Separate the page number and add first, last tag
    if page_value:
        if "-" in page_value:
            split_page = ref["page"].split("-")
            ref["fpage"] = split_page[0]
            ref["lpage"] = split_page[1]
        else:
            ref["fpage"] = page_value

    try:
        #Change the dates
        issued = (ref["issued"])
    except:
        issued = ""
    # print(issued)
    if issued:
        for d_name in issued:
            if d_name=="date-parts":
                date = issued[d_name][0]
            else:
                date = []
                date.append(issued[d_name])
        # print(date,"---")
        # print(len(date))    
        if len(date)>1:
            dates = calendar.month_name[date[1]]
            da = str(date[0]) + " ," + dates[:3] + "."
            
            ref["dates"] = str(da)
        elif date:
            # print(date)
            ref["dates"] = date[0]
    # print(res[0]["doi_metadata"]["dates"])

    return index.Add_tag(res, "ieee")

@app.post("/")
def read_root(inp: Item):
    # print(inp)
    return preprocess(process_requests(inp.references))
    
# Testing....
# references = open("References copy.txt", "r").readlines() #[xml_text] 
# # print(references)
# # print(type(references))
# inp = []
# for reference in references:
#     inp.append({"id": id, "reference": reference})

# # print(inp)
# res = process_requests(inp)
# print(res)

# return preprocess(res)
    
    # process_requests({"references": inp})
    # doi_metadata_api("https://doi.org/10.1016/j.apenergy.2016.01.070")


# TSP_ref("1", "Fontana, R. J. (2008). Acute liver failure including acetaminophen overdose. The Medical Clinics of North America, 92(4), 761�794. doi:10.1016/j.mcna.2008.03.005", "ieee")
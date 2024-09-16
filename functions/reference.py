import re 
import calendar
import requests


#Define function to find reference part
def reference(xml_text,variables):
    
    xml_text=xml_text.replace("<bold>","").replace("</bold>","")
    #Chect "back" is already present in variable or not to open the back tag
    if "back" not in variables["back_start"]:
        if variables["sec_3"]>1:
            text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        elif variables["sec_2"]>1:
            text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        else:
            text=f'</sec></body><back><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        variables["ref"]=True
    elif "fn" in variables["back_start"]:   #fn is already is there then not anames back tag
        text=f'</p></fn></fn-group><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
    else:
        if variables["sec_3"]>1:
            text=f'</sec></sec><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        elif variables["sec_2"]>1:
            text=f'</sec></sec><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        elif variables["sec_1"]>1:
            text=f'</sec><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        else:
            text=f'<ref-list content-type="authoryear"><title1>{xml_text}</title1>'

    variables["fn_start"]=False
    variables["ref"]=True
    #print(text)
    return text

def reference_text(xml_text,variables):
    
    text =''
    
    #Example usage:
    references_data = {
        "references": [
            {
                "id": f'{variables["ref_id"]}',
                "reference": f"{xml_text}"
            }
        ]
    }

    api_endpoint = 'http://10.10.10.41:3333/'  #API url endpoint
    
    try:
        #Sending a POST request to the API endpoint with JSON data
        response = requests.post(api_endpoint, json=references_data)
        
        #Checking if the request was successful (status code 200)
        if response.status_code == 200:
            references_json = response.json()  #Assuming the response is JSON
        else:
            print({'error': f'API Error: {response.status_code}'})
    
    except requests.exceptions.RequestException as e:
        print({'error': f'Request Exception: {str(e)}'})
    
    # xml_text = re.sub(r'^\[\d+\]', '', xml_text)
    print(references_json)
    if references_json and not xml_text.isspace():
        
            data = references_json[0]
            print(data)
            ref_word = ''

            ref_word += f'<label>{data["id"]}</label><mixed-citation publication-type="journal">'

            tag_list = ["author","title","container-title","volume","issue","page","year","issued","DOI","doi_url","publisher"]

            #Loop through the tag order
            for k in tag_list:
                #Loop through parsed text in json
                for j in data["parsed"]:
                    #Find author name
                    if j==k=="author":
                        ref_word += f'<person-group person-group-type="author">'
                        for i in data["parsed"]["author"]:
                            if len(i)>1:
                                ref_word += f'<string-name><surname>{i["family"]}</surname><given-names>{i["given"]}</given-names></string-name>'
                            else:
                                ref_word += f'<string-name><surname>{i["family"]}</surname></string-name>'
                        ref_word += f'</person-group>'
                    #Find article title
                    elif j==k=="title":
                        ref_word += f'<article-title>{data["parsed"]["title"]}</article-title>'
                    #Find source
                    elif j==k=="container-title":
                        ref_word += f'<source>{data["parsed"]["container-title"]}</source>'
                    #Find Volume
                    elif j==k=="volume":
                        ref_word += f'<volume>{data["parsed"]["volume"]}</volume>'
                    #Find issue
                    elif j==k=="issue":
                        ref_word += f'<issue>{data["parsed"]["issue"]}</issue>'
                    #Find page number
                    elif j==k=="page":
                        if "-" in data["parsed"]["page"]:
                            split_page = data["parsed"]["page"].split("-")
                            ref_word += f'<fpage>{split_page[0]}</fpage><lpage>{split_page[1]}</lpage>'
                        else:
                            ref_word += f'<fpage>{data["parsed"]["page"]}</fpage>'
                    #Find Year
                    elif j==k=="year":
                        ref_word += f'<year>{data["parsed"]["year"]}</year>'
                    #Find DOI
                    elif j==k=="DOI":
                        ref_word += f'<pub-id>{data["parsed"]["DOI"]}</pub-id>'
                    #Find publisher
                    elif j==k=="publisher":
                        ref_word += f'<comment>{data["parsed"]["publisher"]}</comment>'
                    #Find doi_url
                    elif j==k=="doi_url":
                        ref_word += f'<web-url>{data["parsed"]["doi_url"]}</web-url>'
                    #Find year
                    elif j==k=="issued":
                        for d_name in data["parsed"]["issued"]:
                            if d_name=="date-parts":
                                date = data["parsed"]["issued"][d_name][0]
                            else:
                                date = []
                                date.append(data["parsed"]["issued"][d_name])
                            
                        if len(date)>1:
                            dates = calendar.month_name[date[1]]
                            date[1] = ","+dates[:3]+"."
                            
                            ref_word += f'<year>{" ".join(map(str, date))}</year>'
                        else:
                            ref_word += f'<year>{date[0]}</year>'

            ref_word += f'</mixed-citation>'
       
        # print(ref_word)

            #Split the reference text and find author name and year
            xml_text_split = xml_text.split(".")
            count = 1
            #Find the author name and year in reference part
            for i in xml_text_split:
                matches = re.findall(r"\b\d{4}\b", i)
                if count==1:
                    auth_name = i.split(",")[0]
                    count+=1
                elif "&" in i:
                    i = i[1:]
                    auth_name += i.split(",")[0]
                elif matches:
                    if matches[0] in i:
                        auth_name += ","+i
                        break
            
            variables["ref_text_link"].append(auth_name)
            # print(variables["ref_text_link"])

            text=f'<ref id="ref-{variables["ref_id"]}">{ref_word}</ref>'
            
            variables["ref_id"]+=1
        # print(text)
    return text

def reference_temp(xml_text,variables):
    
    text =''
    
    #Example usage:
    references_data = {
        "references": [
            {
                "id": f'{variables["ref_id"]}',
                "reference": f"{xml_text}"
            }
        ]
    }

    api_endpoint = 'http://10.10.10.41:3333/'  #API url endpoint
    references_json = ''
    try:
        #Sending a POST request to the API endpoint with JSON data
        response = requests.post(api_endpoint, json=references_data)
        
        #Checking if the request was successful (status code 200)
        if response.status_code == 200:
            references_json = response.json()  #Assuming the response is JSON
        else:
            print({'error': f'API Error: {response.status_code}'})
    
    except requests.exceptions.RequestException as e:
        pass
        # print({'error': f'Request Exception: {str(e)}'})
    # print(references_json)
    if references_json:
        data = references_json[0]

        #Split the reference text and find author name and year
        xml_text_split = xml_text.split(".")
        count = 1
        #Find the author name and year in reference part
        for i in xml_text_split:
            matches = re.findall(r"\b\d{4}\b", i)
            if count==1:
                auth_name = i.split(",")[0]
                count+=1
            elif "&" in i:
                i = i[1:]
                auth_name += i.split(",")[0]
            elif matches:
                if matches[0] in i:
                    auth_name += ","+i
                    break
                
        variables["ref_text_link"].append(auth_name)
        # print(variables["ref_text_link"])

        text=f'<ref id="ref-{variables["ref_id"]}">{data}</ref>'
        
        variables["ref_id"]+=1
    # print(text,"---")
    return text
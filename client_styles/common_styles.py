#import neccessary librarys
import xml.etree.ElementTree as ET
from lxml import etree
import requests
import re
import config


#MARK: TSP Styles
#Replace specific text in a sentence based on the provided data.
def replace_text(element, data, logger):
    try:
        #Replace text
        for i in data["replace_text"]:
            pattern = fr"{re.escape(i['text'])},*"
            if element.text and i["text"] in element.text:
                element.text = re.sub(pattern, f'{i["replace"]}', element.text)
            if element.tail and i["text"] in element.tail:
                element.text = re.sub(pattern, f'{i["replace"]}', element.tail)
            
    except Exception as e:
        print(f"Error in (replace_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (replace_text function) (common_styles.py)-file {e}")

#MARK: Space add remove
#Add spaces before and after arithmetic operators in the sentence.  
def space_add_text(element, data, logger):
    try:
        #Replace and add space text
        for i in data["space_add_text"]:
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f' {i} ', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f' {i} ', element.tail)
            
    except Exception as e:
        print(f"Error in (space_add_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_add_text function) (common_styles.py)-file {e}")

#Remove spaces before and after special characters in the sentence.
def space_remove_text(element, data, logger):
    try:
        #Replace and remove space text
        for i in data["space_remove_text"]:     #https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f'{i}', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f'{i}', element.tail)
    except Exception as e:
        print(f"Error in (space_remove_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_remove_text function) (common_styles.py)-file {e}")
            
#Add a space before specific units like 'm', 'kg', 'cm', 'k', etc., in the sentence.
def space_before_text(element, data, logger):
    try:
        #Replace and add space only before text
        for i in data["space_before_text"]:
            def func1(elem):
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]} {match[1:].strip()}')
                return elem
                        
            if element.text and i in element.text:
                element.text = func1(element.text)
                
            if element.tail and i in element.tail:
                element.tail = func1(element.tail)
    except Exception as e:
        print(f"Error in (space_before_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_before_text function) (common_styles.py)-file {e}")

#Add a space after specific words like 'no.' in the sentence.
def space_after_text(element, data, logger):
    try:
        # Replace and add space only after text
        for i in data["space_after_text"]:
            def func2(elem):
                pattern = fr"{i}\s*\d"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        mat = match.split(i)
                        elem = elem.replace(match, f'{i} {mat[-1].strip()}')
                return elem 
            
            if element.text and i in element.text.lower():
                element.text = func2(element.text)

            if element.tail and i in element.tail.lower():
                element.tail = func2(element.tail)
    except Exception as e:
        print(f"Error in (space_after_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_after_text function) (common_styles.py)-file {e}")
            
#Remove a space before specific words like '℃' in the sentence.
def remove_space_before_text(element, data, logger):
    try:
        #Replace and remove space only before text
        for i in data["space_remove_before_text"]:
            
            def func2(elem):
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]}{match[1:].strip()}')
                return elem
                
            if element.text:
                element.text = func2(element.text)
                
            if element.tail:
                element.tail = func2(element.tail)
    except Exception as e:
        print(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
       
# Add comma and and in continues sentence     
def add_and(element, data, logger):
    try:
        #Find the continuous text and add "," and last will add "and" 
        for symbol in data["add_and"]:
            def func3(elem):
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern, elem, re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i:
                            split = i.split(",")
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1]
                            elem = re.sub(i, simple, elem)
                return elem
                            
            if element.text:
                element.text = func3(element.text)
                
            if element.tail:
                element.tail = func3(element.tail)
    except Exception as e:
        print(f"Error in (add_and function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (add_and function) (common_styles.py)-file {e}")
            
#Find the repeated text with unit and get the same unit name remove them and add unit in last of the string
def add_all(element, data, logger):
    try:
        for symbol in data["add_all"]:
            def func4(elem):
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*a*n*d*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern, elem, re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i or "and" in i:
                            split = re.split(r'\s*,\s*|\s*and\s*', i)
                            j = ''
                            for sec in split:
                                j += ''.join(k for k in sec if k.isalpha())
                                if j:
                                    break
                            split = [sec.replace(j, '') for sec in split]
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1] + j
                            elem = elem.replace(i, simple)
                return elem
                
            if element.text:
                element.text = func4(element.text)
                
            if element.tail:
                element.tail = func4(element.tail)
    except Exception as e:
        print(f"Error in (add_all function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (add_all function) (common_styles.py)-file {e}")
       
#MARK: Units     
#Chnage the SI_unit minutes,seconds,hours with min,s,h
def si_units(element, data, logger):
    try:
        for si_unit in data["si_units"]:
            def func5(elem):
                pattern = fr'\d+\s*{si_unit["text"]}[s]*'
                result = re.findall(pattern, elem, re.IGNORECASE)
                if result:
                    for i in result:
                        new_text = i[0] + " " + si_unit["replace"]
                        elem = re.sub(i, new_text, elem)
                return elem
                
            if element.text and si_unit["text"] in element.text:
                element.text = func5(element.text)
                
            if element.tail and si_unit["text"] in element.tail:
                element.tail = func5(element.tail)
    except Exception as e:
        print(f"Error in (si_units function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (si_units function) (common_styles.py)-file {e}")

# Remove the ref or refs text present in middle of the paragraph
# https://github.com/Transforma-Dev/Word-to-xml/issues/20#issue-2385186827
def remove_ref(element, data, logger):
    try:
        pattern = r"\w\sRefs*\s"
        if element.text is not None:
            match = re.findall(pattern, element.text, re.IGNORECASE)
            if match:
                element.text = re.sub(match[0], match[0][:2], element.text)
        if element.tail is not None:
            match = re.findall(pattern, element.tail, re.IGNORECASE)
            if match:
                element.tail = re.sub(match[0], match[0][:2], element.tail)
    except Exception as e:
        print(f"Error in (remove_ref function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (remove_ref function) (common_styles.py)-file {e}")
        
#MARK: T&F Client
#Remove the double space in a sentence.
def clean_double_space(element, data, logger):
    try:
        pattern = r"\s{2,}"
        if element.text and "  " in element.text.strip():
            element.text = re.sub(pattern, f' ', element.text.strip())
        if element.tail and "  " in element.tail.strip():
            element.tail = re.sub(pattern, f' ', element.tail.strip())
    except Exception as e:
        print(f"Error in (clean_double_space function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (clean_double_space function) (common_styles.py)-file {e}")
        
#Remove a space before specific words like '℃' in the sentence.
def remove_space_before_dot(element, data, logger):
    try:
        #Replace and remove space only before text
        for i in data["space_remove_dot"]:
            
            def func2(elem, i):
                pattern = fr"\s+{re.escape(i)}"
                return re.sub(pattern, i, elem)
                
            if element.text and i in element.text.strip():
                element.text = func2(element.text, i)
                
            if element.tail and i in element.tail.strip():
                element.tail = func2(element.tail, i)
    except Exception as e:
        print(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
        
#MARK: xref
def find_xref(root, logger):
    try:
        # Find the xref tag and change it
        for element in root.findall(".//xref"):
            attrib = element.get("href")
            if "#ref" in attrib:
                if int(element.text) > len(root.findall(".//ref")):
                    query_tag = ET.Element("query")
                    query_tag.text = "No reference fount for this reference number"
                    element.append(query_tag)
                        
        #Success log message
        logger.info(f"Successfully add the xref style from (find_xref function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_xref function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_xref function) (TSP_styles.py)-file {e}")
    return root
        
#MARK: Reference
def find_reference(root, logger):
    try:
        references = []
        # Find the reference text in ref tag
        for element in root.findall(".//ref"):
            if element.text:
                attributes = element.attrib
                text = "".join(text.strip() for text in element.itertext())

                # Ensure the element is an lxml element
                if isinstance(element, etree._Element):
                    lxml_element = element  # already an lxml element
                else:
                    # If it's an xml.etree.ElementTree.Element, convert it to lxml
                    element_str = ET.tostring(
                        element, encoding='unicode', method='xml')
                    lxml_element = etree.fromstring(element_str)
                tt = etree.tostring(lxml_element, encoding='unicode', method='xml')
                tt = re.sub(r"</?ref[^>]*>", "", tt)
                tt = re.sub(r"\s*\n\s*", " ", tt).strip()

                #Remove the unwanted tags like link, email
                tt = re.sub(r"<(link|email)>", "", tt)
                tt = re.sub(r"\s*</(link|email)>\s*", "", tt)
                tt = re.sub(r"\s*<(link|email)/>\s*", "", tt)
                
                #Remove dot end of the sentence
                if tt and tt.strip().endswith('.'):
                    tt = tt.strip()[:-1]
                    
                data = {
                    "id": element.get('id'),
                    "reference": tt,
                    "style": "ieee"
                }

                references.append(data)
        # Send the references to api and get response
        references_data = {"references": references}
        # print(references_data)
        change_ref = ''
        
        try:
            # Sending a POST request to the API endpoint with JSON data
            response = requests.post(config.api_endpoint, json=references_data)

            # Checking if the request was successful (status code 200)
            if response.status_code == 200:
                change_ref = response.json()  # Assuming the response is JSON
                #Success log message
                logger.info(f"API Successfully running(find_reference function) (TSP_styles.py)-file")
            else:
                print({'error': f'reference API Error: {response.json()}'})
                #Error log message
                logger.error(f"reference API Error in reference api (find_reference function) (TSP_styles.py)-file {e}")

        except requests.exceptions.RequestException as e:
            print(f"Error in reference api (find_reference function) (TSP_styles.py)-file {e}")
            #Error log message
            logger.error(f"Error in reference api (find_reference function) (TSP_styles.py)-file {e}")
            pass

        doi_store = []
        article_title_store = []
        # Find the reference text in ref tag
        for element in root.findall(".//ref"):
            if element.text:
                attributes = element.attrib
                if change_ref:
                    for i in change_ref:
                        if i["id"] == attributes["id"] and i["value"]:
                            soup = ET.fromstring(i["value"])
                            # doi_tag = soup.find("")
                            new_tag = ET.Element("reference-text")
                            new_tag.text = "".join(text.strip() for text in element.itertext())
                            #create label tag
                            label_tag = ET.Element("label")
                            label_tag.text = "".join(ii for ii in i["id"] if ii.isdigit()) + "."
                            element.clear()
                            element.attrib.update(attributes)
                            element.append(label_tag)
                            element.append(soup)
                            element.append(new_tag)
                            
                            #Find the duplicate reference based on pub-id or article-title
                            doi_element = soup.find(".//pub-id")
                            ar_title_element = soup.find(".//article-title")
                            if doi_element is not None and doi_element.text:
                                if doi_element.text not in doi_store:
                                    doi_store.append(doi_element.text)
                                else:
                                    query_tag = ET.Element("query")
                                    query_tag.text = "This is duplicate reference."
                                    element.append(query_tag)
                            else:
                                #generate query tag for unstructure reference
                                structure_query_tag = ET.Element("query")
                                structure_query_tag.text = "This reference was unstructured"
                                element.append(structure_query_tag)
                            if ar_title_element is not None and ar_title_element.text:
                                if ar_title_element.text not in article_title_store:
                                    article_title_store.append(ar_title_element.text)
                                else:
                                    query_tag = ET.Element("query")
                                    query_tag.text = "This is duplicate reference."
                                    element.append(query_tag)
                            #Find the reference cited in article
                            ref_number = [int(el.text) for el in root.findall(".//xref") if "#ref" in el.get("href")]
                            if int(i['id'].split("-")[-1]) not in ref_number:
                                query_tag = ET.Element("query")
                                query_tag.text = "No reference number fount for this reference"
                                element.append(query_tag)
                else:
                    #If reference api was not connected then add simple reference change
                    for j in references_data["references"]:
                        if j["id"] == attributes["id"] and j["reference"]:
                            xml_string = f"<mixed-citation>{j['reference']}</mixed-citation>"
                            attributes = element.attrib
                            soup = ET.fromstring(xml_string)
                            new_tag = ET.Element("reference-text")
                            new_tag.text = "".join(text.strip() for text in element.itertext())
                            #create label tag
                            label_tag = ET.Element("label")
                            label_tag.text = "".join(ii for ii in j["id"] if ii.isdigit()) + "."
                            element.clear()
                            element.attrib.update(attributes)
                            element.append(label_tag)
                            element.append(soup)
                            element.append(new_tag)
                            
                            #Find the duplicate reference based on pub-id or article-title
                            if j["reference"] not in article_title_store:
                                article_title_store.append(j["reference"])
                            else:
                                query_tag = ET.Element("query")
                                query_tag.text = "This is duplicate reference."
                                element.append(query_tag)
                            #Find the reference cited in article
                            ref_number = [int(el.text) for el in root.findall(".//xref") if "#ref" in el.get("href")]
                            if int(j['id'].split("-")[-1]) not in ref_number:
                                query_tag = ET.Element("query")
                                query_tag.text = "No reference number fount for this reference"
                                element.append(query_tag)
                            #generate query tag for unstructure reference
                            structure_query_tag = ET.Element("query")
                            structure_query_tag.text = "This reference was unstructured"
                            element.append(structure_query_tag)
                    
        #Success log message
        logger.info(f"Successfully add reference style(find_reference function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_reference function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_reference function) (TSP_styles.py)-file {e}")
        
    return root
        
        
        
#MARK: Change text
#Find the tags in xml and replace the content
def change_text(root, refere, function_name, data, logger=None):
    try:
        if root is None:
            return  # Safely handle if element is None
        
        #Find the reference text in ref tag
        if root.tag == "body":
            refere = True
            
        #Order the reference and api call to find DOI
        if "find_reference" in function_name:
            root = find_reference(root, logger)                
            return root
        if "find_xref" in function_name:
            root = find_xref(root, logger)                
            return root
        
        #Find the reference text in ref tag
        if root.tag == "ref":
            refere = False
        
        #Replace text or add or remove space in text
        if refere and root is not None:
            function = globals().get(function_name)
            if function:
                function(root, data, logger)
            else:
                raise ValueError(f"Function '{function_name}' not found.")

        for child in root:
            change_text(child, refere, function_name, data, logger)
    except Exception as e:
        return e
        
    return root


# if __name__ == "__main__":
#     import os, sys
#     #Get file name using command line argument
#     command_arg = sys.argv[1]
#     input_file_name = command_arg
    
#     #Get the directory of the python file
#     script_path = os.path.abspath(__file__)
    
#     #Get the directory of the script
#     script_directory = os.path.dirname(script_path)
#     input_file = os.path.join(script_directory, "output",input_file_name)

#     #Output folder name
#     output_file = 'output.xml'
    
#     #Load the XML file
#     tree = ET.parse(input_file)
#     root = tree.getroot()
    
#     import json
    
#     # from journal load the json file
#     with open(f"../json_folder/T&F_styles.json", 'r') as file:
#         data = json.load(file)
    
#     refere = False
#     import spacy

#     nlp = spacy.load("en_core_web_sm")
    
#     change_text(root, refere, "add_and", data)
    
#     tree.write(output_file, encoding='utf-8', xml_declaration=True)
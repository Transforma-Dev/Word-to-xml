# import neccessary librarys
import config
import xml.etree.ElementTree as ET
import sys
import re
import json
import spacy
from lxml import etree
# import index
import requests
import sys

# Import the config file
sys.path.append("../")


class TSP_styles:

    def __init__(self):
        self.article_tit = False
        self.references = []

    # Replace text or add space or remove space in this function
    # https://github.com/Transforma-Dev/Word-to-xml/issues/22#issue-2385189744
    def change_space_text(self, element, data):

        # Replace text
        for i in data["replace_text"]:
            if element.text and i["text"] in element.text:
                element.text = element.text.replace(i["text"], i["replace"])
                
            if element.tail and i["text"] in element.tail:
                element.tail = element.tail.replace(i["text"], i["replace"])

        # Replace and add space text
        for i in data["space_add_text"]:
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f' {i} ', element.text)

            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f' {i} ', element.tail)

        # Replace and remove space text
        # https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
        for i in data["space_remove_text"]:
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f'{i}', element.text)
                
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f'{i}', element.tail)

        # Replace and add space only before text
        for i in data["space_before_text"]:
            def func1(elem):
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]} {match[1:].strip()}')
                return elem 
                
            if element.text and i in element.text.lower():
                element.text = func1(element.text)

            if element.tail and i in element.tail.lower():
                element.tail = func1(element.tail)

        # Replace and add space only after text
        for i in data["space_after_text"]:
            def func2(elem):
                pattern = fr"{i}\s*\d"  # r"\bno\.\d+"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]} {match[1:].strip()}')
                return elem 
            
            if element.text and i in element.text.lower():
                element.text = func2(element.text)

            if element.tail and i in element.tail.lower():
                element.tail = func2(element.tail)

        # Find the continuous text and add "," and last will add "and"
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

        # Find the repeated text with unit and get the same unit name remove them and add unit in last of the string
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

        # Chnage the SI_unit minutes,seconds,hours with min,s,h
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

        # Remove the ref or refs text present in middle of the paragraph
        # https://github.com/Transforma-Dev/Word-to-xml/issues/20#issue-2385186827
        pattern = r"\w\sRefs*\s"
        if element.text is not None:
            match = re.findall(pattern, element.text, re.IGNORECASE)
            if match:
                element.text = re.sub(match[0], match[0][:2], element.text)
        if element.tail is not None:
            match = re.findall(pattern, element.tail, re.IGNORECASE)
            if match:
                element.tail = re.sub(match[0], match[0][:2], element.tail)

    # Find the article title,heading tag and capitalie the article title,heading text except remove conjuction and preposition
    # https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
    def find_artitle(self, element, data, nlp):
        if element.text and element.text.strip():
            doc = nlp(element.text)
            text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
            element.text = text.strip()[0].upper() + text.strip()[1:]

        if element.tail and element.tail.strip():
            doc = nlp(element.tail)
            text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
            element.tail = " " + text.strip()[0].upper() + text.strip()[1:]

    # Remove dot in end of affliation tag and replace the perticuler text
    # https://github.com/Transforma-Dev/Word-to-xml/issues/9#issue-2379911935
    def find_aff(self, element, data, nlp):
        for child in element:
            self.change_text(child, nlp)
            # Replace text
            for i in data["aff_replace_text"]:
                if child.text and i["text"] in child.text:
                    child.text = child.text.replace(i["text"], i["replace"])
                if child.tail and i["text"] in child.tail:
                    child.tail = child.tail.replace(i["text"], i["replace"])

        if child.text and child.text.strip().endswith('.'):
            child.text = child.text[:-1]

    # Find if date is not present in document then add query tag
    # https://github.com/Transforma-Dev/Word-to-xml/issues/11#issue-2385178216
    def find_history(self, element):
        tag = False
        children_to_remove = []
        for child in element:
            for chil in child:
                if chil.tag == "day":
                    if chil.text.strip() == "0":
                        tag = True
                    # Add 0 for single digit day value
                    elif len(element.text.strip()) == 1:
                        chil.text = "0" + chil.text.strip()
            if tag:
                children_to_remove.append(child)

        for child in children_to_remove:
            element.remove(child)
        if tag:
            new_tag = ET.Element("Query")
            new_tag.text = "No History details present in the document"
            element.append(new_tag)

    # Remove dot in end of kwd-group tag and change the first letter as capital others all are small
    # https://github.com/Transforma-Dev/Word-to-xml/issues/14#issue-2385180471
    def find_key(self, element, nlp):
        try:
            n = 1
            for child in element:
                if child.text != None:
                    self.change_text(child, nlp)
                    docs = nlp(child.text)
                    child_text = " ".join([word.text if word.text.isupper() else word.text.lower() for word in docs])
                    doc = nlp(child_text)
                    if n == 1 and child.text.strip():
                        child_ext = ' '.join([word.text if not word.text.isupper() else word.text for word in doc])
                        child.text = " " + child_ext.strip().capitalize() + " "
                        n += 1
                    else:
                        child.text = ' '.join([word.text if not word.text.isupper() else word.text for word in doc])

            if child.text != None:
                if child.text.strip().endswith('.'):
                    child.text = " " + child.text.strip()[:-1]
        except Exception as e:
            print("Error in find_key in tsp_styles.", e)

    # Change the table title and figure title in sentance case.
    # https://github.com/Transforma-Dev/Word-to-xml/issues/17#issue-2385183456
    def find_fig_title(self, element, nlp):
        try:
            if element.text and element.text.strip():
                # https://github.com/Transforma-Dev/Word-to-xml/issues/18#issue-2385184522
                doc = nlp(element.text)
                text = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])

                # Remove extra spaces around commas and inside parentheses
                # Remove space before commas and periods
                text = re.sub(r'\s+([,.])', r'\1', text)
                # Remove space after opening parenthesis
                text = re.sub(r'\(\s*', '(', text)
                # Remove space before closing parenthesis
                text = re.sub(r'\s*\)', ')', text)
                element.text = text.strip()[0].upper() + text.strip()[1:]

                for child in element:
                    def func_fig1(ch):
                        nlp = spacy.load("en_core_web_sm")
                        doc = nlp(ch)
                        child_text = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])
                        split = child_text.split(".")
                        for id, i in enumerate(split):
                            if len(i.strip()) != 0:
                                if id == 0:
                                    ch = i
                                else:
                                    ch += "." + i.strip()[0].upper() + i.strip()[1:]
                        return ch
                        
                    if child.text and child.text.strip():
                        child.text = func_fig1(child.text)
                        
                    if child.tail is not None and child.tail.strip():
                        child.tail = func_fig1(child.tail)
                        
                if element.text and element.text.strip().endswith('.'):
                    element.text = " " + element.text[:-1]
        except:
            print("error in find_fig_title in tsp_style")

    def find_xref(self, element):
        if element.text and element.text.strip():
            if "-" in element.text.lower() or "and" in element.text.lower():
                element.text = element.text.lower().replace("figures", "Figs.",)
            elif "figure" in element.text.lower():
                element.text = element.text.lower().replace("figure", "Fig.",)

    def find_reference(self, element):
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

            data = {
                "id": element.get('id'),
                "reference": tt,
                "style": "ieee"
            }

            self.references.append(data)

    # Correct the back matter order in fn-group tag
    # https://github.com/Transforma-Dev/Word-to-xml/issues/24#issue-2397382765
    def back_order(self, fn_elements, fn_group):
        order_map = {"fund": None, "author": None, "availability": None, "ethics": None, "conflict": None}
        # funding = availability = author = conflict = ethics = None
        for fn in fn_elements:
            bold = fn.find("./p/bold")
            if bold is not None and bold.text:
                text_lower = bold.text.strip().lower()
                for key in order_map:
                    if key in text_lower:
                        order_map[key] = fn
                        break

        fn_group.clear()

        for key in ["fund", "author", "availability", "ethics", "conflict"]:
            if order_map[key]:
                fn_group.append(order_map[key])

    # Find the tags in xml and replace the content
    def change_text(self, element, nlp, refere=None):

        # from journal load the json file
        with open("json_folder/TSP_styles.json", 'r') as file:
            data = json.load(file)

        # Find the article title tag inside the front tag
        if element.tag == "article-title" or self.article_tit:
            self.find_artitle(element, data, nlp)
            self.article_tit = False
            for child in element:
                self.article_tit = True
                self.change_text(child, nlp)

        # Find the affliation tag
        if element.tag == "aff":
            self.find_aff(element, data, nlp)

        # Find the kwd-group tag
        if element.tag == "kwd-group":
            self.find_key(element, nlp)

        # Find the history tag
        if element.tag == "history":
            self.find_history(element)

        # Find heading title in sec tag and change in title case(ULC)
        for heading in element.findall("./sec/title1"):
            self.find_artitle(heading, data, nlp)

        # Find the table title tag
        for title in element.findall('./fig'):
            image_title = title.find('.//title1')
            if image_title is not None:
                self.find_fig_title(image_title, nlp)

        # Find the table title tag
        for title in element.findall('./table-wrap'):
            table_title = title.find('.//title1')
            if table_title is not None:
                self.find_fig_title(table_title, nlp)

        # Find the xref tag and change it
        if element.tag == "xref":
            self.find_xref(element)

        # Find the th tag
        for th in element.findall("./th"):
            if th.text is not None and element.text.strip():
                self.find_fig_title(th, nlp)

        # Find the fn-group tag and change the order of fn group
        fn_elements = element.findall(".//fn")
        fn_group = element.find("./fn-group")
        if fn_group is not None:
            self.back_order(fn_elements, fn_group)

        # Find the reference text in ref tag
        if element.tag == "ref":
            refere = True
            self.find_reference(element)

        # Replace text or add or remove space in text
        if not refere:
            self.change_space_text(element, data)

        for child in element:
            self.change_text(child, nlp, refere)

    # Order the reference part
    def order_reference(self, element, change_ref):
        if element.text:
            attributes = element.attrib
            for i in change_ref:
                if i["id"] == attributes["id"] and i["value"]:
                    soup = ET.fromstring(i["value"])
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

    def add_reference(self, element, nlp, change_ref):

        # Find the reference text in ref tag
        if element.tag == "ref":
            self.order_reference(element, change_ref)

        for child in element:
            self.add_reference(child, nlp, change_ref)

    def modify_xml(self, input_file, output_file):
        # Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        nlp = spacy.load("en_core_web_sm")
        # Variable to find reference then stop the add,remove space
        refere = False
        self.change_text(root, nlp, refere)

        # Send the references to api and get response
        references_data = {"references": self.references}

        change_ref = ''
        try:
            # Sending a POST request to the API endpoint with JSON data
            response = requests.post(config.api_endpoint, json=references_data)

            # Checking if the request was successful (status code 200)
            if response.status_code == 200:
                change_ref = response.json()  # Assuming the response is JSON
            else:
                print({'error': f'API Error: {response.json()}'})

        except requests.exceptions.RequestException as e:
            print("Error in reference api", e)
            pass

        if change_ref:
            self.add_reference(root, nlp, change_ref)

        # Save the modified XML to a new file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"The modified XML file has been saved as '{output_file}'.")

# if __name__ == "__main__":
#     #Get file name using command line argument
#     command_arg = sys.argv[1]
#     input_file_name = os.path.basename(command_arg) if "/" in command_arg else command_arg

#     #Get the directory of the python file
#     script_path = os.path.abspath(__file__)

#     #Get the directory of the script
#     script_directory = os.path.dirname(script_path)
#     input_file = os.path.join(script_directory, "output",input_file_name)

#     #Output folder name
#     output_file = 'output.xml'

#     #Create object for class TSP_styles
#     xml_modifier = TSP_styles()
#     xml_modifier.modify_xml(input_file, output_file)

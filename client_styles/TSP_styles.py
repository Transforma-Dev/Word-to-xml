# import neccessary librarys
import xml.etree.ElementTree as ET
from lxml import etree
import re
import spacy


def add_spaces(reference, incorrect):
    corrected = []
    j = 0  # Pointer for incorrect string
    for char in reference:
        if j < len(incorrect) and char.lower() == incorrect[j].lower():
            corrected.append(incorrect[j])
            j += 1
        else:
            corrected.append(' ')  # Add space if the reference has one
    return ''.join(corrected)

#MARK: Remove dot
# Remove dot in end of the sentence
def remove_dot(element):
    if isinstance(element, etree._Element):
        lxml_element = element  # already an lxml element
    else:
        # If it's an xml.etree.ElementTree.Element, convert it to lxml
        element_str = ET.tostring(
            element, encoding='unicode', method='xml')
        lxml_element = etree.fromstring(element_str)
    
    tt = etree.tostring(lxml_element, encoding='unicode', method='xml')
    if "<article-title>" in tt:
        tag_name = "article-title"
    else:
        tag_name = "title1"
    tt = tt.replace(f"<{tag_name}>", "").replace(f"</{tag_name}>", "").strip()
    if tt.endswith("."):
        tt = tt[:-1]
    tt = "<ttt>" + tt  + "</ttt>"
    element.clear()
    element.append(ET.fromstring(tt))
    for child in list(element):
        if child.tag == "ttt":
            element.text = child.text  # Preserve text inside <ttt>
            element.extend(child)  # Move <ttt>'s children to parent
            element.remove(child)  # Remove <ttt> itself
    # print(element.text)
    # print("Final XML:", ET.tostring(element, encoding="unicode", method="xml"))
    return element

#Remove dot in end of the sentence
def remove_dot(element):
    if isinstance(element, etree._Element):
        lxml_element = element  # already an lxml element
    else:
        # If it's an xml.etree.ElementTree.Element, convert it to lxml
        element_str = ET.tostring(
            element, encoding='unicode', method='xml')
        lxml_element = etree.fromstring(element_str)
    tt = etree.tostring(lxml_element, encoding='unicode', method='xml')
    if tt.endswith("."):
        tt = tt.replace("<title1>", "").replace("</title1>", "").strip()
        tt = "<title1>" + tt[:-1] + "</title1>"
    tt_elem = etree.fromstring(tt)
    return tt_elem

#MARK: Article title
# Find the article title,heading tag and capitalie the article title,heading text except remove conjuction and preposition
# https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
def find_article(root, nlp, data, logger):

    try:
        # Find the article title tag inside the front tag
        for element in root.findall(".//article-title"):
            remove_dot(element)  # Remove dot from title
            def ar_func(element):
                if element.text and element.text.strip():
                    element.text = element.text.strip()
                    doc = nlp(element.text)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.text, text)
                    element.text = text.strip()[0].upper() + text.strip()[1:]

                if element.tail and element.tail.strip():
                    doc = nlp(element.tail)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.tail, text)
                    element.tail = " " + text.strip()[0].upper() + text.strip()[1:]
            if element is not None:
                ar_func(element)
                for child in element:
                    ar_func(child)
                    
        #Success log message
        logger.info(f"Successfully change the article-title tag style from (find_article function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_article function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_article function) (TSP_styles.py)-file {e}")
    
    return root
    
#MARK: Alt title
# Find the alt title and capitalie the alt title except remove conjuction and preposition
# https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
def find_alt_title(root, nlp, data, logger):

    try:
        for element in root.findall(".//alt-title"):
            remove_dot(element)  # Remove dot from title
            def alt_func(element):
                if element.text and element.text.strip():
                    doc = nlp(element.text)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.text, text)
                    element.text = text.strip()[0].upper() + text.strip()[1:]

                if element.tail and element.tail.strip():
                    doc = nlp(element.tail)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.tail, text)
                    element.tail = " " + text.strip()[0].upper() + text.strip()[1:]
            if element is not None:
                alt_func(element)
                for child in element:
                    alt_func(child)
                    
        #Success log message
        logger.info(f"Successfully change the alt tag style from (find_alt_title function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_alt_function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_alt function) (TSP_styles.py)-file {e}")
    
    return root
    
    
#MARK: Affliation
# Remove dot in end of affliation tag and replace the perticuler text
# https://github.com/Transforma-Dev/Word-to-xml/issues/9#issue-2379911935
def find_aff(root, nlp, data, logger):

    try:
        # Find the affliation tag
        for element in root.findall(".//aff"):
            def aff_func(elem, data):
                # Replace text
                for i in data["aff_replace_text"]:
                    if elem.text and i["text"] in elem.text:
                        elem.text = elem.text.replace(i["text"], i["replace"])
                    if elem.tail and i["text"] in elem.tail:
                        elem.tail = elem.tail.replace(i["text"], i["replace"])
                
            if element is not None:
                aff_func(element, data)
                for child in element:
                    aff_func(child, data)

                # if child.text and child.text.strip().endswith('.'):
                #     child.text = child.text[:-1]
            
        #Success log message
        logger.info(f"Successfully change the affliation tag style from (find_aff function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_aff function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_aff function) (TSP_styles.py)-file {e}")
    
    return root
    
    
#MARK: Keyword
# Remove dot in end of kwd-group tag and change the first letter as capital others all are small
# https://github.com/Transforma-Dev/Word-to-xml/issues/14#issue-2385180471
def find_key(root, nlp, data, logger):

    
    # Find the kwd-group tag
    for element in root.findall(".//kwd-group"):
        if element is not None:
            try:
                n = 1
                for child in element:
                    if child.text != None:
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
                #Success log message
                logger.info(f"Successfully change the keyword style from (find_key function) (TSP_styles.py)-file")
            except Exception as e:
                print(f"Error in (find_key function) (TSP_styles.py)-file {e}")
                #Error log message
                logger.error(f"Error in (find_key function) (TSP_styles.py)-file {e}")
            
    return root
    
    
#MARK: History
# Find if date is not present in document then add query tag
# https://github.com/Transforma-Dev/Word-to-xml/issues/11#issue-2385178216
def find_history(root, nlp, data, logger):

    try:
        # Find the history tag
        for element in root.findall(".//history"):
            tag = False
            children_to_remove = []
            for child in element:
                for chil in child:
                    if chil.tag == "day":
                        if chil.text.strip() == "0":
                            tag = True
                        # Add 0 for single digit day value
                        elif len(chil.text.strip()) == 1:
                            chil.text = "0" + chil.text.strip()
                if tag:
                    children_to_remove.append(child)

            for child in children_to_remove:
                element.remove(child)
            if tag:
                new_tag = ET.Element("Query")
                new_tag.text = "No History details present in the document"
                element.append(new_tag)
        #Success log message
        logger.info(f"Successfully change the history tag style from (find_history function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_history function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_history function) (TSP_styles.py)-file {e}")
            
    return root
    
#MARK: Section title
# Find the heading tag and capitalie the heading text except remove conjuction and preposition
# https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
def find_sec_title(root, nlp, data, logger):
    
    try:
        # Find heading title in sec tag and change in title case(ULC)
        for element in root.findall(".//sec/title1"):
            def ar_func(element):
                if element.text and element.text.strip():
                    element.text = element.text.strip()
                    doc = nlp(element.text)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.text, text)
                    element.text = text.strip()[0].upper() + text.strip()[1:]

                if element.tail and element.tail.strip():
                    doc = nlp(element.tail)
                    text = ''.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.text.lower() for word in doc])
                    text = add_spaces(element.text, text)
                    element.tail = " " + text.strip()[0].upper() + text.strip()[1:]
            if element is not None:
                ar_func(element)
                for child in element:
                    ar_func(child)
        #Success log message
        logger.info(f"Successfully change the heading style from (find_sec_title function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_sec_title function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_sec_title function) (TSP_styles.py)-file {e}")
            
    return root
    
#MARK: Figure Title and Table title and th
# Change the table title and figure title and table th tag in sentance case.
# https://github.com/Transforma-Dev/Word-to-xml/issues/17#issue-2385183456
def find_fig_title(root, nlp, data, logger):

    def change_title(element):
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
                    
            #Success log message
            logger.info(f"Successfully change figure and table title style from (find_fig_title function) (TSP_styles.py)-file")
        except Exception as e:
            print(f"Error in (find_fig_title function) (TSP_styles.py)-file {e}")
            #Error log message
            logger.error(f"Error in (find_fig_title function) (TSP_styles.py)-file {e}")
            
    # Find the table title tag
    for element in root.findall(".//fig//title1"):
        if element is not None:
            change_title(element)
    # Find the table title tag
    for element in root.findall(".//table-wrap//title1"):
        if element is not None:
            change_title(element)
    # Find the th tag
    for element in root.findall("./th"):
        if element is not None:
            change_title(element)
            
    return root
    
#MARK: xref
def find_xref(root, nlp, data, logger):

    try:
        # Find the xref tag and change it
        for element in root.findall("xref"):
            if element is not None:
                if element.text and element.text.strip():
                    if "-" in element.text.lower() or "and" in element.text.lower():
                        element.text = element.text.lower().replace("figures", "Figs.",)
                    elif "figure" in element.text.lower():
                        element.text = element.text.lower().replace("figure", "Fig.",)
                        
        #Success log message
        logger.info(f"Successfully add the xref style from (find_xref function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (find_xref function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (find_xref function) (TSP_styles.py)-file {e}")
    return root
    
    
#MARK: Backmatter Order
# Correct the back matter order in fn-group tag
# https://github.com/Transforma-Dev/Word-to-xml/issues/24#issue-2397382765
def back_order(root, nlp, data, logger):
    
    try:
        order_map = {"fund": None, "author": None, "availability": None, "ethics": None, "conflict": None}
        
        # Find the fn-group tag and change the order of fn group
        for element in root.findall(".//fn"):
            # funding = availability = author = conflict = ethics = None
            for fn in element:
                bold = fn.find(".//bold")
                if bold is not None and bold.text:
                    text_lower = bold.text.strip().lower()
                    for key in order_map:
                        if key in text_lower:
                            order_map[key] = fn
                            break

        #Order the fn-group contents
        for fn_group in root.findall(".//fn-group"):
            fn_group.clear()

            for key in ["fund", "author", "availability", "ethics", "conflict"]:
                if order_map[key]:
                    fn_group.append(order_map[key])
                    
        #Success log message
        logger.info(f"Successfully change the back order from (back_order function) (TSP_styles.py)-file")
    except Exception as e:
        print(f"Error in (back_order function) (TSP_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (back_order function) (TSP_styles.py)-file {e}")
    return root
    
    
#MARK: Reference
# def find_reference(root, nlp, data, logger):

#     try:
#         references = []
#         # Find the reference text in ref tag
#         for element in root.findall(".//ref"):
#             if element.text:
#                 attributes = element.attrib
#                 text = "".join(text.strip() for text in element.itertext())

#                 # Ensure the element is an lxml element
#                 if isinstance(element, etree._Element):
#                     lxml_element = element  # already an lxml element
#                 else:
#                     # If it's an xml.etree.ElementTree.Element, convert it to lxml
#                     element_str = ET.tostring(
#                         element, encoding='unicode', method='xml')
#                     lxml_element = etree.fromstring(element_str)
#                 tt = etree.tostring(lxml_element, encoding='unicode', method='xml')
#                 tt = re.sub(r"</?ref[^>]*>", "", tt)
#                 tt = re.sub(r"\s*\n\s*", " ", tt).strip()

#                 #Remove the unwanted tags like link, email
#                 tt = re.sub(r"<(link|email)>", "", tt)
#                 tt = re.sub(r"\s*</(link|email)>\s*", "", tt)
#                 tt = re.sub(r"\s*<(link|email)/>\s*", "", tt)

#                 data = {
#                     "id": element.get('id'),
#                     "reference": tt,
#                     "style": "ieee"
#                 }

#                 references.append(data)
#         # Send the references to api and get response
#         references_data = {"references": references}
        
#         change_ref = ''
#         try:
#             # Sending a POST request to the API endpoint with JSON data
#             response = requests.post('http://127.0.0.1:8000/', json=references_data)

#             # Checking if the request was successful (status code 200)
#             if response.status_code == 200:
#                 change_ref = response.json()  # Assuming the response is JSON
#                 #Success log message
#                 logger.info(f"API Successfully running(find_reference function) (TSP_styles.py)-file")
#             else:
#                 print({'error': f'reference API Error: {response.json()}'})
#                 #Error log message
#                 logger.error(f"reference API Error in reference api (find_reference function) (TSP_styles.py)-file {e}")

#         except requests.exceptions.RequestException as e:
#             print(f"Error in reference api (find_reference function) (TSP_styles.py)-file {e}")
#             #Error log message
#             logger.error(f"Error in reference api (find_reference function) (TSP_styles.py)-file {e}")
#             pass

#         if change_ref:
#             # Find the reference text in ref tag
#             for element in root.findall(".//ref"):
#                 if element.text:
#                     attributes = element.attrib
#                     for i in change_ref:
#                         if i["id"] == attributes["id"] and i["value"]:
#                             soup = ET.fromstring(i["value"])
#                             new_tag = ET.Element("reference-text")
#                             new_tag.text = "".join(text.strip() for text in element.itertext())
#                             #create label tag
#                             label_tag = ET.Element("label")
#                             label_tag.text = "".join(ii for ii in i["id"] if ii.isdigit()) + "."
#                             element.clear()
#                             element.attrib.update(attributes)
#                             element.append(label_tag)
#                             element.append(soup)
#                             element.append(new_tag)
                    
#         #Success log message
#         logger.info(f"Successfully add reference style(find_reference function) (TSP_styles.py)-file")
#     except Exception as e:
#         print(f"Error in (find_reference function) (TSP_styles.py)-file {e}")
#         #Error log message
#         logger.error(f"Error in (find_reference function) (TSP_styles.py)-file {e}")
        
#     return root
                
    

# if __name__ == "__main__":
#     import os
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
    
    
#     find_article(root, output_file)
#     find_alt_title(output_file, output_file)
#     find_aff(output_file, output_file)
#     find_key(output_file, output_file)
#     find_history(output_file, output_file)
#     find_sec_title(output_file, output_file)
#     find_fig_title(output_file, output_file)
#     find_xref(output_file, output_file)
#     back_order(output_file, output_file)
#     find_reference(output_file, output_file)
    #Create object for class TSP_styles
    # xml_modifier = TSP_styles()
    # xml_modifier.modify_xml(root, output_file)

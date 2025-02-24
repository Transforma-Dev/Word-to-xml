# import neccessary librarys
import xml.etree.ElementTree as ET
from lxml import etree
import re
import requests
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
                    text = ''.join([word.tail if word.tail.isupper() else word.tail.capitalize() if word.pos_ not in ["ADP", "DET", "CCONJ"] else word.tail.lower() for word in doc])
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
                    text = add_spaces(element.tail, text)
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

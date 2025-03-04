#Import necessary modules from the python-docx library
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.oxml.shape import CT_Inline
from docx.shape import InlineShape
from bs4 import BeautifulSoup

#Get the directory of the script file
import sys
import os
import re
import xml.etree.ElementTree as ET
import spacy
import json

from convertion import paragraph,table,image   #Import Functions from 'convertion.py' file
from functions import eq_link
from logger import setup_logger

import configparser
import importlib

#Add client styles for the document
def add_styles(output_xml, client, logger):

    # Initialize the config parser
    config = configparser.ConfigParser()
    config.read(f'client_styles/config/{client}_config.ini')

    section = config[client]
    
    #Parse the xml file
    tree = ET.parse(output_xml)
    root = tree.getroot()
    
    nlp = spacy.load("en_core_web_sm")
    
    #Load the common_styles json file
    with open(f"json_folder/common_styles.json", 'r') as file:
        com_data = json.load(file)
        
    # from journal load the json file
    with open(f"json_folder/{client}_styles.json", 'r') as file:
        data = json.load(file)

    for key, value in section.items():
        try:
            # Split module and function name (e.g., TSP_styles.find_reference)
            module_name, func_name = value.rsplit('.', 1)
            
            #Add Common styles
            if "common" in module_name:
                # Dynamically import the submodule
                module = importlib.import_module(f"client_styles.{module_name}")

                # Get the function from the resolved module
                function_to_call = getattr(module, "change_text")
                refere = False

                if callable(function_to_call):
                    # Call the function with arguments
                    root = function_to_call(root, refere, func_name, com_data, logger)
                    #Success log message
                    logger.info(f"Successfully add all {func_name} styles from ({func_name} function) (wordtoxml.py)-file")
                else:
                    print(f"'{func_name}' is not callable in module '{module_name}'.")
            #Add perticuler client styles
            else:
                # Dynamically import the submodule
                module = importlib.import_module(f"client_styles.{module_name}")

                # Get the function from the resolved module
                function_to_call = getattr(module, func_name)

                if callable(function_to_call):
                    # Call the function with arguments
                    root = function_to_call(root, nlp, data, logger)
                else:
                    print(f"'{func_name}' is not callable in module '{module_name}'.")
            
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error resolving function '{value}': {e}")
            
    #Save the modified XML to a new file
    tree.write(output_xml, encoding='utf-8', xml_declaration=True)

    #Apply all common styles
    # xml_modifier = common_styles.Common_styles()
    # xml_modifier.modify_xml(output_xml, output_xml)
    
    # #Create object for class TSP_styles
    # xml_modifier = TSP_styles.TSP_styles()
    # xml_modifier.modify_xml(output_xml, output_xml)


#Create XML header
pre_xml = """<?xml version='1.0' encoding='UTF-8'?>
"""

#Separate paragraph,tables and Inline shapes
def iter_block_items(parent):
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):       #Child is paragraph
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):   #Child is Table
            yield Table(child, parent)
        elif isinstance(child, CT_Inline):     #Child is Inline Shape
            yield InlineShape(child,parent)
        else:
            print(type(child), "Unknown Type")     


#Define funcion to create xml
def convert(input_file_name = None):
    #Get the file name in command line argument.
    if input_file_name == None:
        input_file_name = (sys.argv[1])
        in_file = input_file_name
        input_file_name = os.path.basename(input_file_name) if "/" in input_file_name else input_file_name
        
    #Get the client name from argument
    client_name = sys.argv[2]
    
    #Get the path of the python file
    script_path = os.path.abspath(__file__)
    
    #Get the directory of the script
    script_directory = os.path.dirname(script_path)    
    
    #Define the name of the logs folder and Check if the logs folder exists, if not, create it
    log_path = os.path.join(script_directory, "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logger = setup_logger(os.path.join(log_path, os.path.splitext(input_file_name)[0]))
    
    #Check document was present in the input folder
    input_path = script_directory + "/input/" + input_file_name
    
    if not os.path.exists(input_path):
        with open(in_file, "rb")as f:
            with open(input_path, "wb")as ff:
                ff.write(f.read())
    if not os.path.exists(input_path):
        print(f"File not exists.")
        logger.error(f"File not exists.")
        return ''
    xml = pre_xml

    #Define the name of the output folder and Check if the output folder exists, if not, create it
    output_folder = os.path.join(script_directory, "output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #Separate the file name and extension of the document
    filename, extension = os.path.splitext(input_file_name)

    #Define the name of the Image folder and Check if the image folder exists, if not, create it
    image_folder = os.path.join(script_directory, "image")
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    doc_filename = image_folder + "/" + filename

    #Construct the output file in output folder in html extension
    output_xml_name = filename + '.xml'
    output_xml = os.path.join(output_folder, output_xml_name)

    #Define all neccessary variables in dictionary
    variables = {"previous_text": "","para_count": 1,"key_first":True,"key_store":'',
    "abs_para": False, "corr_auth": False,
    "sec_1": 1,"sec_2": 1,"sec_3": 1,
    "secid": 0,"inner_3_id": 1,
    "sec_1_id": 1,"sec_2_id": 1,"sec_3_id": 1,
    "list_end": False,"list_count": 1,
    "fig": False,"fig_caption": 1,"image_next_para": False,"image_find": False,"image_count": 1,"images_path": "",
    "ref": False,"ref_id": 1,
    "table_no": 1,"table_title": False,
    "aff_tag": True,"aff_id": 1,
    "back_start": "",
    "copyright_state": "",    
    "abbre": False,
    "fn_start": False,
    "noman_text": False,"noman_store": '',
    "ref_text_link":[],"ref_link_save":[],
    "recive":'',
    "author_mail":True,
    "eq_count":1
    }

    #Read the Word document and not present word document then thrown error
    try:
        doc = Document(input_path)
        logger.info("Document upload successfully.")
    except ValueError as e:
        logger.error("There was an error accure in the document Error opening the document")
        print(f"Error opening the document: {e}")
        return ''

    # Add css style in xml file
    # xml+=f'<?xml-stylesheet href="/media/user/daecfb15-4cb5-43c2-a390-112ab6fc48dd/Siva/python/wordtoxml/convertion/styles.css" ?>'
    
    #Add nessaccery tags
    xml += f"<article xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:mml='http://www.w3.org/1998/Math/MathML' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' article-type='research-article' dtd-version='1.0'>"

    #Check the word document and separate them in paragraph,tables and inline shapes
    for para_num, para in enumerate(iter_block_items(doc)):
        """
        Parameters:
            para (object): The element (paragraph, table, or inline shape) from the Word document.
        """
        if isinstance(para, Paragraph):   #Word contain a paragraph
            xml += paragraph(para, doc, doc_filename, variables, para_num, logger) or ""

        elif isinstance(para, Table):    #Word contain a table
            xml += table(para, doc, doc_filename, variables, logger)

        elif isinstance(para, InlineShape):     #Word contain a Inline shape
            xml += image(para, doc, logger)

        #Change the email in author name 
        if "</contrib-group>" in xml and variables["author_mail"]:
            if "<email>" in xml:
                match = re.search(r'<email>.*</email>', xml, re.IGNORECASE)
                match = match.group() if match else None
                xml = xml.replace("<mail>demo@email.com</mail>", match)
                variables["author_mail"] = False

    #Call function to solve the xref tag for references, reference number citation
    xml = eq_link.add_ref_tag(xml, variables, logger)

    xml += f"</article>"

    #Parse the HTML with BeautifulSoup for pretty-printing
    soup = BeautifulSoup(xml, 'xml')
    pretty_xml = soup.prettify()

    #Remove the xml header in middle of the content
    if '<?xml version="1.0"?>' in pretty_xml:
        pretty_xml = pretty_xml.replace('<?xml version="1.0"?>', '')

    #Write the HTML content to a file
    with open(output_xml, 'w', encoding="utf-8") as file:
        file.write(pretty_xml)
        
    #Apply styles
    add_styles(output_xml, client_name, logger)

    #Success log message
    logger.info(f"File converted Successfully.")
        
    return output_xml_name


# convert()

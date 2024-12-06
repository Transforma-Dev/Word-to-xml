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

from convertion import paragraph,table,image   #Import Functions from 'convertion.py' file
from functions import eq_link
#Import the styles
from client_styles import TSP_styles,common_styles


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
        input_file_name = os.path.basename(input_file_name) if "/" in input_file_name else input_file_name
    
    #Get the path of the python file
    script_path = os.path.abspath(__file__)
    
    #Get the directory of the script
    script_directory = os.path.dirname(script_path)
   
    #Check document was present in the input folder
    input_path = script_directory + "/input/" + input_file_name
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
    except ValueError as e:
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
            xml += paragraph(para, doc, doc_filename, variables, para_num)

        elif isinstance(para, Table):    #Word contain a table
            xml += table(para, doc, doc_filename, variables)

        elif isinstance(para, InlineShape):     #Word contain a Inline shape
            xml += image(para, doc)

        #Change the email in author name 
        if "</contrib-group>" in xml and variables["author_mail"]:
            if "<email>" in xml:
                match = re.search(r'<email>.*</email>', xml, re.IGNORECASE)
                match = match.group() if match else None
                xml = xml.replace("<mail>demo@email.com</mail>", match)
                variables["author_mail"] = False

    #Call function to solve the xref tag for references
    xml = eq_link.add_ref_tag(xml, variables)

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

    #Create object for class TSP_styles
    xml_modifier = TSP_styles.TSP_styles()
    xml_modifier.modify_xml(output_xml, output_xml)

    xml_modifier = common_styles.Common_styles()
    xml_modifier.modify_xml(output_xml, output_xml)

    return output_xml_name


#convert()

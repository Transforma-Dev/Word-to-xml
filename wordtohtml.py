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

#Import additional module
import base64
from lxml import etree
from xml.etree import ElementTree as ET
from io import StringIO

#Get the directory of the script file
import sys
import os

from pa import paragraph,table   #Import Functions from 'pa.py' file

# Create HTML header and body
pre_xml = """<?xml version='1.0' encoding='UTF-8'?>"""

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



def convert(input_file_name):
    #Get the directory of the file
    script_directory = "/home/user2/Documents"
   
    #Check command line argument was present in input folder
    input_path=script_directory+"/input/"+input_file_name
    xml = pre_xml

    #Define the name of the output folder and Check if the output folder exists, if not, create it
    output_folder = os.path.join(script_directory, "output")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #Separate the file name and extension of the document
    filename,extension=os.path.splitext(input_file_name)

    #Define the name of the Image folder and Check if the image folder exists, if not, create it
    image_folder = os.path.join(script_directory, "image")

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    doc_filename=image_folder+"/"+filename

    #Construct the output file in output folder in html extension
    output_xml_name = filename + '.xml'
    output_xml = os.path.join(output_folder, output_xml_name)

    #Read the Word document
    doc = Document(input_path)
    
    xml+=f"<article xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:mml='http://www.w3.org/1998/Math/MathML' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' article-type='research-article' dtd-version='1.0'>"

    #Check the word document and separate them in paragraph,tables and inline shapes
    for para in iter_block_items(doc):
        """
        Parameters:
            para (object): The element (paragraph, table, or inline shape) from the Word document.
        """
        if isinstance(para, Paragraph):   #Word contain a paragraph
            xml += paragraph(para, doc,doc_filename)
            
        elif isinstance(para, Table):    #Word contain a table
            xml += table(para, doc,doc_filename)
        
        elif isinstance(para, InlineShape):     #Word contain a Inline shape
            xml+=image(para,doc)
    
    xml+=f"</article>"

    #Parse the HTML with BeautifulSoup for pretty-printing
    soup = BeautifulSoup(xml, 'xml')
    pretty_xml = soup.prettify()

    #Remove the xml header in middle of the content
    if '<?xml version="1.0"?>' in pretty_xml:
        pretty_xml = pretty_xml.replace('<?xml version="1.0"?>', '')

    #Write the HTML content to a file
    with open(output_xml, 'w', encoding="utf-8") as file:
        file.write(pretty_xml)

    return output_xml_name


convert("peerj-17265.docx")


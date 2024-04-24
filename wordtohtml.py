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
pre_html = """<?xml version='1.0' encoding='UTF-8'?>"""

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
    script_directory = "/home/user2/python/wordtoxml/convertion"
   
    #Check command line argument was present in input folder
    input_path=script_directory+"/input/"+input_file_name
    html = pre_html
    #Read the Word document
    doc = Document(input_path)
    
    html+=f"<article>"

    #Check the word document and separate them in paragraph,tables and inline shapes
    for para in iter_block_items(doc):
        """
        Parameters:
            para (object): The element (paragraph, table, or inline shape) from the Word document.
        """
        if isinstance(para, Paragraph):   #Word contain a paragraph
            html += paragraph(para, doc)
            
        elif isinstance(para, Table):    #Word contain a table
            html += table(para, doc)
        
        elif isinstance(para, InlineShape):     #Word contain a Inline shape
            html+=image(para,doc)
    
    html+=f"</article>"

    # Parse the HTML with BeautifulSoup for pretty-printing
    soup = BeautifulSoup(html, 'xml')
    pretty_html = soup.prettify()

    if '<?xml version="1.0"?>' in pretty_html:
        pretty_html = pretty_html.replace('<?xml version="1.0"?>', '')

    #Define the name of the output folder
    output_folder = os.path.join(script_directory, "output")

    #Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #Construct the output file in output folder in html extension
    output_html_name = os.path.splitext(input_file_name)[0] + '.xml'
    output_html = os.path.join(output_folder, output_html_name)

    #Write the HTML content to a file
    with open(output_html, 'w', encoding="utf-8") as file:
        file.write(pretty_html)

    return output_html_name


convert("EJ-EDU_652.docx")


#Get the directory of the script file
import sys
import os

#Import additional module
import base64     
import re
from lxml import etree
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from io import StringIO
from unidecode import unidecode
import subprocess
import json
from functions import title,authors,abstract_key,heading,list_file,image_table,reference,other_tags,eq_link


#Define the function to convert a paragraph from word document
def paragraph(para,doc,doc_filename,variables,para_num):

    """
    Convert a paragraph from a Word document into XML format.

    Parameters:
        para (Paragraph): The Paragraph object from the Word document.
        doc (Document): The Document object representing the converter Word document.

    Returns:
        The XML representation of the paragraph.
    """
    
    #Initialize the all variables
    xml_text=""
    math_count = 0    #Initialize math count for math equations 
    box_text = ''
    
    #Remove space between start and end of the string
    space_strip=para.text.strip() 

    #Split the filename in folder path
    file_name = os.path.basename(doc_filename)
    journal=file_name.split("_")

    #Construct the filename with .pdf extension
    filename = f"{file_name}.pdf"

    #from journal load the json file
    with open("json_folder/journal.json",'r') as file:
        data = json.load(file)

    #Skip the paragraph
    if space_strip.strip().lower().startswith(("running","doi")):
        xml_text=''
        return xml_text
    
    #Find the all bold paragraph
    all_bold = all(run.bold for run in para.runs if run.text.strip()!='')
    # print(para.text)
    #Convert the pargaraph into xml
    xml=para._element.xml
    # print(xml)
    root = ET.fromstring(xml)

    #Find the square bracket text present in paragraph
    if "<w:sdt>" in xml:
        box_text = eq_link.sq_text(root,file_name,variables)

    #Check where the boxed text are present in paragraph
    if "<wps:txbx>" in xml:
        box_text = eq_link.txbox(root,file_name,variables)
        

    #Check where the equation are present in paragraph
    if "<m:oMath" in xml:
        values,xml_text,math_count = eq_link.eq(root,xml_text,para,math_count,file_name,variables)

    #Check the paragraph to find the hyperlink
    if para.hyperlinks:
        siva,text,address,font,p = eq_link.hyper(root,para)

    #Iterate through each run in the paragraph
    for run in para.runs:
        """
        Iterate through the runs in the paragraph and process each run accordingly.

        Parameters:
            i (Run): The Run object representing a portion of the paragraph text.
        """
        
        # print(run.text,len(run.text))
        #Check if the paragraph contains math equations
        if '<m:oMath' in xml:
            values,xml_text,math_count = eq_link.run_eq(root,xml_text,para,run,values,math_count,file_name,variables)

        #Convert the run text in xml
        xmlstr = str(run._element.xml)

        #Check if the run contain an inline image image
        if 'pic:pic' in xmlstr:
            xml_text = eq_link.inline_image(doc,doc_filename,file_name,xmlstr,variables,xml_text)

        #Print the hyperlink present in paragraph
        if para.hyperlinks:
            siva,p,xml_text,text,address,font = eq_link.print_hyper(run,para,siva,p,xml_text,text,address,font)

        run.text = unidecode(run.text)    #Convert all non-ascii characters to the closest ascii character

        run.text=run.text.replace("<","&#60;").replace("<<","&#60;&#60;")   #Replace the '<' symbol in string format

        #Find superscript text
        if run.font.superscript and len(para.text)!=0:
            xml_text+=f'<sup>{run.text}</sup>'
        #Find the italic text
        elif run.font.italic and not run.text.lower()=="key words" and len(run.text)!=0 and not run.text.isspace():
            xml_text+=f'<italic>{run.text}</italic>'
        #Find subscript text
        elif run.font.subscript and len(para.text)!=0:
            xml_text+=f'<sub>{run.text}</sub>'
        #Find underlined text
        elif run.font.underline and len(para.text)!=0:
            xml_text+=f'<under>{run.text}</under>'
        #Find bold text
        elif run.bold and len(run.text)!=0  and not run.text.isspace():
            matches = re.findall(r'^Table \d+:', para.text, flags=re.IGNORECASE | re.MULTILINE)
            if matches and matches[0] in run.text or run.text == ":":
                xml_text+=f'{run.text}'
            else:
                xml_text+=f'<bold>{run.text}</bold>'

        else:
            xml_text+=f'{run.text}'

    #Print the link text at end of the paragraph
    if para.hyperlinks and len(text)!=0:
        xml_text+=f'<email>{text[0]}</email>'


    
    #Find the title of the document
    if (variables["para_count"]==1 or (variables["para_count"]==2 and all_bold and not para.style.name.startswith("author") and "," not in para.text)) and len(para.text)!=0:
        # print(para.text)
        xml_text=title.title(para,xml_text,variables,data,journal,file_name)

    #Find author name in word document
    elif (para.style.name.startswith("Authors") or variables["para_count"]==2) and len(para.text)!=0:
        xml_text = authors.author_name(xml_text,variables)
        
    #Find corresponding author text in paragraph in word document and change the tag into author-notes
    elif ("corresponding author" in para.text.lower() or ".com" in para.text.lower() or para.text.strip().lower().startswith(("e-mail", "*", "email"))) and not "Materials" in para.text and not "doi" in para.text and para_num<25 and len(para.text)!=0:
        xml_text = authors.corres_author(xml_text,variables)

    #Find the recived text paragraph in document
    elif (para.text.strip().lower().startswith("received")):
        variables["recive"] = para.text
        xml_text = ''
        return xml_text

    #Find the next paragraph is abstract paragraph
    elif variables["previous_text"].strip().lower() in ["abstract","abstract:"] and len(para.text)!=0:
        xml_text = abstract_key.abstract(xml_text,variables,filename)

    #Find abstract in word document and skip this
    elif para.text.strip().lower() in ["abstract", "abstract:"] and len(para.text)!=0:       
        variables["previous_text"]=para.text
        xml_text=''
        if variables["aff_tag"]:
            xml_text+=f'</contrib-group>'
            variables["aff_tag"]=False
        return xml_text

    #Check the paragraph was starts with abstract text
    elif para.text.strip().lower().startswith("abstract") or "abstract" in box_text.lower():
        if box_text:
            xml_text=box_text
            box_text=''
        xml_text = abstract_key.abstract(xml_text,variables,filename)

    #Check the resume and mots cell in document
    elif "resume" in para.text.lower():
        xml_text = other_tags.noman(xml_text,variables)
    
    #Check para.text is keyword then skip them
    elif para.text.strip().lower()=="keywords":
        variables["previous_text"]=para.text.strip()
        xml_text=''
        return xml_text

    #Check previous text was equal to keyword
    elif variables["previous_text"].lower()=="keywords":
        xml_text=abstract_key.keyword_text(xml_text,variables)

    #Check the paragraph was starts with keyword text
    elif para.text.strip().lower().startswith("keyword") or para.text.strip().lower().startswith("key words"):
        xml_text=abstract_key.keyword_text(xml_text,variables)

    #Find paragraph between author and mail and apply tag aff
    elif variables["aff_tag"] and variables["para_count"]>2 and len(para.text)!=0 and not para.text.isspace():
        xml_text = authors.aff_para(xml_text,variables)

    #Find acknowledgment paragraph in word document and change the tag into ack and p
    elif re.fullmatch(r'\backnowledg[e]*(?:ment|ments)?\b\:*', variables["previous_text"].strip(),flags=re.IGNORECASE):
        xml_text = other_tags.ack_text(xml_text,variables)

    #Find acknowledgment in word document and skip this
    elif re.fullmatch(r'\backnowledg[e]*(?:ment|ments)?\b\:*', para.text.strip(),flags=re.IGNORECASE):
        xml_text = other_tags.ack_para(xml_text,variables,para)

    #Find acknowledgment in word document and skip this
    elif para.text.strip().lower().startswith("acknowledg") and not re.search(r'^Acknowledging', para.text,re.IGNORECASE):
        xml_text = other_tags.ack_text(xml_text,variables)

    #Find funding statement in word document
    elif para.text.strip().lower().startswith("funding"):
        xml_text="<fn-group>"+xml_text
        xml_text = other_tags.funding_text(xml_text,variables)

    #Print abbrevation contents
    elif space_strip.lower()=="abbreviations":
        xml_text = other_tags.abbrevation(xml_text,variables)
    
    #Print abbrevation contents
    elif variables["abbre"] and len(space_strip)!=0:
        xml_text = other_tags.abbrev_text(xml_text,variables)

    #Find references in word document and change the tag into back,ref-list,title
    elif space_strip.strip().lower().startswith(("references","reference","bibliographie")) and len(para.text)!=0:
        xml_text = reference.reference(xml_text,variables)

    #Find the fn tag 
    elif variables["fn_start"] and len(para.text)!=0:
        xml_text = other_tags.funding_text(xml_text,variables)

    #Find figure caption in word document and change the tag into fig
    elif (para.style.name.startswith("figure caption") or variables["image_next_para"] or re.search(r'^Figure \d+(\:|\.|\s)+', para.text)) and not re.search(r'^\d', para.text) and len(para.text)!=0:
        #print(xml_text)
        xml_text = image_table.image_caption(xml_text,variables)

    #Find table title in word document and change the tag into table-wrap
    elif (para.style.name.startswith("Table Title") or re.search(r'^Table \d+(\:|\.|\s)+', para.text)) and len(para.text)<=150 and len(para.text)!=0:
        xml_text = image_table.table_heading(xml_text,variables)
    
    #Find reference paragraph in word document and change the tag into ref
    elif variables["ref"] and para.text!="":
        xml_text = reference.reference_temp(xml_text,variables)

    #Find the Nomenclature text in word document
    elif para.text.strip().lower().startswith("nomenclature"):
        xml_text = other_tags.noman(xml_text,variables)

    #Change noman tag text
    elif variables["noman_text"] and not "introduction" in space_strip.lower() and len(para.text)!=0:
        
        xml_text = other_tags.noman_para(xml_text,variables)
        # print(xml_text)

    #Find heading in word document and change the tags into sec
    elif ((((para.alignment==1 and all_bold) or para.style.name.startswith("Heading 1") or space_strip.lower()=="introduction" or space_strip.strip().lower().startswith("conflict") or re.search(r'^((\d+\.*\)*\s*|\w+\.+\s*))(\w+)', para.text)) and (variables["sec_1"]==1)) or (((para.alignment==0 and all_bold) or para.style.name.startswith("Heading 2") or re.search(r'^\d+\.\d+(\.*|\s)+.*$', para.text)) and (variables["sec_2"]==1)) or ((para.style.name.startswith("Heading 3") or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text)) and len(para.text.split())<20 and variables["sec_3"]==1)) and (not space_strip.lower().startswith("conclusion")) and len(para.text.strip())!=0:
        # print(para.text,"---****")
        xml_text=heading.heading(para,space_strip,xml_text,variables)

    #Find heading in word document and change the tags sec
    elif (((para.alignment==1 and all_bold) or para.style.name.startswith("Heading 1") or space_strip.strip().lower().startswith(("conflict","discussion","conclusion","materials"))) or ((para.alignment==0 and all_bold)  or para.style.name.startswith("Heading 2")) or (para.style.name.startswith("Heading 3") or re.search(r'^((\b[IVX]+\.\s*|\d+(\.|\)|\s)+))(\w+)', para.text) or (all_bold and len(para.text.strip().split())<15))) and not re.search(r'^(Note:|Figure \d)', para.text.strip(),re.IGNORECASE) and len(para.text.split())<18 and len(para.text.strip())!=0:
        # print(para.text,len(para.text))
        xml_text = heading.sub_heading(para,xml_text,variables,space_strip,all_bold)

    #Find List in word document and change the tag into list-item and p
    elif (para.style.name.startswith("List Paragraph") or "<w:numPr>" in xml) and not all_bold and len(para.text)!=0:
        #print(xml_text)
        xml_text = list_file.list_para(xml_text,variables,xml,root)

    #Close the list tag
    elif variables["list_end"]:
        xml_text = list_file.list_close(xml_text,variables,para)  

    elif box_text:
        xml_text = eq_link.add_tag(box_text)
        xml_text=f'<p>{xml_text}</p>' 
        box_text = ''

    #Else print p tag
    elif len(para.text)!=0 and not para.text.isspace():
        xml_text = eq_link.add_tag(xml_text)
        xml_text=f'<p>{xml_text}</p>' 

    #Find the image caption or next paragraph of image
    if variables["image_find"]:
        variables["image_next_para"]=True

    if len(para.text)!=0:
        variables["previous_text"]=para.text

    return xml_text


#Define function to find the table in word document
def table(table,doc,doc_filename,variables):

    """
    Convert a table from a Word document into HTML format.

    Parameters:
        table (Table): The Table object from the Word document.
        doc (Document): The Document object representing the Word document.

    Returns:
        str: The HTML representation of the table.
    """
    empty_table = False
    xml_text = ''

    #Count number of rows and columns in table
    row_count = len(table.rows)
    col_count = len(table.rows[0].cells)

    #Check if the table text is not empty or not
    for row in table.rows:
        for cell in row.cells:
            if cell.text.strip():  
                empty_table = True
                

    if not empty_table:
        return xml_text

    xml=table._element.xml
    root = ET.fromstring(xml)

    #Find col-group was center or not 
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    jc_element = root.find('.//w:jc', namespaces=ns)
    
    #Check if the element is found
    if jc_element is not None:
        #Check if the attribute exists and get its value
        center_value = jc_element.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
        if center_value is not None:
            center_value= center_value
        else:
            center_value = ''
    else:
        center_value = ''
    
    #Find the number of col tag in col-group
    colgroup_text=""
    for i in range(col_count):
        if center_value=="center":
            colgroup_text+="<col align='center'></col>"
        else:
            colgroup_text+="<col></col>"

    #Split the filename in folder path
    file_name = os.path.basename(doc_filename)
    filename = f'{file_name}-table-{variables["table_no"]}.tif'

    #Determine the table-wrap tag based on the table title presence
    table_wrap_tag = f'<table-wrap id="table-{variables["table_no"]}">' if not variables["table_title"] else ''

    #Generate the XML text
    xml_text = f'{table_wrap_tag}<alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filename}"/><table><colgroup>{colgroup_text}</colgroup>'
    
    #Store the span of merged cells
    li = []
    variables["table_title"]=True
    
    #Find rows in table
    for r, row in enumerate(table.rows):  

        #Find the tanle row was center or not
        row_center = False
        for cell in row.cells:
            #Find the vAlign element within the cell
            v_align = cell._element.find('.//w:vAlign', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
            if v_align is not None and v_align.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') == 'center':
                row_center = True
                break
                
        #find the row height
        h = row.height.inches * 96 if row.height is not None else 25

        #Present first row in thead tag other present in tbody tag
        tag = "<thead>" if r == 0 else ""
        alignment = " align='center'" if row_center else ""
        xml_text += f"{tag}<tr{alignment}>"

        tt=False
        tr=False
        
        #Find columns in table  
        for c, cell in enumerate(row.cells):   
            # print(cell.text)
            #Skip the cell that are part of a merged region
            if (r, c) in li:
                continue 

            #Call functio to fin no of rowspan and colspan
            r,c,row,cell,table,li,tt,tr,xml_text = image_table.row_col_span(r,c,row,cell,table,li,tt,tr,xml_text)
           
            #Iterate through the cell text
            for para in cell.paragraphs:  
            
                math_count = 0    #Initialize math count for math equations

                #Convert the pargaraph into xml
                xml=para._element.xml
                root = ET.fromstring(xml)

                #Check where the equation are present in paragraph
                if "<m:oMath" in xml:
                    values,xml_text,math_count = eq_link.eq(root,xml_text,para,math_count,file_name,variables)
                
                #Iterate through the run object
                for run in para.runs:
                    """
                    Iterate through the runs in the cell paragraph and process each run accordingly.

                    Parameters:
                        i (Run): The Run object representing a portion of the cell paragraph text.
                    """

                    xml = para._element.xml    
                    #Check if the paragraph contains math equations
                    if '<m:oMath' in xml:
                        values,xml_text,math_count = eq_link.run_eq(root,xml_text,para,run,values,math_count,file_name,variables)
                    
                    #Convert the run text into xml
                    xmlstr = str(run.element.xml) 

                    #Check if the run contain an image
                    if 'pic:pic' in xmlstr:
                        xml_text = eq_link.inline_image(doc,doc_filename,file_name,xmlstr,variables,xml_text)

                    #If keyword present in run.text the skip this
                    if "keyword" in run.text.lower():
                        continue
                    
                    #Check for formatting properties and create corresponding XML elements
                    if run.font.superscript:
                        xml_text+=f'<sup>{run.text}</sup>'
                    elif run.font.subscript:
                        xml_text+=f'<sub>{run.text}</sub>'
                    elif run.font.italic:
                        xml_text+=f'<italic>{run.text}</italic>'
                    elif run.font.underline:
                        xml_text+=f'<under>{run.text}</under>'
                    elif "<" in run.text:
                        run.text=run.text.split()
                        text=""
                        for i in run.text:
                            if i=="<":
                                text+=f'&#60;'
                            else:
                                text+=f'{i}'
                        xml_text+=f'{text}'
                    else:
                        #Default case (no special formatting)
                        xml_text+=f'{run.text}'

            #Close the td,tr,table tag
            xml_text+=f"</td>"

        if r==0:
            xml_text += "</tr></thead><tbody>"
            thead=False
        else:
            xml_text+="</tr>"

    variables["table_title"]=False
    xml_text += "</tbody></table></alternatives></table-wrap>"
    variables["table_no"]+=1
    return xml_text



def image(image,doc):
    """
    Convert an inline shape from a Word document into HTML format.

    Parameters:
        inline_shape (InlineShape): The InlineShape object from the Word document.
        doc (Document): The Document object representing the Word document.

    Returns:
        str: The HTML representation of the inline shape.
    """

    xml_text+="<div>"
    #Find the Inline Shape is an images
    if image.type.name == "PICTURE":  
        image_bytes = image._inline.graphic.graphicData.pic.blipFill.blip.embed
        rel = doc.part.rels[image_bytes]
        image_path = rel.target_part.blob

        #Find the image width and height
        width = image.width.inches*96
        height = image.height.inches*96

        encoded_image = base64.b64encode(image_path).decode('utf-8')

        #Check if the image was center or not
        #if shape.alignment==1:
            #html += f"<img src='data:image/png;base64,{encoded_image}' widt h='{width}pt' height='{height}pt' style='center' />"
        #else:
        xml_text += f"<img src='data:image/png;base64,{encoded_image}' widt h='{width}px' height='{height}px'/></div>"

        return xml_text
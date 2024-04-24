from docx.enum.dml import MSO_THEME_COLOR

#Import additional module
import base64     
from lxml import etree
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from io import StringIO
from unidecode import unidecode
import subprocess
import unicodedata
from anyascii import anyascii

previous_text = ""
kwd=False
end_sec=1
end_list=1
fig=False
ref=False
table_title=False
table_caption=False

#Define the function for convert a paragraph from word document
def paragraph(para,doc):

    # Keep track of the previous paragraph text
    global previous_text,kwd,end_sec,end_list,ref,fig,table_title,table_caption
    xml_text=""
    key_text=""

    if para.text=="":
        return xml_text

    all_bold = all(run.bold for run in para.runs)

    """elif para.style.name.startswith("List Paragraph") and end_list==1:  
        xml_text+=f'<list><list-item><p>'
        end_list+=1"""

    if para.style.name.startswith("Heading 2"):  
        xml_text+=f'<title-group>'

    elif para.style.name.startswith("List Paragraph"):  
        xml_text+=f'<list-item><p>'

    elif para.style.name.startswith("figure caption"):  
        xml_text+=f'<fig>'
        fig=True

    elif para.style.name.startswith("Table Title"):  
        xml_text+=f'<table-wrap>'
        table_title=True

    elif previous_text.lower()=="abstract" :
        xml_text+=f'<abstract abstract-type="abstract"><p>'

    elif para.text.lower()=="abstract":
        previous_text=para.text
        return xml_text

    elif para.text.lower()=="references":
        xml_text+=f'</sec></body><back><ref-list><title>'
        ref=True
    
    elif all_bold and end_sec==1:
        xml_text+=f'<body><sec><label>1</label><title>'
        end_sec+=1

    elif all_bold:
        xml_text+=f'</sec><sec><label>1</label><title>'

    elif "keyword" in para.text.lower():
        xml_text+=f'<kwd-group kwd-group-type="author">'
        kwd=True

    elif ref:
        xml_text+=f'<ref>'

    else:
        xml_text+=f'<p>' 

    eq = 2   #Initialize eq =2
    math_count = 0    #Initialize math count for math equations 

    #Convert the pargaraph into xml
    xml=para._element.xml
    #print(xml)
    root = ET.fromstring(xml)

    #Check where the equation are present in paragraph
    if "<m:oMath" in xml:
        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
        }
        values = []     #Define the empty list for store the equation paragraph
        for elem in root.iter():
                if elem.tag.endswith("Math"):      #Find math equation text in paragraph
                    text = ""
                    for t_elem in elem.findall(".//m:t", namespaces=ns): 
                        text += t_elem.text if t_elem.text else ""
                    if text!="":
                        values.append(text)
                if elem.tag.endswith("r"):      #Find normal text in paragraph
                    tex = ""
                    for t_elem in elem.findall(".//w:t", namespaces=ns): 
                        tex += t_elem.text if t_elem.text else ""
                    if tex!="":
                        values.append(tex) 
        #If the paragraph contain only equation.
        if len(values)==1:
            ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
            math_xml = para._element.findall('.//m:oMath', namespaces = ns)
            if len(math_xml) > math_count:
                cur_math = math_xml[math_count]
                math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                math_count = math_count + 1
                from lxml import etree
                xslt_file = "config/omml2mml.xsl"
                xslt_doc = etree.parse(xslt_file)
                transformer = etree.XSLT(xslt_doc)
                xml_doc = etree.fromstring(xml)
                transformed_tree = transformer(xml_doc)
                #Print the math equation
                transformed_tree = str(transformed_tree).replace("mml:", "")
                mathml = str(transformed_tree)
                #print(mathml)
                if eq!=2:
                    xml_text+=f'<kwd-group>{mathml}</kwd-group>'
                    eq=2
                else:       
                    xml_text+=f'<kwd-group>{mathml}</kwd-group>'

    #Check the paragraph to find the hyperlink
    if para.hyperlinks:
        ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
        }
        siva = []
        for elem in root.iter():
            if elem.tag.endswith("r"):      #Find normal text in paragraph
                tex = ""
                for t_elem in elem.findall(".//w:t", namespaces=ns): 
                    if t_elem.text is not None:
                        tex += t_elem.text if t_elem.text else ""
                if tex!="":
                    siva.append(tex)  
        #print(siva)
    
    #Check the paragraph contain hyperlink or not
    if para.hyperlinks :
        #Initialize an empty list to store hyperlink text,address,font size
        text=[]
        address=[]
        font=[]
        #Iterate throgh the each hyperlink in the paragraph
        for hyperlink in para.hyperlinks:
            for run in hyperlink.runs:
                hyperlink_font_size = run.font.size    #Find the fond size of the hyperlink
                hyperlink_font_size = int(hyperlink_font_size.pt) if hyperlink_font_size else 12
                font.append(hyperlink_font_size)

            #Get the hyperlink address and text
            link_address = hyperlink.address
            link_text = hyperlink.text
            if link_text in para.text:
                if hyperlink.address:
                    for i in range(len(siva)):
                        if siva[i]==link_text:
                            siva[i]="<"
                    p = ''.join(siva)
                    text.append(link_text)
                    address.append(link_address)

    #print(para.text,len(para.text))
    # Iterate through each run in the paragraph
    for run in para.runs:
        # print(run.text,len(run.text))
        #Check if the paragraph contains math equations
        if '<m:oMath' in xml:
            stri = run.text
            try:
                if values[0]!=stri:
                    #Check the length of run object equal to zero
                    if len(run.text) != 0:
                            ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
                            math_xml = para._element.findall('.//m:oMath', namespaces = ns)
                            if len(math_xml) > math_count:
                                cur_math = math_xml[math_count]
                                math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                                math_count = math_count + 1
                                from lxml import etree
                                xslt_file = "config/omml2mml.xsl"
                                xslt_doc = etree.parse(xslt_file)
                                transformer = etree.XSLT(xslt_doc)
                                xml_doc = etree.fromstring(math_str)
                                transformed_tree = transformer(xml_doc)
                                transformed_tree = str(transformed_tree).replace("mml:", "")
                                mathml = str(transformed_tree)
                                if eq!=2:
                                    xml=f'<kwd-group>{mathml}</kwd-group>'
                                    eq=2
                                else:       
                                    xml=f'<kwd-group>{mathml}</kwd-group>'
                                stri = run.text

                                if values[1]!=stri:
                                    values=values[1:]
                                    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
                                    math_xml = para._element.findall('.//m:oMath', namespaces = ns)
                                    if len(math_xml) > math_count:
                                        cur_math = math_xml[math_count]
                                        math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                                        math_count = math_count + 1
                                        from lxml import etree
                                        xslt_file = "config/omml2mml.xsl"
                                        xslt_doc = etree.parse(xslt_file)
                                        transformer = etree.XSLT(xslt_doc)
                                        xml_doc = etree.fromstring(math_str)
                                        transformed_tree = transformer(xml_doc)
                                        transformed_tree = str(transformed_tree).replace("mml:", "")
                                        mathml = str(transformed_tree)
                                        if eq!=2:
                                            xml=f'<kwd-group>{mathml}</kwd-group>'
                                            eq=2
                                        else:       
                                            xml=f'<kwd-group>{mathml}</kwd-group>'
                                try:    
                                    if values[1]==stri:
                                        values=values[1:]
                                except:
                                    pass


                if len(run.text)==0:
                    pass
                else:
                    values=values[1:]
            
            except:
                pass 

        #Convert the run text in xml
        xmlstr = str(run._element.xml)
        my_namespaces = dict([node for _, node in ElementTree.iterparse(StringIO(xmlstr), events=['start-ns'])])
        ro = ET.fromstring(xmlstr)
        #print(xmlstr)
        #Check if the run contain an image
        if 'pic:pic' in xmlstr:
            print(xmlstr)
            for pic in ro.findall('.//pic:pic', my_namespaces):
                #Extract the image data if it exists
                blip_elem = pic.find(".//a:blip", my_namespaces)
                if blip_elem is not None:
                    embed_attr = blip_elem.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                    rel = doc.part.rels[embed_attr]
                    image_path = rel.target_part.blob
                
                    #Find the image width and height from the XML
                    cx = pic.find(".//a:xfrm/a:ext", my_namespaces).get('cx')
                    cy = pic.find(".//a:xfrm/a:ext", my_namespaces).get('cy')
                    width = int(cx) / 914400 * 96  
                    height = int(cy) / 914400 * 96  

                    #Encode the image
                    encoded_image = base64.b64encode(image_path).decode('utf-8')
                    
                    #Construct HTML for the image
                    xml_text += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_413-fig-1.tif"></graphic>'

        try:
            #Find the hyperlink
            a=2
            if para.hyperlinks:  
                if siva[0]=="<":
                    print(run.text)
                    a=1
                    siva=siva[1:]
                if len(p)>1:
                    siva=siva[1:]
        except:
            print("link")

        #hyperlink
        if a==1:   
            try:
                # Handle superscript text
                xml_text+=f'<link>{text[0]}</link>'
                text=text[1:]
                address=address[1:]
                font=font[1:]   #Remove the first element of the list
            except:
                print("link")

        if "keyword" in run.text.lower():
            continue

        if all_bold:
            xml_text+=f'{run.text}</title>'
            return xml_text

        if fig:
            figure=run.text
            fig_text=""
            figure=figure.split(".")
            for i in range(len(figure)):
                if i==0:
                    pass
                elif i==1:
                    fig_text=figure[0]+figure[1]
                    xml_text+=f'<label>{fig_text}</label><caption>'
                elif figure[i]!="":
                    fig_text=figure[i]
                    xml_text+=f'<title>{fig_text}</title>'
            fig=False
            xml_text+=f'</caption></fig>'
            return xml_text

        if table_title:
            table_text=run.text
            table_text=table_text.split(":")
            for i in range(len(table_text)):
                if i==0:
                    xml_text+=f'<label>{table_text[i]}</label><caption>'
                else:
                    xml_text+=f'<title>{table_text[i]}'
            table_title=False
            table_caption=True
            continue
            
        
        # Check for formatting properties and create corresponding XML elements
        if run.font.superscript:
            # Handle superscript text
            xml_text+=f'<sup>{run.text}</sup>'
        elif run.font.subscript:
            # Handle subscript text
            xml_text+=f'<sub>{run.text}</sub>'
        elif run.font.italic:
            # Handle italic text
            xml_text+=f'<italic>{run.text}</italic>'
        elif run.font.underline:
            # Handle underlined text
            xml_text+=f'<under>{run.text}</under>'
        elif para.style.name.startswith("Heading 2"):  
            xml_text+=f'<article-title>{para.text}</article-title></title-group>'
        elif kwd:
            key_text+=run.text
                
        else:
            # Default case (no special formatting)
            xml_text+=f'{run.text}'

    if table_caption:
        xml_text+=f'</title></caption>'
        table_caption=False

    if key_text:
        key=key_text.split(",")
        for a in key:
            if a!="":
                a=a.strip()
                xml_text+=f'<kwd>{a}</kwd>'


    """if para.hyperlinks and len(text)!=0:
        # Handle superscript text
        run_elem = etree.Element("email")
        run_elem.text = text[0]
        para_elem.append(run_elem)"""
    kwd=False

    if para.style.name.startswith("Heading 2"):  
        return xml_text

    elif para.style.name.startswith("figure caption"):  
        xml_text+=f'</fig>'
    
    elif previous_text.lower()=="abstract" :
        xml_text+=f'</p></abstract>'

    elif para.text.lower()=="abstract":
        xml_text+=f''

    elif para.text.lower()=="references":
        xml_text+=f'</title>'

    elif "keyword" in para.text.lower():
        xml_text+=f'</kwd-group>'

    elif para.style.name.startswith("List Paragraph"):  
        xml_text+=f'</p></list-item>'

    elif ref:
        xml_text+=f'</ref>'

    elif para.style.name.startswith("Table Title"):  
        xml_text+=f''

    else:
        xml_text+=f'</p>'

    #print(xml_text)
    if previous_text:
        if para.style.name.startswith("List Paragraph"):
            list_text=True
        previous_text = para.text
    #print(previous_text)

    return xml_text




def table(table,doc):

    """
    Convert a table from a Word document into HTML format.

    Parameters:
        table (Table): The Table object from the Word document.
        doc (Document): The Document object representing the Word document.

    Returns:
        str: The HTML representation of the table.
    """

    #xml=table._element.xml
    #print(xml)

    math_count = 0
    row_count=0
    col_count=0

    # Iterate through each row in the table
    for r, row in enumerate(table.rows):
        row_count+=1

    # Iterate through each row in the table
    for r, row in enumerate(table.rows):
        for c, cell in enumerate(row.cells): 
            col_count += 1
        break

    colgroup_text=""
    for i in range(col_count):
        colgroup_text+="<col align='center'></col>"

    xml_text=f"<alternatives><table><colgroup>{colgroup_text}</colgroup>"

    #Store the span of merged cells
    li = []

    #Find rows in table
    for r, row in enumerate(table.rows):  
        #find the row height
        if row.height is not None:   
            i=1
            h = row.height.inches * 96  #Convert height from inches to pixels            
        else:
            h =25

        if r==0:
            #Initialize table row tag
            xml_text+="<thead><tr align='center'>"
        else:
            #Initialize table row tag
            xml_text+="<tr align='center'>"

        tt=False
        tr=False

        #Find columns in table  
        for c, cell in enumerate(row.cells):   
            #Skip the cell that are part of a merged region
            if (r, c) in li:
                continue
            
            try:
                #Find the rowspan
                rowspan, colspan = 1, 1
                for merge in range(r + 1, len(table.rows)):
                    if table.rows[merge].cells[c].text == cell.text and cell.text!="" :
                        rowspan += 1
                        tt=True
                        li.append((merge,c))
                    else:
                        break

                #Find the columnspan
                for merge in range(c + 1, len(row.cells)):
                    if row.cells[merge].text == cell.text and cell.text!="" :
                        colspan += 1
                        tr=True
                        li.append((r, merge))
                    else:
                        break
            
                #Find the total number of merged cell and append in list for skip the cell
                if tt and tr:
                    oo,pp,rr,cc=r,c,rowspan-1,colspan-1
                    for k in range(rr):
                        th=True
                        for l in range(cc):
                            if th:
                                oo+=1
                                th=False
                            pp+=1
                            li.append((oo, pp))
                tt=False
                tr=False
            except:
                print("table")
                
            # Find the width of the column
            if cell.width is not None:
                w = cell.width.inches * 96  
            else:
                w=0
            
            if r==0:
                if colspan==1 and rowspan==1:
                    #Initialize table data tag
                    xml_text+=f"<th>"
                else:
                    #Initialize table data tag
                    xml_text+=f"<th rowsapn='{rowspan}' colspan='{colspan}'>"
            else:
                if colspan==1 and rowspan==1:
                    #Initialize table data tag
                    xml_text+=f"<td>"
                else:
                    #Initialize table data tag
                    xml_text+=f"<td rowsapn='{rowspan}' colspan='{colspan}'>"
           
            #Iterate through the cell text
            for paragraph in cell.paragraphs:  


                """eq=2
                math_count = 0    #Initialize math count for math equations

                #Convert the pargaraph into xml
                xml=paragraph._element.xml
                root = ET.fromstring(xml)

                #Check where the equation are present in paragraph
                if "<m:oMath" in xml:
                    #print(xml)
                    ns = {
                        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
                    }
                    values = []
                    for elem in root.iter():
                        if elem.tag.endswith("Math"):      #Find math equation text in paragraph
                            text = ""
                            for t_elem in elem.findall(".//m:t", namespaces=ns): 
                                text += t_elem.text if t_elem.text else ""
                            if text!="":
                                values.append(text)
                        if elem.tag.endswith("r"):      #Find normal text in paragraph
                            tex = ""
                            for t_elem in elem.findall(".//w:t", namespaces=ns): 
                                tex += t_elem.text if t_elem.text else ""
                            if tex!="":
                                values.append(tex) 
                    #Paragraph contain only equation
                    if len(values)==1:
                        ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
                        math_xml = paragraph._element.findall('.//m:oMath', namespaces = ns)
                        if len(math_xml) > math_count:
                            cur_math = math_xml[math_count]
                            math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                            math_count = math_count + 1
                            from lxml import etree
                            xslt_file = "config/omml2mml.xsl"
                            xslt_doc = etree.parse(xslt_file)
                            transformer = etree.XSLT(xslt_doc)
                            xml_doc = etree.fromstring(math_str)
                            transformed_tree = transformer(xml_doc)
                            #Print the math equation
                            transformed_tree = str(transformed_tree).replace("mml:", "")
                            mathml = str(transformed_tree)
                            if eq!=2:
                                xml_text += f"<span style='font-size:{eq}pt;color:{color_hex};'>{mathml}</span>"
                                eq=2
                            else:       
                                xml_text += f"<span style='font-size:11pt;color:black;'>{mathml}</span>" """

                #Iterate through the run object
                for run in paragraph.runs:
                    """
                    Iterate through the runs in the cell paragraph and process each run accordingly.

                    Parameters:
                        i (Run): The Run object representing a portion of the cell paragraph text.
                    """

                    """xml = paragraph._element.xml    
                    #Check if the paragraph contains math equations
                    if '<m:oMath' in xml:
                        stri = i.text
                        try:
                            if values[0]!=stri:
                                #Check the length of run object equal to zero
                                if len(i.text) != 0:
                                        ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
                                        math_xml = paragraph._element.findall('.//m:oMath', namespaces = ns)
                                        if len(math_xml) > math_count:
                                            cur_math = math_xml[math_count]
                                            math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                                            math_count = math_count + 1
                                            from lxml import etree
                                            xslt_file = "config/omml2mml.xsl"
                                            xslt_doc = etree.parse(xslt_file)
                                            transformer = etree.XSLT(xslt_doc)
                                            xml_doc = etree.fromstring(math_str)
                                            transformed_tree = transformer(xml_doc)
                                            #Print the math equation
                                            transformed_tree = str(transformed_tree).replace("mml:", "")
                                            mathml = str(transformed_tree)
                                            if eq!=2:
                                                xml_text += f"<span style='font-size:{eq}pt;color:{color_hex};'>{mathml}</span>"
                                                eq=2
                                            else:       
                                                xml_text += f"<span style='font-size:11pt;color:black;'>{mathml}</span>"
                                            stri = i.text

                                            if values[1]!=stri:
                                                    values=values[1:]
                                                    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
                                                    math_xml = paragraph._element.findall('.//m:oMath', namespaces = ns)
                                                    if len(math_xml) > math_count:
                                                        cur_math = math_xml[math_count]
                                                        math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                                                        math_count = math_count + 1
                                                        from lxml import etree
                                                        xslt_file = "config/omml2mml.xsl"
                                                        xslt_doc = etree.parse(xslt_file)
                                                        transformer = etree.XSLT(xslt_doc)
                                                        xml_doc = etree.fromstring(math_str)
                                                        transformed_tree = transformer(xml_doc)
                                                        #Print the math equation
                                                        transformed_tree = str(transformed_tree).replace("mml:", "")
                                                        mathml = str(transformed_tree)
                                                        if eq!=2: 
                                                            xml_text += f"<span style='font-size:{eq}pt;color:{color_hex};'>{mathml}</span>"
                                                            eq=2
                                                        else:       
                                                            xml_text += f"<span style='font-size:11pt;color:black;'>{mathml}</span>"
                                            try:    
                                                if values[1]==stri:
                                                    values=values[1:]
                                            except:
                                                pass


                            if len(i.text)==0:
                                pass
                            else:
                                values=values[1:]
                        except:
                            pass
                    
                    #Convert the run text into xml
                    xmlstr = str(i.element.xml) 
                    my_namespaces = dict([node for _, node in ElementTree.iterparse(StringIO(xmlstr), events=['start-ns'])])
                    root = ET.fromstring(xmlstr)

                    #Check if the run contain an image
                    if 'pic:pic' in xmlstr:
                        for pic in root.findall('.//pic:pic', my_namespaces):
                            #Extract the image data if it exists
                            blip_elem = pic.find(".//a:blip", my_namespaces)
                            if blip_elem is not None:
                                embed_attr = blip_elem.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                                rel = doc.part.rels[embed_attr]
                                image_path = rel.target_part.blob

                                #Find the image width and height from the XML
                                cx = pic.find(".//a:xfrm/a:ext", my_namespaces).get('cx')
                                cy = pic.find(".//a:xfrm/a:ext", my_namespaces).get('cy')
                                width = int(cx) / 914400 * 96  
                                height = int(cy) / 914400 * 96  

                                #Encode the image
                                encoded_image = base64.b64encode(image_path).decode('utf-8')
                                #Construct HTML for the image
                                xml_text += f"<img src='data:image/png;base64,{encoded_image}' width='{width}px' height='{height}px'/>"
                        
                    """

                    if "keyword" in run.text.lower():
                        continue
                    
                    # Check for formatting properties and create corresponding XML elements
                    if run.font.superscript:
                        # Handle superscript text
                        xml_text+=f'<sup>{run.text}</sup>'
                    elif run.font.subscript:
                        # Handle subscript text
                        xml_text+=f'<sub>{run.text}</sub>'
                    elif run.font.italic:
                        # Handle italic text
                        xml_text+=f'<italic>{run.text}</italic>'
                    elif run.font.underline:
                        # Handle underlined text
                        xml_text+=f'<under>{run.text}</under>'
                    else:
                        # Default case (no special formatting)
                        xml_text+=f'{run.text}'


            #Close the td,tr,table tag
            xml_text+=f"</td>"

        if r==0:
            xml_text += "</tr></thead><tbody>"
            thead=False
        else:
            xml_text+="</tr>"
            
    xml_text += "</tbody></table></alternatives></table-wrap>"
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
    print("jkiuy")
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
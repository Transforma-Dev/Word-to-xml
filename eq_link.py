#Import nesseccary packages
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from io import StringIO
import base64    

#Define function to find the boxed text in the document
def txbox(root):
    box_text=''
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for elem in root.iter():
        if elem.tag.endswith("txbx"):  # Check if the element is a textbox
            text_box = elem.find(".//w:txbxContent", namespaces=ns)  # Check if it contains a text box content
            if text_box is not None:
                for p_elem in text_box.findall(".//w:p", namespaces=ns):  # Find all paragraph elements inside the text box
                    for r_elem in p_elem.findall(".//w:r", namespaces=ns):  # Find all run elements inside the paragraph
                        text = ""
                        for t_elem in r_elem.findall(".//w:t", namespaces=ns):  # Find all text elements inside the run
                            text += t_elem.text if t_elem.text else ""
                        bold = r_elem.find(".//w:b", namespaces=ns)  # Look for bold property inside the run
                        if bold is not None:
                            box_text += f"{text}:"
                        else:
                                box_text += f'{text}'
    return box_text

#Define function to find the equation in the document
def eq(root,xml_text,para,math_count):
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
    }
    values = []     #Define the empty list for store the equation paragraph
    for elem in root.iter():
        if elem.tag.endswith("Math"):     #Find math equation text in paragraph
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
    #If the paragraph contain only one equation.
    if len(values)==1:
        #Call function to print equation
        xml_text,math_count = print_equation(xml_text,para,math_count)

    return values,xml_text,math_count

#Define the function to find the para.run equation in document
def run_eq(root,xml_text,para,run,values,math_count):
    stri = run.text
    try:
        if values[0]!=stri:
            #Check the length of run object equal to zero
            if len(run.text) != 0:
                #Call function to print equation
                xml_text,math_count = print_equation(xml_text,para,math_count)
                stri = run.text

                if values[1]!=stri:
                    values=values[1:]
                    #Call function to print equation
                    xml_text,math_count = print_equation(xml_text,para,math_count)
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

    return values,xml_text,math_count

#Define function to print the equation in correct position
def print_equation(xml_text,para,math_count):
    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
    math_xml = para._element.findall('.//m:oMath', namespaces = ns)     #Count mathml tag in paragraph
    if len(math_xml) > math_count:
        cur_math = math_xml[math_count]
        math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
        math_count = math_count + 1
        math_count = math_count + 1
        from lxml import etree    #Change omml to mml format
        xslt_file = "config/omml2mml.xsl"
        xslt_doc = etree.parse(xslt_file)
        transformer = etree.XSLT(xslt_doc)
        xml_doc = etree.fromstring(math_str)
        transformed_tree = transformer(xml_doc)
        transformed_tree = str(transformed_tree).replace("mml:", "")
        mathml =f'{str(transformed_tree)}'
        #Print the equation
        xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
        
    return xml_text,math_count

#Define the function to find the hyperlinks in the paragraph
def hyper(root,para):
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

    return siva,text,address,font,p

#Define function to print the hyperlink text
def print_hyper(run,para,siva,p,xml_text,text,address,font):
    try:
        #Find the hyperlink in paragraph
        a=2
        if para.hyperlinks:  
            if siva[0]=="<":
                a=1
                siva=siva[1:]
            if len(siva)>1:
                siva=siva[1:]
    except Exception as e:
        print(f"An error occurred: {e}")

    #hyperlink paragraph
    if a==1:   
        try:
            #Handle hyperlink in run.text
            xml_text+=f'<link>{text[0]}</link>'
            text=text[1:]
            address=address[1:]
            font=font[1:]   #Remove the first element of the list
        except:
            pass

    return siva,p,xml_text,text,address,font

#Define the function to find the inline image in the document
def inline_image(doc,doc_filename,file_name,xmlstr,variables,xml_text):
    my_namespaces = dict([node for _, node in ElementTree.iterparse(StringIO(xmlstr), events=['start-ns'])])
    ro = ET.fromstring(xmlstr)
    
    for pic in ro.findall('.//pic:pic', my_namespaces):
        #Find cNvPr in pic:pic for find image id
        cNvPr = pic.find('.//pic:cNvPr',my_namespaces)
        id_attribute = cNvPr.get("id")
        
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

            # Save the image to a file
            folder = f'{doc_filename}-fig-{variables["image_count"]}.jpg'  # You can use any folder format you prefer
            filenames = f'{file_name}-fig-{variables["image_count"]}.jpg'  # You can use any filename format you prefer
            variables["image_count"]+=1
            with open(folder, 'wb') as f:
                f.write(image_path)

            if variables["table_title"]==True:
                #Construct HTML for the image
                xml_text += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/>'
            else:
                #Construct HTML for the image
                variables["images_path"] += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/>'
                variables["image_find"]=True

    return xml_text
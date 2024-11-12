#Import nesseccary packages
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from lxml import etree
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from io import StringIO
import base64    
import re

#Define function to find the boxed text in the document
def txbox(root,file_name,variables):
    box_text=''
    # ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    # for elem in root.iter():
    #     if elem.tag.endswith("txbx"):  # Check if the element is a textbox
    #         text_box = elem.find(".//w:txbxContent", namespaces=ns)  # Check if it contains a text box content
    #         if text_box is not None:
    #             for p_elem in text_box.findall(".//w:p", namespaces=ns):  # Find all paragraph elements inside the text box
    #                 for r_elem in p_elem.findall(".//w:r", namespaces=ns):  # Find all run elements inside the paragraph
    #                     text = ""
    #                     for t_elem in r_elem.findall(".//w:t", namespaces=ns):  # Find all text elements inside the run
    #                         text += t_elem.text if t_elem.text else ""
    #                     bold = r_elem.find(".//w:b", namespaces=ns)  # Look for bold property inside the run
    #                     if bold is not None:
    #                         box_text += f"{text}:"
    #                     else:
    #                         box_text += f'{text}'
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
        'mml': 'http://www.w3.org/1998/Math/MathML' 
    }
    
    for elem in root.iter():
        math_count = 0
        if elem.tag.endswith("txbx"):  # Check if the element is a textbox
            text_box = elem.find(".//w:txbxContent", namespaces=ns)  # Check if it contains a text box content
            if text_box is not None:
                box_text = ""
                for sub_elem in text_box.iter():
                    # if sub_elem.tag.endswith("oMath"):  # Find math equation text in paragraph

                    if sub_elem.tag.endswith("r"):  # Find normal text in paragraph
                        text = ""
                        for t_elem in sub_elem.findall(".//w:t", namespaces=ns):
                            text = t_elem.text if t_elem.text else ""
                        bold = sub_elem.find(".//w:b", namespaces=ns)  # Look for bold property inside the run
                        if bold is not None and text:
                            box_text += f"{text}:"
                        else:
                            box_text += f'{text}'
                    if sub_elem.tag.endswith("oMath"):
                        math_xml = elem.findall('.//m:oMath', namespaces=ns)  # Find all OMML tags in paragraph
                        # print(math_xml)
                        if len(math_xml) > math_count:
                            cur_math = math_xml[math_count]
                            math_str = str(ET.tostring(cur_math, method='xml', encoding="unicode"))
                            math_count = math_count + 1
                            # Transform OMML to MML
                            xslt_file = "config/omml2mml.xsl"
                            xslt_doc = etree.parse(xslt_file)
                            transformer = etree.XSLT(xslt_doc)
                            xml_doc = etree.fromstring(math_str)
                            transformed_tree = transformer(xml_doc)
                            transformed_tree = str(transformed_tree).replace("mml:", "")
                            mathml = f'{str(transformed_tree)}'
                            #Filename with equation
                            filenames = f'{file_name}-eqn-{variables["eq_count"]}.tif'  # You can use any filename format you prefer
                            variables["eq_count"]+=1
                            box_text+=f'<inline-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/><tex-math>{mathml}</tex-math></alternatives></inline-formula>'
    
    return box_text

#Define function to find the boxed text in the document
def sq_text(root,file_name,variables):
    box_text = ''
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
        'mml': 'http://www.w3.org/1998/Math/MathML' 
    }
    
    for elem in root.iter():
        math_count = 0
        if elem.tag.endswith("p"):  # Check if the element is a textbox
                box_text = ""
                for sub_elem in elem.iter():
                    # if sub_elem.tag.endswith("oMath"):  # Find math equation text in paragraph

                    if sub_elem.tag.endswith("r"):  # Find normal text in paragraph
                        text = ""
                        for t_elem in sub_elem.findall(".//w:t", namespaces=ns):
                            text = t_elem.text if t_elem.text else ""
                        bold = sub_elem.find(".//w:b", namespaces=ns)  # Look for bold property inside the run
                        if bold is not None and text:
                            box_text += f"{text}:"
                        else:
                            box_text += f'{text}'
                    if sub_elem.tag.endswith("oMath"):
                        math_xml = elem.findall('.//m:oMath', namespaces=ns)  # Find all OMML tags in paragraph
                        # print(math_xml)
                        if len(math_xml) > math_count:
                            cur_math = math_xml[math_count]
                            math_str = str(ET.tostring(cur_math, method='xml', encoding="unicode"))
                            math_count = math_count + 1
                            # Transform OMML to MML
                            xslt_file = "config/omml2mml.xsl"
                            xslt_doc = etree.parse(xslt_file)
                            transformer = etree.XSLT(xslt_doc)
                            xml_doc = etree.fromstring(math_str)
                            transformed_tree = transformer(xml_doc)
                            transformed_tree = str(transformed_tree).replace("mml:", "")
                            mathml = f'{str(transformed_tree)}'
                            #Filename with equation
                            filenames = f'{file_name}-eqn-{variables["eq_count"]}.tif'  # You can use any filename format you prefer
                            variables["eq_count"]+=1
                            box_text+=f'<inline-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/><tex-math>{mathml}</tex-math></alternatives></inline-formula>'
                            
    return box_text

#Define function to find the equation in the document
def eq(root,xml_text,para,math_count,file_name,variables):
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
        xml_text,math_count = print_equation(xml_text,para,math_count,file_name,variables)

    return values,xml_text,math_count

#Define the function to find the para.run equation in document
def run_eq(root,xml_text,para,run,values,math_count,file_name,variables):
    stri = run.text
    try:
        
        if values[0]!=stri:
            if values[0] == "[":
                num = 0
                text = ''
                for i in values:
                    num+=1
                    text += i
                    if i=="]":
                        break
                xml_text += text
                values = values[num:]
                
            else:
                #Check the length of run object equal to zero
                if len(run.text) != 0:
                    #Call function to print equation
                    xml_text,math_count = print_equation(xml_text,para,math_count,file_name,variables)
                    stri = run.text

                    if values[1]!=stri:
                        values=values[1:]
                        #Call function to print equation
                        xml_text,math_count = print_equation(xml_text,para,math_count,file_name,variables)
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
def print_equation(xml_text,para,math_count,file_name,variables):
    # print("plo")
    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
    math_xml = para._element.findall('.//m:oMath', namespaces = ns)     #Count mathml tag in paragraph
    if len(math_xml) > math_count:
        cur_math = math_xml[math_count]
        math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
        math_count = math_count + 1
        from lxml import etree    #Change omml to mml format
        xslt_file = "config/omml2mml.xsl"
        xslt_doc = etree.parse(xslt_file)
        transformer = etree.XSLT(xslt_doc)
        xml_doc = etree.fromstring(math_str)
        transformed_tree = transformer(xml_doc)
        transformed_tree = str(transformed_tree).replace("mml:", "")
        
        # xslt_file = "config/xsl_yarosh/mmltex.xsl"
        # dom = etree.fromstring(transformed_tree)
        # xslt = etree.parse(xslt_file)
        # transform = etree.XSLT(xslt)
        # transformed_tree = transform(dom)
        mathml =f'{str(transformed_tree)}'
        #Filename with equation
        filenames = f'{file_name}-eqn-{variables["eq_count"]}.tif'  # You can use any filename format you prefer
        variables["eq_count"]+=1
        #Print the equation
        xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
        
    return xml_text,math_count

#Define the function to find the hyperlinks in the paragraph
def hyper(root,para):
    # print(para.text)
    # if not para.text.strip() or re.match(r'^\d', para.text.strip()):
    #     print(para.text)
    ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"
        }
    siva = []
    # print(root)
    for elem in root.iter():
        if elem.tag.endswith("r"):      #Find normal text in paragraph
            tex = ""
            for t_elem in elem.findall(".//w:t", namespaces=ns): 
                if t_elem.text is not None:
                    tex += t_elem.text if t_elem.text else ""
            if tex!="":
                siva.append(tex) 
    # print(siva)
    #Initialize an empty list to store hyperlink text,address,font size
    text=[]
    address=[]
    font=[]
    p = ''
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
            if len(siva)>1 and "".join(siva[0].split()) == "".join(run.text.split()):
                siva=siva[1:]
            else:
                pass
                # print(run.text,"-=-=-=")
                # print(siva,"====")
                # print(p,"---")
                # print(xml_text)
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
            #Save the image in perticuler folder
            with open(folder, 'wb') as f:
                f.write(image_path)
            #Get the image as base64 value
            # with open(folder, "rb") as f:
            #     base64_content = base64.b64encode(f.read()).decode('utf-8')

            if variables["table_title"]==True:
                #Construct HTML for the image
                xml_text += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/><img src="image/{filenames}" />'
            else:
                #Construct HTML for the image
                variables["images_path"] += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/><img src="image/{filenames}" />'
                variables["image_find"]=True

    return xml_text

#Define function to find fig and table in paragraph nd add xref tag
def add_tag(xml_text):
    #Find fig and add tag
    pattern = r"Figu*r*e*s?\.*\s\d+\w*(?:,\d\w+)*(?:(?: and |-)(?:Figu*r*e*s*\.)*\s*\d+\w*)?"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            if "-" in i:
                xml_tex = i.split()
                xml_1 = xml_tex[1].split("-")
                xml_text = xml_text.replace(i,f"<xref ref-type='fig' rid='fig-{xml_1[0]}'>{xml_tex[0]} {xml_1[0]}</xref>-<xref ref-type='fig' rid='fig-{xml_1[1]}'>{xml_1[1]}</xref>")
            elif " and " in i and "," in i:
                xml_tex = i.split()
                xml_1 = xml_tex[1].split(",")
                for id,j in enumerate(xml_1):
                    if id == 0:
                        rep = f"<xref ref-type='fig' rid='fig-{j}'>{xml_tex[0]} {j}</xref>,"
                    else:
                        rep += f"<xref ref-type='fig' rid='fig-{j}'>{j}</xref>,"
                if rep.endswith(","):
                    rep = rep[:-1]
                xml_text = xml_text.replace(i,f"{rep} {xml_tex[2]} <xref ref-type='fig' rid='fig-{xml_tex[3]}'>{xml_tex[3]}</xref>")
            else:
                if "and" in i:
                    split_t = i.split("and")
                    first = "".join([di if di.isdigit() else "" for di in split_t[0]])
                    end = "".join([di if di.isdigit() else "" for di in split_t[1]])
                    xml_text = xml_text.replace(i,f"<xref ref-type='fig' rid='fig-{first}'>Figs. {first}</xref> and <xref ref-type='fig' rid='fig-{end}'>{end}</xref>")
                else:
                    xml_tex = i.split()
                    xml_text = xml_text.replace(i,f"<xref ref-type='fig' rid='fig-{xml_tex[1]}'>{xml_tex[0]} {xml_tex[1]}</xref>")
    #Find tables and add tag
    pattern = r"Tables*\.*\s\d+:*(?:,\d+|-\d+)*(?: and (?:Tables*)\s*\d+:*)*"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            if "-" in i:
                xml_tex = i.split()
                xml_1 = xml_tex[1].split("-")
                xml_text = xml_text.replace(i,f"<xref ref-type='table' rid='table-{xml_1[0]}'>{xml_tex[0]} {xml_1[0]}</xref>-<xref ref-type='table' rid='table-{xml_1[1]}'>{xml_1[1]}</xref>")
            elif "and" in i:
                xml_tex = i.split("and")
                if "," in xml_tex:
                    xml_1 = xml_tex[0].split(",")
                    xml_1.append(xml_tex[-1])
                    len_xml = len(xml_1)
                    # print(len_xml)
                    for id,j in enumerate(xml_1):
                        if id == 0:
                            rep = f"<xref ref-type='table' rid='table-{j.strip()[-1]}'>Tables {j.strip()[-1]}</xref>,"
                        elif len_xml == id+1:
                            rep = rep[:-1]    
                            rep += f" and <xref ref-type='table' rid='table-{j.strip()[-1]}'>{j.strip()[-1]}</xref>"
                        else:
                            rep += f"<xref ref-type='table' rid='table-{j.strip()[-1]}'>{j.strip()[-1]}</xref>,"
                    xml_text = xml_text.replace(i,f"{rep}")
                else:
                    xml_tex = i.split("and")
                    first = "".join([di for di in xml_tex[0] if di.isdigit()])
                    last = "".join([di for di in xml_tex[1] if di.isdigit()])
                    rep = f"<xref ref-type='table' rid='table-{first}'>Tables {first}</xref> and <xref ref-type='table' rid='table-{last}'>{last}</xref>"
                    xml_text = xml_text.replace(i,f"{rep}")
                # print(xml_text)
            else:
                xml_tex = i.split()
                xml_tex[1] = "".join([di for di in xml_tex[1] if di.isdigit()])
                i = i.replace(":","")
                xml_text = xml_text.replace(i,f"<xref ref-type='table' rid='table-{xml_tex[1]}'>{i}</xref>")
    #Find Eqs and add tag
    pattern = r"Eqs\.\s\(*\d+\s*?[-–]?\s*\d+\)*"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            if "-" in i:
                xml_tex = i.split("Eqs.")
                xml_1 = xml_tex[1].split("-")
                xml_text = xml_text.replace(i,f"<xref ref-type='disp-formula' rid='eqn-{xml_1[0]}'>Eqs. {xml_1[0]}</xref>-<xref ref-type='disp-formula' rid='eqn-{xml_1[1]}'>{xml_1[1]}</xref>")
            # print(no2)
            # xml_text = xml_text.replace(i,f"<xref ref-type='disp-formula' rid='eqn-{no1}'>{xml_tex[0]})</xref><xref ref-type='disp-formula' rid='eqn-{no2}'>({xml_tex[1]}</xref>")
            
    #Find Eqs and add tag
    pattern = r"Eq\.\s*\(*\d+\d*\)*"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        no1 = ""
        for i in match:
            if "(" in i or ")" in i:
                for j in i:
                    if j.isdigit():
                        no1 = 1
                xml_text = xml_text.replace(i,f"<xref ref-type='disp-formula' rid='eqn-{no1}'>{match[0]}</xref>")
            else:
                for j in i:
                    if j.isdigit():
                        no1 += str(j)
                replace = i.replace(no1,"("+no1+")")
                xml_text = xml_text.replace(i,f"<xref ref-type='disp-formula' rid='eqn-{no1}'>{replace}</xref>")

    #Find Section and add tag
    pattern = r"Section\s\d\d*"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            for j in match[0]:
                if j.isdigit():
                    no1 = 1
            xml_text = xml_text.replace(i,f"<xref ref-type='sec' rid='s-{no1}'>{match[0]}</xref>")

    #Find Formula and add tag
    pattern = r"Formula\s\(*\d\d*\)*"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            for j in match[0]:
                if j.isdigit():
                    no1 = 1
            xml_text = xml_text.replace(i,f"<xref ref-type='formula' rid='for-{no1}'>{match[0]}</xref>")

    #Find and add tag
    pattern = r"Appendix"
    match = re.findall(pattern, xml_text,re.IGNORECASE)
    if match:
        match = set(match)
        match = list(match)
        for i in match:
            xml_text = xml_text.replace(i,f"<xref ref-type='appendix' rid='app'>{match[0]}</xref>")

    return xml_text

#Define function to find the reference number in paragraph
def add_ref_tag(xml,variables):
    xml = xml.split("<ref-list")
    
    if re.findall(r'\[\d+\]', xml[0]):   #Find the number inside the square bracket
        # print(xml)
        p_pattern = r'(?:\[\d+\]\s*,\s*)+\[\d+\]'
        matchs = re.findall(p_pattern, xml[0],re.IGNORECASE)
        if matchs:
            # print(matchs)
            for match in matchs:
                sp = match.split(",")
                if len(sp) == 2:
                    first = sp[0].strip().replace("[","").replace("]","")
                    last = sp[-1].strip().replace("[","").replace("]","")
                    add_xref = f'[<xref ref-type="bibr" rid="ref-{first}">{first}</xref>,<xref ref-type="bibr" rid="ref-{last}">{last}</xref>]'
                    
                else:
                    first = sp[0].strip().replace("[","").replace("]","")
                    last = sp[-1].strip().replace("[","").replace("]","")
                    add_xref = f'[<xref ref-type="bibr" rid="ref-{first}">{first}</xref>-<xref ref-type="bibr" rid="ref-{last}">{last}</xref>]'
                xml[0] = xml[0].replace(match, add_xref)
                # print(xml[0])

        parentheses_text = re.findall(r'\[(.*?)\]',xml[0])
        # print(parentheses_text)
        for num in parentheses_text:
            if not "close" in num and not ">" in num and not "mask" in num:
                # print(num,"---")
                if num.isdigit() or "," in num or "-" in num and "xref" not in num:
                    # check_digit = False

                    if "-" in num:
                        # Split the num by commas
                        split_i = num.split("-")
                    else:
                        split_i = num.split(",")

                    #Check digit or not
                    if "," in num:
                            # print(num)
                        # try:
                            if len(split_i) == 2:
                                add_xref = f'[<xref ref-type="bibr" rid="ref-{split_i[0]}">{split_i[0]}</xref>,<xref ref-type="bibr" rid="ref-{split_i[1]}">{split_i[1]}</xref>]'
                            else:
                                first = split_i[0].strip().replace("[","").replace("]","")
                                last = split_i[-1].strip().replace("[","").replace("]","")
                                check = 0
                                for ea in split_i:
                                    if ea.strip().isdigit():
                                        check += 1
                                if len(split_i) == check:
                                    # print(split_i)
                                    for id,each in enumerate(split_i):
                                        if int(each) == int(first):
                                            order_num = True
                                            first = int(first) + 1
                                        else:
                                            order_num =False
                                else:
                                    order_num = False
                                if order_num:
                                    add_xref = f'[<xref ref-type="bibr" rid="ref-{first}">{first}</xref>-<xref ref-type="bibr" rid="ref-{last}">{last}</xref>]'
                                else:
                                    add_xref = '['
                                    for i, ref in enumerate(split_i):
                                        # Add xref tags to each reference
                                        add_xref += f'<xref ref-type="bibr" rid="ref-{ref.strip()}">{ref.strip()}</xref>'
                                        # Add comma separator if not the last reference
                                        if i < len(split_i) - 1:
                                            add_xref += ','
                                    # Close the num
                                    add_xref += ']'
                            # print(add_xref,"---")
                            # print(f"[{num}]","---")
                            xml[0] = xml[0].replace(f"[{num}]", add_xref)
                        # except Exception as e:
                        #     print("Error in add_xref_tag in eq_link", e)

                    elif "-" in num:
                        add_xref = f"[<xref ref-type='bibr' rid='ref-{split_i[0]}'>{split_i[0]}</xref>-<xref ref-type='bibr' rid='ref-{split_i[1]}'>{split_i[1]}</xref>]"
                        # print(add_xref)
                        # print(f"[{num}]")
                        xml[0] = xml[0].replace(f"[{num}]", add_xref)

                    else:
                        #Initialize the replacement string
                        add_xref = '['
                        for i, ref in enumerate(split_i):
                            # Add xref tags to each reference
                            add_xref += f'<xref ref-type="bibr" rid="ref-{ref.strip()}">{ref.strip()}</xref>'
                            # Add comma separator if not the last reference
                            if i < len(split_i) - 1:
                                add_xref += ','
                        # Close the num
                        add_xref += ']'
                        # Replace the original num with the new one in the XML
                        xml[0] = xml[0].replace(f'[{num}]', add_xref)

    else:
        #Find author name and year present in xml
        for index,i in enumerate(variables["ref_text_link"]):
            name = i.split(",")
            if len(name)>=2:
                year = name[1].replace("(","").replace(")","")
                pattern = rf'{re.escape(name[0].strip())}\,*\s*\(*{re.escape(year.strip())}'
                match = re.findall(pattern, xml[0])
                #Save the matched text and index in variable
                for j in match:
                    variables["ref_link_save"].append((j,index))

        #Remove duplicates
        variables["ref_link_save"] = list(set(variables["ref_link_save"]))

        #Replace refereance text in xml
        for j,index in variables["ref_link_save"]:
            add_xref = f'<xref ref-type="bibr" rid="ref-{index+1}">{j}</xref>'
            xml[0] = xml[0].replace(j,add_xref)

        # for i in variables["ref_text_link"]:
        #     # print(i)
        #     for j in variables["ref_link_save"]:
        #         if i in j:
        #             # print(i)
        #             # print(j)
        #             xml[0] = xml[0].replace(i,j)
    
    xml=xml[0]+"<ref-list"+xml[1]
    # print(xml)
    return xml
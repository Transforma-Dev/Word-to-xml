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
import unicodedata
from anyascii import anyascii

previous_text = ""  #Stroe a previous paragraph text
kwd=False       #Find the keyword in document
para_count=1    #Find the heading and author in document
table_no=1      #Find the no of table
sec_1=1   
sec_2=1
sec_3=1   #Find the first section of heading 1 ,heading 2,heading 3
inner_3_id=1    #Find no of heading 3 in one section
sec_3_id=1
list_end=False  #Close the list
list_count=1
fig=False   #Find figure caption
fig_caption=1   #Find the figure caption number
ref=False   #Find the reference text
table_title=False   #Find table title text
table_caption=False
aff_tag=True    #Find text between author tag and" corresponding author" text
images_path=""   #Store the image path
sec_1_id=1  #Find Section 1 id
secid=0
sec_2_id=1  #Find section 2 id
image_next_para=False   #Fin the image next para figure caption
image_find=False
back_start=""   #Start the back tag
ref_id=1    #Put reference id
copyright_state=""  #Find the copryrights statement
aff_id=1    #Find number of aff tags
image_count=1   #Find number of image
abbre=False     #Find abbrevation content

#Define the function for convert a paragraph from word document
def paragraph(para,doc,doc_filename):
    
    #Define the global variables
    global previous_text,kwd,sec_1,list_count,ref,fig,fig_caption,abbre,image_find,table_title,table_caption,ref_id,back_start,copyright_state,images_path,image_count,para_count,aff_tag,sec_3,sec_2,image_next_para,list_end
    #Store all text in xml_text
    xml_text=""
    key_text="" #Store keyword text
    aff_text=""    #Find aff text

    #Remove space between start and end of the string
    space_strip=para.text.strip() 

    #Split the filename in folder path
    file_name = os.path.basename(doc_filename)
    journal=file_name.split("_")
    if "EJ-EDU" in journal:
        journal_title="European Journal of Education and Pedagogy"
        issn_no="2736-4534"
        publisher_name="European Open Science"
        publisher_loc="UK"
        article_id="10.24018/ejedu.2024.1.1."
    elif "EJ-GEO" in journal:
        journal_title="European Journal of Environment and Earth Sciences"
        issn_no="2684-446X"
        publisher_name="European Open Science"
        publisher_loc="UK"
        article_id="10.24018/ejgeo.2024.1.1."
    elif "EJ-MATH" in journal:
        journal_title="European Journal of Mathematics and Statistics"
        issn_no="2736-5484"
        publisher_name="European Open Science"
        publisher_loc="UK"
        article_id="10.24018/ejmath.2023.1.1."
    elif "EJ-MED" in journal:
        journal_title="European Journal of Medical and Health Sciences"
        issn_no="2593-8339"
        publisher_name="European Open Science"
        publisher_loc="UK"
        article_id="10.24018/ejmed.2024.1.1."
    elif "Phyton" in journal:
        journal_title="Phyton-International Journal of Experimental Botany"
        issn_no="1851-5657"
        publisher_name="Tech Science Press"
        publisher_loc="USA"
        article_id="10.32604/phyton.2024."
    elif "EJ-SOCIAL" in journal:
        journal_title="European Journal of Humanities and Social Sciences"
        issn_no="2736-5522"
        publisher_name="European Open Science"
        publisher_loc="UK"
        article_id="10.24018/ejsocial.2024.1.1."
    elif "peerj" in journal[0]:
        journal_title="PeerJ"
        issn_no="2167-8359"
        publisher_name="PeerJ Inc."
        publisher_loc="San Diego, USA"
        article_id="10.7717/peerj."
    elif "BIOCELL" in journal:
        journal_title="BIOCELL"
        issn_no="1667-5746"
        publisher_name="Tech Science Press"
        publisher_loc="USA"
        article_id="10.32604/biocell.2024."
    elif "CMC" in journal:
        journal_title="Computers, Materials &#x0026; Continua"
        issn_no="1546-2226"
        publisher_name="Tech Science Press"
        publisher_loc="USA"
        article_id="10.32604/cmc.2024."
    elif "Po" in journal:
        journal_title="Psycho-Oncologie"
        issn_no="1778-3798"    
        publisher_name="Tech Science Press"
        publisher_loc="USA"    
        article_id="10.3166/po.2024."
    filename = f"{file_name}.pdf"

    if len(journal)==1:
        journal=file_name.split("-")
        numbers_only = re.findall(r'\d+',journal[1])
    elif len(journal)==3:
        journal=journal[1:]
        numbers_only = re.findall(r'\d+',journal[-1])
    else:
        numbers_only = re.findall(r'\d+',journal[-1])
    
    #Find the all bold paragraph
    all_bold = all(run.bold for run in para.runs)

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
        #If the paragraph contain only equation.
        if len(values)==1:
            ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math', "mml": "http://www.w3.org/1998/Math/MathML"}
            math_xml = para._element.findall('.//m:oMath', namespaces = ns)
            if len(math_xml) > math_count:
                cur_math = math_xml[math_count]
                math_str = str(ElementTree.tostring(cur_math, method='xml', encoding="unicode"))
                math_count = math_count + 1
                math_count = math_count + 1
                from lxml import etree
                xslt_file = "config/omml2mml.xsl"
                xslt_doc = etree.parse(xslt_file)
                transformer = etree.XSLT(xslt_doc)
                xml_doc = etree.fromstring(math_str)
                transformed_tree = transformer(xml_doc)
                transformed_tree = str(transformed_tree).replace("mml:", "")
                mathml =f'{str(transformed_tree)}'
                if eq!=2:
                    xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                    eq=2
                else:       
                    xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'

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
                                mathml =f'{str(transformed_tree)}'
                                if eq!=2:
                                    xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                    eq=2
                                else:       
                                    xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
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
                                        mathml =f'{str(transformed_tree)}'
                                        if eq!=2:
                                            xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                            eq=2
                                        else:       
                                            xml_text+=f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
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

        #Check if the run contain an image
        if 'pic:pic' in xmlstr:
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
                    folder = f"{doc_filename}-fig-{image_count}.jpg"  # You can use any folder format you prefer
                    filenames = f"{file_name}-fig-{image_count}.jpg"  # You can use any filename format you prefer
                    image_count+=1
                    with open(folder, 'wb') as f:
                        f.write(image_path)
                    
                    #Construct HTML for the image
                    images_path += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/>'
                    image_find=True
                  
        try:
            #Find the hyperlink
            a=2
            if para.hyperlinks:  
                if siva[0]=="<":
                    a=1
                    siva=siva[1:]
                if len(p)>1:
                    siva=siva[1:]
        except:
            print("link")

        #hyperlink paragraph
        if a==1:   
            try:
                #Handle hyperlink in run.text
                xml_text+=f'<link>{text[0]}</link>'
                text=text[1:]
                address=address[1:]
                font=font[1:]   #Remove the first element of the list
            except:
                print("link")

        run.text = unidecode(run.text)    #Convert all non-ascii characters to the closest ascii character
        
        run.text=run.text.replace("<","&#60;")
        run.text=run.text.replace("<<","&#60;&#60;")

        #Find superscript text
        if run.font.superscript and len(para.text)!=0:
            xml_text+=f'<sup>{run.text}</sup>'
        #Find subscript text
        elif run.font.subscript and len(para.text)!=0:
            xml_text+=f'<sub>{run.text}</sub>'
        #Find underlined text
        elif run.font.underline and len(para.text)!=0:
            xml_text+=f'<under>{run.text}</under>'
        #Find bold text
        elif run.bold and len(para.text)!=0  and not run.text.isspace():
            xml_text+=f'<bold>{run.text}</bold>'
        else:
            xml_text+=f'{run.text}'


    #Print the link text at end of the paragraph
    if para.hyperlinks and len(text)!=0:
        xml_text+=f'<email>{text[0]}</email>'
   
    #Define the function for find title
    def title(xml_text):
        global para_count
        text=''
        #Replace bold tag to empty
        xml_text=xml_text.replace("<bold>","").replace("</bold>","")
        
        if para_count==2:
            para_count-=1
            
            text=f'{xml_text}'
        else:
            text=f'''<front>
                <journal-meta>
                    <journal-id journal-id-type="pmc">{journal[0]}</journal-id>
                    <journal-id journal-id-type="nlm-ta">{journal[0]}</journal-id>
                    <journal-id journal-id-type="publisher-id">{journal[0]}</journal-id>
                    <journal-title-group>
                        <journal-title>{journal_title}</journal-title>
                    </journal-title-group>
                    <issn pub-type="epub">{issn_no}</issn>
                    <publiher>
                        <publisher-name>{publisher_name}</publisher-name>
                        <publisher-loc>{publisher_loc}</publisher-loc>
                    </publisher>
                </journal-meta>
                <article-meta>
                    <article-id pub-id-type="publisher-id">{numbers_only[0]}</article-id>
                    <article-id pub-id-type="doi">{article_id}{numbers_only[0]}</article-id>
                    <article-categories>
                        <subj-group subj-group-type="heading">
                            <subject>RESEARCH ARTICLE</subject>
                        </subj-group>
                    </article-categories>
                <title-group><article-title>{xml_text}'''
        return text
    #Define function to find author name
    def author_name(xml_text):
        global copyright_state
        author_id=1
        pattern = re.compile(r'<sup>(.*?)</sup>')
        matches = pattern.findall(xml_text)     #Get superscipt tag text
        string = re.sub(pattern, '', xml_text)  #Get non superscript text
        split_string = string.split(",")
        text=f'''</article-title>
                        <alt-title alt-title-type="left-running-head">Amoako and Otchere</alt-title>
                        <alt-title alt-title-type="right-running-head">Inevitability of Politics in Ghana&#x2019;s Curriculum Development</alt-title>
                    </title-group>
                    <contrib-group content-type="authors">'''  
        for i in split_string:
            auth=i.split()
            auth = [value for value in auth if value != ""]
            if author_id==1:
                text+=f'<contrib id="author-{author_id}" contrib-type="author" corresp="yes"><contrib-id contrib-id-type="orcid">https:</contrib-id><name name-style="western"><surname>{auth[-1]}</surname><given-names>'
            else:
                text+=f'<contrib id="author-{author_id}" contrib-type="author"><contrib-id contrib-id-type="orcid">https:</contrib-id><name name-style="western"><surname>{auth[-1]}</surname><given-names>'
            author_id+=1
            copyright_state+=auth[-1]+" and "
            auth=auth[:-1]
            for i in auth:
                text+=f'{i}'
                text+=f' '
            text+=f'</given-names></name>'
            if matches:
                mat=matches[0].split(",")
                matches=matches[1:]
                for j in mat:
                    if j=="*":
                        text+=f'<email>ssss@email.com</email>'
                    else:
                        text+=f'<xref ref-type="aff" rid="aff-{j}">{j}</xref>'
            text+=f'</contrib>'
        return text
    #Define function to find coresponding author
    def corres_author(xml_text):
        xml_text=xml_text.replace("<sup>","<label>").replace("</sup>","</label>").replace("<link>","<email>").replace("</link>","</email>")
        text=f'</contrib-group><author-notes><corresp id="cor1">{xml_text}</corresp></author-notes>'
        return text
    #Define function to find aff text
    def aff_para(xml_text):
        global aff_id
        split_last=xml_text.split(";")
        xml_text=split_last[0]
        text=""
        pattern = re.compile(r'<sup>(.*?)</sup>')
        matches = pattern.findall(xml_text)     #Get superscipt tag text
        string = re.sub(pattern, '', xml_text)  #Get non superscript text
        if "running title:" in para.text.lower():
            return text
        else:
            text=f'<aff id="aff-{aff_id}">'
            run_text=string.split(",")
            if matches:
                text+=f'<label>{matches[0]}</label>'
            runn=run_text
            text+=f'<institution>'
            run_text=run_text[:-1]
            for i in run_text:
                text+=f'{i}'
                text+=f' '
            text+=f'</institution>,<country>{runn[-1]}</country>.'
            text+=f'</aff>' 
            aff_id+=1
        return text
    #Define function to find 
    def abstract(xml_text):
        xml_text = re.sub(r'<bold>.*?abstract:.*?</bold>', '', xml_text,flags=re.IGNORECASE)
        text=f'''<pub-date pub-type="epub" date-type="pub" iso-8601-date="2024-00-00">
                        <day>00</day>
                        <month>00</month>
                        <year>2024</year>
                    </pub-date>
                    <volume>1</volume>
                    <issue>1</issue>
                    <fpage>1</fpage>
                    <lpage>XX</lpage>
                    <history>
                        <date date-type="received">
                            <day>00</day>
                            <month>0</month>
                            <year>2024</year>
                        </date>
                        <date date-type="accepted">
                            <day>00</day>
                            <month>0</month>
                            <year>2024</year>
                        </date>
                    </history>
                    <permissions>
                        <copyright-statement>&#x00A9; 2024 {copyright_state[:-4]}</copyright-statement>
                        <copyright-year>2024</copyright-year>
                        <copyright-holder>{copyright_state[:-4]}</copyright-holder>
                        <license xlink:href="https://creativecommons.org/licenses/by/4.0/">
                            <license-p>This is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original source is cited.</license-p>
                        </license>
                    </permissions>
                    <self-uri content-type="pdf" xlink:href="{filename}"></self-uri><abstract abstract-type="abstract"><p>{xml_text}</p>'''
        return text
    #Define funcion to find keywords
    def keyword_text(xml_text):
        xml_text = re.sub("keywords:", '', xml_text, flags=re.IGNORECASE)
        xml_text= re.sub(r'<bold>.*?</bold>', '', xml_text)
        xml_text=xml_text.replace(":","")
        if ";" in xml_text:
            xml_text=xml_text.split(";")
        else:       
            xml_text=xml_text.split(",")
        text=f'</abstract><kwd-group kwd-group-type="author">'
        for i in xml_text:
            if "keyword" in i.lower():
                pass
            else:
                text+=f'<kwd>{i}</kwd>'
        text+=f'</kwd-group></article-meta></front><body>'
        return text
    #Define function to find Heading
    def heading(xml_text):
        global sec_1,sec_2,sec_3,sec_1_id,sec_2_id,sec_3_id,inner_3_id,secid
        xml_text=xml_text.replace("<bold>","").replace("</bold>","")
        xml_text = re.sub('^[\d.]+', '', xml_text)
        if para.alignment==1 or para.style.name.startswith("Heading 1") or space_strip.lower()=="introduction" or re.search(r'^\d\s.*$', para.text):
            text=f'<sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
            secid=sec_1_id
            sec_1_id+=1
            sec_2=1
            sec_2_id=1
            sec_3=1
        elif para.style.name.startswith("Heading 3") or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text):
            text=f'<sec id="s{secid}_{sec_3_id}_{inner_3_id}"><label>{secid}.{sec_3_id}.{inner_3_id}</label><title>{xml_text}</title>'
            inner_3_id+=1
            sec_3+=1
        elif para.alignment==0 or para.style.name.startswith("Heading 2") or re.search(r'^\d+\..*', para.text):
            text=f'<sec id="s{secid}_{sec_2_id}"><label>{secid}.{sec_2_id}</label><title>{xml_text}</title>'
            sec_3_id=sec_2_id
            sec_2_id+=1
            inner_3_id=1
            sec_3=1
            sec_2+=1
        sec_1+=1
        return text
    #Define function to find sub-heading 
    def sub_heading(xml_text):
        global sec_1,sec_2,sec_3,sec_1_id,sec_2_id,sec_3_id,inner_3_id,secid,back_start
        xml_text=xml_text.replace("<bold>","").replace("</bold>","")
        xml_text = re.sub('^[\d.]+', '', xml_text)
        if para.alignment==1 or para.style.name.startswith("Heading 1") or re.search(r'^\d\s.*$', para.text):
            if "conflict of interest" in para.text.lower() and "back" not in back_start:
                if sec_3>1:
                    text=f'</sec></sec></sec></body><back><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                elif sec_2>1:
                    text=f'</sec></sec></body><back><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                else:
                    text=f'</sec></body><back><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                secid=sec_1_id
                sec_1_id+=1
                sec_2_id=1
                sec_2=1
                back_start+="back"
            else:
                if sec_3>1:
                    text=f'</sec></sec></sec><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                elif sec_2>1:
                    text=f'</sec></sec><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                else:
                    text=f'</sec><sec id="s{sec_1_id}"><label>{sec_1_id}.</label><title>{xml_text}</title>'
                secid=sec_1_id
                sec_1_id+=1
                sec_2_id=1
                sec_2=1
        elif para.style.name.startswith("Heading 3") or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text):
            text=f'</sec><sec id="s{secid}_{sec_3_id}_{inner_3_id}"><label>{secid}.{sec_3_id}.{inner_3_id}</label><title>{xml_text}</title>'
            inner_3_id+=1
        elif para.alignment==0 or para.style.name.startswith("Heading 2") or re.search(r'^\d+\..*', para.text):
            if sec_3>1:
                text=f'</sec></sec><sec id="s{secid}_{sec_2_id}"><label>{secid}.{sec_2_id}</label><title>{xml_text}</title>'
            else:
                text=f'</sec><sec id="s{secid}_{sec_2_id}"><label>{secid}.{sec_2_id}</label><title>{xml_text}</title>'
            sec_3_id=sec_2_id
            sec_2_id+=1
            inner_3_id=1
            sec_3=1
        return text
    #Define function to find the List paragraph
    def list_para(xml_text): 
        global list_count
        if list_count==1:
            text=f'<list list-type="order"><list-item><p>{xml_text}</p></list-item>'
        else:
            text=f'<list-item><p>{xml_text}</p></list-item>'
        list_count+=1
        return text
    #Define function to find the figure caption text
    def image_caption(xml_text):
        global fig_caption,images_path
        xml_text = re.sub(r'<bold>.*?FIGURE.*?</bold>', '', xml_text,flags=re.IGNORECASE)
        path_image=re.findall(r'<graphic[^>]*>', images_path)
        count_graphic=images_path.count("graphic")
        text=""
        figure=xml_text
        for i in range(count_graphic):
            if "<" in figure:
                figure=figure.replace("<","&#60;")
            figure=figure.replace("Figure","").replace(str(fig_caption),"").replace("Fig","").replace(".","")
            if "fig" in para.text.lower():
                text+=f'<fig id="fig-{fig_caption}"><label>Fig.{fig_caption}</label><caption><title>{figure}</title></caption>{path_image[i]}</fig>'
            else:
                text+=f'<fig id="fig-{fig_caption}"><label>Fig.{fig_caption}</label><caption><title></title></caption>{path_image[i]}</fig>'
            fig_caption+=1
        fig=False
        images_path=""
        return text
    #Define function to find the table heading text
    def table_heading(xml_text):
        global table_caption,table_title
        xml_text=xml_text.split(":")
        text=f'<table-wrap id="table-{table_no}"><label>{xml_text[0]}</label><caption><title>{xml_text[1]}</title></caption>'
        return text
    #Define function to find abrevation paragraph
    def abbrevation(xml_text):
        global sec_3,sec_2,sec_1,back_start
        if sec_3>1:
            text=f'</sec></sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title><bold>{xml_text}</bold></title>'
        elif sec_2>1:
            text=f'</sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title><bold>{xml_text}</bold></title>'
        else:
            text=f'</sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title><bold>{xml_text}</bold></title>'
        sec_1=1
        back_start+="back"
        return text
    # Define function to find and Print abbrevation contents
    def abbrev_text(xml_text):
        xml_text=xml_text.split(":")
        text=f'<def-list><def-item><term>{xml_text[0]}</term><def><p>{xml_text[1]}</p></def></def-item></def-list></glossary>'
        return text
    #Define function to find acknowledgment paragraph
    def ack_para(xml_text):
        global back_start,sec_1
        if sec_3>1:
            text=f'</sec></sec></sec></body><back>'
        elif sec_2>1:
            text=f'</sec></sec></body><back>'
        else:
            text=f'</sec></body><back>'
        sec_1=1
        back_start+="back"
        previous_text=para.text
        return text
    #Define function to find acknowledgment text
    def ack_text(xml_text):
        text=f'<ack><p>{xml_text}</p></ack>'
        return text
    #Define function to find reference part
    def reference(xml_text):
        xml_text=xml_text.replace("<bold>","").replace("</bold>","")
        if "back" not in back_start:
            if sec_3>1:
                text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
            elif sec_2>1:
                text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
            else:
                text=f'</sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
            ref=True
        else:
            if sec_3>1:
                text=f'</sec></sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
            elif sec_2>1:
                text=f'</sec></sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
            else:
                text=f'</sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
        return text

    def reference_text(xml_text):
        global ref_id
        text=f'<ref id="ref-{ref_id}">{xml_text}</ref>'
        ref_id+=1
        return text

        
    #Close the heading tag
    if (para_count==1 or (para_count==2 and all_bold)) and len(para.text)!=0:  
        if "doi:" in para.text.lower():
            xml_text=''
            return xml_text
        if "commentary" in para.text.lower():
            xml_text=''
            return xml_text
        if "type:" in para.text.lower():
            xml_text=''
            return xml_text
        if "article" in para.text.lower():
            xml_text=''
            return xml_text

        xml_text=title(xml_text)
        para_count+=1

    #Find authors in word document and change the tag into contrib
    elif (para.style.name.startswith("Authors") or para_count==2) and len(para.text)!=0:
        xml_text = author_name(xml_text)
        para_count+=1

    #Find corresponding author text in paragraph in word document and change the tag into author-notes
    elif ("corresponding author" in para.text.lower() or "e-mail" in para.text.lower()) and len(para.text)!=0:
        aff_tag=False
        xml_text = corres_author(xml_text)

    #Find the next paragraph of abstract paragraph
    elif previous_text.lower()=="abstract"  and len(para.text)!=0:
        xml_text = abstract(xml_text)

    #Find abstract in word document and skip this
    elif para.text.lower()=="abstract" and len(para.text)!=0:
        previous_text=para.text
        xml_text=''
        if aff_tag:
            xml_text+=f'</contrib-group>'
            aff_tag=False
        return xml_text

    #Check the paragraph was starts with abstract text
    elif para.text.strip().lower().startswith("abstract"):
        xml_text = abstract(xml_text)
    
    #Check para.text is keyword then skip them
    elif para.text.lower()=="keywords":
        previous_text=para.text
        return xml_text

    #Check previous text was equal to keyword
    elif previous_text.lower()=="keywords":
        xml_text=keyword_text(xml_text)
        kwd=True

    #Check the paragraph was starts with keyword text
    elif para.text.strip().lower().startswith("keyword") or para.text.strip().lower().startswith("key words"):
        xml_text=keyword_text(xml_text)
        kwd=True

    #Find paragraph between author and mail and apply tag aff
    elif aff_tag and para_count>2 and len(para.text)!=0 and not para.text.isspace():
        xml_text = aff_para(xml_text)

    #Find acknowledgment paragraph in word document and change the tag into ack and p
    elif "acknowledgment" in previous_text.lower() and len(para.text)!=0:
        xml_text = ack_text(xml_text)

    #Find acknowledgment in word document and skip this
    elif  para.text.strip().lower().startswith("acknowledgment"):
        xml_text = ack_para(xml_text)

    #Print abbrevation contents
    elif space_strip.lower()=="abbreviations":
        xml_text = abbrevation(xml_text)
        abbre=True
    
    #Print abbrevation contents
    elif abbre:
        xml_text = abbrev_text(xml_text)
        abbre=False

    #Find references in word document and change the tag into back,ref-list,title
    elif space_strip.lower()=="references" and len(para.text)!=0:
        xml_text = reference(xml_text)
        ref=True

    #Find figure caption in word document and change the tag into fig
    elif (para.style.name.startswith("figure caption") or image_next_para) and len(para.text)!=0:
        xml_text = image_caption(xml_text)
        image_find=False
        image_next_para=False

    #Find table title in word document and change the tag into table-wrap
    elif para.style.name.startswith("Table Title") and len(para.text)!=0:  
        xml_text = table_heading(xml_text)
        table_title=True

    #Find heading in word document and change the tags into sec
    elif (((para.alignment==1 or para.style.name.startswith("Heading 1") or space_strip.lower()=="introduction" or re.search(r'^\d\s.*$', para.text)) and (sec_1==1)) or ((para.alignment==0 or para.style.name.startswith("Heading 2") or re.search(r'^\d+\..*', para.text)) and (sec_2==1)) or ((para.style.name.startswith("Heading 3") or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text)) and sec_3==1)) and len(para.text)!=0:
        xml_text=heading(xml_text)

    #Find heading in word document and change the tags sec
    elif ((para.alignment==1 or para.style.name.startswith("Heading 1") or re.search(r'^\d\s.*$', para.text)) or (para.alignment==0  or para.style.name.startswith("Heading 2") or re.search(r'^\d+\..*', para.text)) or (para.style.name.startswith("Heading 3") or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text))) and len(para.text)!=0:
        xml_text = sub_heading(xml_text)

    #Find List in word document and change the tag into list-item and p
    elif para.style.name.startswith("List Paragraph") and len(para.text)!=0:
        xml_text=list_para(xml_text)
        list_end=True

    #Find reference paragraph in word document and change the tag into ref
    elif ref and para.text!="":
        xml_text = reference_text(xml_text)

    #Close the list
    elif list_end:
        if len(para.text)!=0:
            xml_text=f'</list><p>{xml_text}</p>'
            list_end=False
            list_count=1
        else:
            xml_text+=f'</list>'
            list_end=False
            list_count=1        

    #Else print p tag
    elif len(para.text)!=0:
        xml_text=f'<p>{xml_text}</p>' 

 
    if image_find:
        image_next_para=True

    if len(para.text)!=0:
        previous_text=para.text

    return xml_text




def table(table,doc,doc_filename):

    """
    Convert a table from a Word document into HTML format.

    Parameters:
        table (Table): The Table object from the Word document.
        doc (Document): The Document object representing the Word document.

    Returns:
        str: The HTML representation of the table.
    """

    global table_no,image_count

    math_count = 0
    row_count=0
    col_count=0

    #Find the length of the row
    for r, row in enumerate(table.rows):
        row_count+=1

    #Find the length of the row
    for r, row in enumerate(table.rows):
        for c, cell in enumerate(row.cells): 
            col_count += 1
        break
    #Find the number of col tag in col-group
    colgroup_text=""
    for i in range(col_count):
        colgroup_text+="<col align='center'></col>"
    #Split the filename in folder path
    file_name = os.path.basename(doc_filename)
    filename = f"{file_name}-table-{table_no}.tif"
    if table_title==False:
        xml_text=f'<table-wrap id="table-{table_no}"><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filename}"/><table><colgroup>{colgroup_text}</colgroup>'
    else:
        xml_text=f'<alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="{filename}"/><table><colgroup>{colgroup_text}</colgroup>'

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

        #Present first row in thead tag other present in tbody tag
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
            
            #Present first row in th tag other present in td tag
            if r==0:
                #Check the rowspan and colspan to print in output
                if colspan==1 and rowspan==1:
                    xml_text+=f"<th>"
                elif colspan>1:
                    xml_text+=f"<th colspan='{colspan}'>"
                elif rowspan>1:
                    xml_text+=f"<th rowspan='{rowspan}'>"
                else:
                    xml_text+=f"<th rowsapn='{rowspan}' colspan='{colspan}'>"
            else:
                if colspan==1 and rowspan==1:
                    xml_text+=f"<td>"
                elif colspan>1:
                    xml_text+=f"<td colspan='{colspan}'>"
                elif rowspan>1:
                    xml_text+=f"<td rowspan='{rowspan}'>"
                else:
                    xml_text+=f"<td rowsapn='{rowspan}' colspan='{colspan}'>"
           
            #Iterate through the cell text
            for paragraph in cell.paragraphs:  

                eq=2
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
                                xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                eq=2
                            else:       
                                xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'

                #Iterate through the run object
                for run in paragraph.runs:
                    """
                    Iterate through the runs in the cell paragraph and process each run accordingly.

                    Parameters:
                        i (Run): The Run object representing a portion of the cell paragraph text.
                    """

                    xml = paragraph._element.xml    
                    #Check if the paragraph contains math equations
                    if '<m:oMath' in xml:
                        stri = run.text
                        try:
                            if values[0]!=stri:
                                #Check the length of run object equal to zero
                                if len(run.text) != 0:
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
                                                xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                                eq=2
                                            else:       
                                                xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                            stri = run.text

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
                                                            xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
                                                            eq=2
                                                        else:       
                                                            xml_text += f'<disp-formula><alternatives><graphic mimetype="image" mime-subtype="tif" xlink:href="EJ-GEO_421-eqn-1.tif"/><tex-math>{mathml}</tex-math></alternatives></disp-formula>'
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
                    
                    #Convert the run text into xml
                    xmlstr = str(run.element.xml) 
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

                                 # Save the image to a file
                                folder = f"{doc_filename}-fig-{image_count}.jpg"  # You can use any folder format you prefer
                                filenames = f"{file_name}-fig-{image_count}.jpg"  # You can use any filename format you prefer
                                image_count+=1
                                with open(folder, 'wb') as f:
                                    f.write(image_path)
                    
                                #Construct HTML for the image
                                xml_text += f'<graphic mimetype="image" mime-subtype="tif" xlink:href="{filenames}"/>'

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
            
    xml_text += "</tbody></table></alternatives></table-wrap>"
    table_no+=1
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
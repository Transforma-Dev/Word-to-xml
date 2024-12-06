import re


#Define function to find abrevation paragraph
def abbrevation(xml_text, variables):
    if variables["sec_3"] > 1:
        text = f'</sec></sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
    elif variables["sec_2"] > 1:
        text = f'</sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
    else:
        text = f'</sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
    variables["sec_1"] = 1
    variables["back_start"] += "back"
    
    variables["abbre"] = True

    return text


#Define function to find and Print abbrevation contents
def abbrev_text(xml_text, variables):
    xml_text = xml_text.split(":")
    text = f'<def-list><def-item><term>{xml_text[0]}</term><def><p>{xml_text[1]}</p></def></def-item></def-list></glossary>'

    variables["abbre"] = False

    return text


#Define function to find acknowledgment paragraph
def ack_para(xml_text, variables, para):
    text = ''
    variables["previous_text"] = para.text.strip()

    return text


#Define function to find acknowledgment text
def ack_text(xml_text, variables):
    text = ''
    #Remove the acknowledgement and ':' in string
    xml_text = re.sub(r'<bold>.*?Acknowledgement.*?</bold>|<bold>.*?:.*?</bold>', '', xml_text, flags=re.IGNORECASE)
    xml_text = xml_text.replace(":", "")
    if variables["sec_3"] > 1:
        text = f'</sec></sec></sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
    elif variables["sec_2"] > 1:
        text = f'</sec></sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
    else:
        text = f'</sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
    
    variables["sec_1"] = 1
    variables["sec_2"] = 1
    variables["sec_3"] = 1
    variables["back_start"] += "back"

    return text


#Define function to find the Nomenclature text
def noman(xml_text, variables):
    text = ''
    #Find the contend in resume in TSP_PO_49526.docx
    xml_text = xml_text.replace("<bold>", "").replace("</bold>", "")
    if "resume" in xml_text.lower():
        variables["noman_store"] += f'{xml_text}'
        variables["noman_text"] = True
        return text
    variables["noman_store"] += f'<glossary content-type="abbreviations" id="glossary-1"><title1>{xml_text}</title1><def-list>'

    variables["noman_text"] = True

    return text


#Define function to find the noman paragraph text
def noman_para(xml_text, variables):
    text = ''
    #Find the contend in resume in TSP_PO_49526.docx
    if "resume" in variables["noman_store"].lower():
        xml_text = xml_text.replace("<bold>", "").replace("</bold>", "")
        variables["noman_store"] += f'{xml_text}'

        return text
    i = False

    xml_text = [item.strip() for item in xml_text.split("\t") if item.strip()]

    if len(xml_text) != 1:
        variables["noman_store"] += f'<def-item><term>{xml_text[0]}</term><def><p>{xml_text[1]}</p></def></def-item>'
    else:
        variables["noman_store"] += f'<def-item><def><p>{xml_text[0]}</p></def></def-item>'
    
    return text


#Define function to find funding statement text
def funding_text(xml_text, variables):
    xml_text = xml_text.replace(":", "")
    variables["back_start"] += "fn"
    if xml_text[:10] == "<fn-group>":
        xml_text = xml_text[10:]
        text = f'<fn-group><fn fn-type="other"><p>{xml_text}'    
    elif "<bold>" not in xml_text:
        text = f'{xml_text}'
    else:
        text = f'</p></fn><fn fn-type="other"><p>{xml_text}'
 
    variables["fn_start"] = True

    return text
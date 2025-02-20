import re


#Define function to find abrevation paragraph
def abbrevation(xml_text, variables, logger):
    
    try:
        if variables["sec_3"] > 1:
            text = f'</sec></sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
        elif variables["sec_2"] > 1:
            text = f'</sec></sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
        else:
            text = f'</sec></body><back><glossary content-type="abbreviations" id="glossary-1"><title1><bold>{xml_text}</bold></title1>'
        variables["sec_1"] = 1
        variables["back_start"] += "back"
        
        variables["abbre"] = True
        
        #Success log message
        logger.info(f"Successfully created the abbrevation tag from (abbrevation function) (other_tags.py)-file")
    except Exception as e:
        print(f"Error in (abbrevation function) (other_tags.py)-file {e}")
        #Error log message
        logger.error(f"Error in (abbrevation function) (other_tags.py)-file {e}")

    return text


#Define function to find and Print abbrevation contents
def abbrev_text(xml_text, variables, logger):
    xml_text = xml_text.split(":")
    text = f'<def-list><def-item><term>{xml_text[0]}</term><def><p>{xml_text[1]}</p></def></def-item></def-list></glossary>'

    variables["abbre"] = False

    #Success log message
    logger.info(f"Successfully created the def-item tag from (abbrev_text function) (other_tags.py)-file")
    return text


#Define function to find acknowledgment paragraph
def ack_para(xml_text, variables, para, logger):
    text = ''
    variables["previous_text"] = para.text.strip()

    #Success log message
    logger.info(f"Successfully created the acknowledgement tag from (ack_para function) (other_tags.py)-file")
    return text


#Define function to find acknowledgment text
def ack_text(xml_text, variables, logger):
    text = ''
    
    try:
        #Remove the acknowledgement and ':' in string
        xml_text = re.sub(r'<bold>.*?Acknowledgement.*?</bold>|<bold>.*?:.*?</bold>', '', xml_text, flags=re.IGNORECASE)
        xml_text = xml_text.replace(":", "")
        if "back" in variables["back_start"]:
            text = f'{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
        else:
            if variables["sec_3"] > 1:
                text = f'</sec></sec></sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
            elif variables["sec_2"] > 1:
                text = f'</sec></sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
            else:
                text = f'</sec></body><back>{variables["noman_store"]}<ack><p>{xml_text}</p></ack>'
        
        variables["sec_1"] = variables["sec_2"] = variables["sec_3"] = 1
        variables["back_start"] += "back"
        
        #Success log message
        logger.info(f"Successfully created the acknowledgement tag from (ack_text function) (other_tags.py)-file")
    except Exception as e:
        print(f"Error in (ack_tex function) (other_tags.py)-file {e}")
        #Error log message
        logger.error(f"Error in (ack_text function) (other_tags.py)-file {e}")

    return text


#Define function to find the Nomenclature text
def noman(xml_text, variables, logger):
    text = ''
    
    try:
        #Find the contend in resume in TSP_PO_49526.docx
        xml_text = xml_text.replace("<bold>", "").replace("</bold>", "")
        if "resume" in xml_text.lower():
            variables["noman_store"] += f'{xml_text}'
        else:
            variables["noman_store"] += f'<glossary content-type="abbreviations" id="glossary-1"><title1>{xml_text}</title1><def-list>'
            
        #Success log message
        logger.info(f"Successfully created the noman tag from (noman function) (other_tags.py)-file")
    except Exception as e:
        print(f"Error in (noman function) (other_tags.py)-file {e}")
        #Error log message
        logger.error(f"Error in (noman function) (other_tags.py)-file {e}")

    variables["noman_text"] = True

    return text


#Define function to find the noman paragraph text
def noman_para(xml_text, variables, logger):
    text = ''
    
    try:
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
            
        #Success log message
        logger.info(f"Successfully created the def-item tag from (noman_para function) (other_tags.py)-file")
    except Exception as e:
        print(f"Error in (noman_para function) (other_tags.py)-file {e}")
        #Error log message
        logger.error(f"Error in (noman_para function) (other_tags.py)-file {e}")
    
    return text


#Define function to find funding statement text
def funding_text(xml_text, variables, logger):
    
    try:
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
        
        #Success log message
        logger.info(f"Successfully created the fn tag from (funding_text function) (other_tags.py)-file")
    except Exception as e:
        print()
        #Error log message
        logger.error(f"Error in (funding_text function) (other_tags.py)-file {e}")

    return text
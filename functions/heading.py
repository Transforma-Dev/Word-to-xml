import re


#Define function to find Heading
def heading(para, space_strip, xml_text, variables, logger):

    text = ''
    
    try:
        #Remove bold and italic tag
        xml_text = xml_text.replace("<bold>", "").replace("</bold>", "").replace("<italic>", "").replace("</italic>", "")
        if ".edu." in xml_text:
            return text

        #Determine the heading type based on paragraph alignment, style, or content
        if para.alignment == 1 or re.search(r"Heading\s*1", para.style.name) or space_strip.lower() == "introduction" or re.search(r'(^\d\.*\s|^\w\.*\s+)', para.text) or space_strip.strip().lower().startswith("conflict"):
            xml_text = re.sub('^[\d.\s*]+', '', xml_text)   #Remove numbers before string
            if variables["abs_para"]:
                text = f'</abstract></article-meta></front><body><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
            else:
                text = f'<sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'

            #Update the dictionary variable values
            variables.update(secid = variables["sec_1_id"], sec_1_id = variables["sec_1_id"] + 1, sec_2 = 1, sec_2_id = 1, sec_3 = 1)

        elif re.search(r"Heading\s*3", para.style.name) or re.search(r'^\d+\.\d+\.\d+\s.*$', para.text):
            xml_text = re.sub('^[\d\.\d\.\d\.*\s*]+', '', xml_text)   #Remove numbers before string
            text = f'<sec id="s{variables["secid"]}_{variables["sec_3_id"]}_{variables["inner_3_id"]}"><label>{variables["secid"]}.{variables["sec_3_id"]}.{variables["inner_3_id"]}</label><title1>{xml_text}</title1>'

            #Update the dictionary variable values
            variables["inner_3_id"] += 1
            variables["sec_3"] += 1

        elif para.alignment == 0 or re.search(r"Heading\s*2", para.style.name) or re.search(r'^\d+\..*', para.text):
            xml_text = re.sub('^[\d\.\d\.*\s*]+', '', xml_text)   #Remove numbers before string
            text = f'<sec id="s{variables["secid"]}_{variables["sec_2_id"]}"><label>{variables["secid"]}.{variables["sec_2_id"]}</label><title1>{xml_text}</title1>'

            #Update the dictionary variable values
            variables.update(sec_3_id = variables["sec_2_id"], sec_2_id = variables["sec_2_id"] + 1, inner_3_id = 1, sec_3 = 1, sec_2 = variables["sec_2"] + 1)

        else:
            text = f'<p>{xml_text}</p>'

        variables["sec_1"] += 1
        if variables["noman_text"]:
            variables["noman_store"] += "</def-list></glossary>"

        variables["noman_text"] = False
        
        #Success log message
        logger.info(f"Successfully created the sec tag from (heading function) (heading.py)-file")
    except Exception as e:
        print(f"Error in (heading function) (heading.py)-file {e}")
        #Error log message
        logger.error(f"Error in (heading function) (heading.py)-file {e}")

    return text


#Define function to find sub-heading 
def sub_heading(para, xml_text, variables, space_strip, all_bold, logger):
    text = ''
    
    try:
        if variables["list_end"]:
            text += "</list>"
            variables["list_end"] = False
            variables["list_count"] = 1

        if xml_text.lower().startswith("fig."):
            text += f'<p>{xml_text}</p>'
            return text
        #Remove bold and italic tag
        xml_text = xml_text.replace("<bold>", "").replace("</bold>", "").replace("<italic>", "").replace("</italic>", "")
        
        xml_text = re.sub(r'^[\d.]+|^\w+\.', '', xml_text)
        
        if para.alignment == 1 or re.search(r"Heading\s*1", para.style.name) or space_strip.strip().lower().startswith(("conflict","discussion","conclusion","materials")) or re.search(r'^\d(\.|\s)+[A-Za-z]|^\b[IVX]+\.\s*', para.text):
            if  space_strip.strip().lower().startswith("conflict"):
                if "back" not in variables["back_start"]:
                    if variables["sec_3"] > 1:
                        text += f'</sec></sec></sec></body><back><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
                    elif variables["sec_2"] > 1:
                        text += f'</sec></sec></body><back><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
                    else:
                        text += f'</sec></body><back><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
                    
                    #Update the dictionary variable values
                    variables.update(secid = variables["sec_1_id"], sec_1_id = variables["sec_1_id"] + 1, sec_2_id = 1, sec_2 = 1, sec_3 = 1, back_start = variables["back_start"] + "back")

                elif "fn" in variables["back_start"]:
                    xml_text = xml_text.split(":")
                    text += f'<fn fn-type="conflict"><p><bold>{xml_text[0]}</bold>{xml_text[1]}</p></fn>'

            else:
                if "<disp-formula>" in xml_text or "figure" in xml_text.lower() or xml_text.strip().lower().startswith("("):
                    text += f'<p>{xml_text}</p>'
                    return text
                
                xml_text = re.sub('^[\d.\s*]+', '', xml_text)   #Remove numbers before string
                if variables["sec_3"] > 1:
                    text += f'</sec></sec></sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
                elif variables["sec_2"] > 1:
                    text += f'</sec></sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
                else:
                    text += f'</sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'

                #Update the dictionary variable values
                variables.update(secid = variables["sec_1_id"], sec_1_id = variables["sec_1_id"] + 1, sec_2_id = 1, sec_2 = 1, sec_3 = 1)

        elif re.search(r"Heading\s*3", para.style.name) or re.search(r'^\d+\.\d+\.\d+\.*\s.*$', para.text):
            
            xml_text = re.sub('^[\d\.\d\.\d\.*\s*]+', '', xml_text)   #Remove numbers before string
            text += f'</sec><sec id="s{variables["secid"]}_{variables["sec_3_id"]}_{variables["inner_3_id"]}"><label>{variables["secid"]}.{variables["sec_3_id"]}.{variables["inner_3_id"]}</label><title1>{xml_text}</title1>'
            variables["inner_3_id"] += 1

        elif para.alignment == 0 or re.search(r"Heading\s*2", para.style.name) or re.search(r'^\d+\.\d+\.*\)*\s*', para.text.strip()):
            xml_text = re.sub('^[\d\.\d\.*\s*]+', '', xml_text)   #Remove numbers before string
            if "<disp-formula>" in xml_text:
                text += f'<p>{xml_text}</p>'
                return text
            if variables["sec_3"] > 1:
                text += f'</sec></sec><sec id="s{variables["secid"]}_{variables["sec_2_id"]}"><label>{variables["secid"]}.{variables["sec_2_id"]}</label><title1>{xml_text}</title1>'
            else:
                text += f'</sec><sec id="s{variables["secid"]}_{variables["sec_2_id"]}"><label>{variables["secid"]}.{variables["sec_2_id"]}</label><title1>{xml_text}</title1>'

            #Update the dictionary variable values
            variables.update(sec_3_id = variables["sec_2_id"], sec_2_id = variables["sec_2_id"] + 1, inner_3_id = 1, sec_3 = 1,sec_2 = variables["sec_2"] + 1)
        
        elif (all_bold and len(para.text.strip().split()) < 15):
            xml_text = re.sub('^[\d.\s*]+', '', xml_text)   #Remove numbers before string
            if variables["sec_3"] > 1:
                text += f'</sec></sec></sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
            elif variables["sec_2"] > 1:
                text += f'</sec></sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'
            else:
                text += f'</sec><sec id="s{variables["sec_1_id"]}"><label>{variables["sec_1_id"]}</label><title1>{xml_text}</title1>'

            #Update the dictionary variable values
            variables.update(secid = variables["sec_1_id"], sec_1_id = variables["sec_1_id"] + 1,sec_3_id = 1, sec_2_id = 1, sec_2 = 1, sec_3 = 1)

        else:
            text = f'<p>{xml_text}</p>'
            
        #Success log message
        logger.info(f"Successfully created the inner sec tag from (sub_heading function) (heading.py)-file")
    except Exception as e:
        print(f"Error in (sub_heading function) (heading.py)-file {e}")
        #Error log message
        logger.error(f"Error in (sub_heading function) (heading.py)-file {e}")

    return text
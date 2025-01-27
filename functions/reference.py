
#Define function to find reference part
def reference(xml_text, variables, logger):

    try:
        xml_text = xml_text.replace("<bold>","").replace("</bold>","")
        #Chect "back" is already present in variable or not to open the back tag
        if "back" not in variables["back_start"]:
            if variables["sec_3"] > 1 or variables["sec_2"] > 1:
                text = f'</sec></sec></body><back><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
            else:
                text = f'</sec></body><back><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
            variables["ref"]=True
        elif "fn" in variables["back_start"]:   #fn is already is there then not anames back tag
            text = f'</p></fn></fn-group><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        else:
            if variables["sec_3"] > 1 or variables["sec_2"] > 1:
                text = f'</sec></sec><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
            elif variables["sec_1"] > 1:
                text = f'</sec><ref-list content-type="authoryear"><title1>{xml_text}</title1>'
            else:
                text = f'<ref-list content-type="authoryear"><title1>{xml_text}</title1>'
        variables["fn_start"] = False
        variables["ref"] = True
        
        #Success log message
        logger.info(f"Successfully created the ref tag from (reference function) (reference.py)-file")

        return text
    except Exception as e:
        print(f"Error in (reference function) (reference.py)-file {e}")
        #Error log message
        logger.error(f"Error in (reference function) (reference.py)-file {e}")

def reference_temp(xml_text, variables, logger):
    
    text = ''

    text = f'<ref id="ref-{variables["ref_id"]}">{xml_text}</ref>'
        
    variables["ref_id"] += 1
    
    #Success log message
    logger.info(f"Successfully created the ref tag from (reference_temp function) (reference.py)-file")
    
    return text
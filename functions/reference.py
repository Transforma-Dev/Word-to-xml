import re 


#Define function to find reference part
def reference(xml_text,variables):
    
    xml_text=xml_text.replace("<bold>","").replace("</bold>","")
    #Chect "back" is already present in variable or not to open the back tag
    if "back" not in variables["back_start"]:
        if variables["sec_3"]>1:
            text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
        elif variables["sec_2"]>1:
            text=f'</sec></sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
        else:
            text=f'</sec></body><back><ref-list content-type="authoryear"><title>{xml_text}</title>'
        variables["ref"]=True
    elif "fn" in variables["back_start"]:   #fn is already is there then not add back tag
        text=f'</p></fn></fn-group><ref-list content-type="authoryear"><title>{xml_text}</title>'
    else:
        if variables["sec_3"]>1:
            text=f'</sec></sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
        elif variables["sec_2"]>1:
            text=f'</sec></sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
        elif variables["sec_1"]>1:
            text=f'</sec><ref-list content-type="authoryear"><title>{xml_text}</title>'
        else:
            text=f'<ref-list content-type="authoryear"><title>{xml_text}</title>'

    variables["fn_start"]=False
    variables["ref"]=True
    #print(text)
    return text

def reference_text(xml_text,variables):
    #Split the reference text and find author name and year
    xml_text_split = xml_text.split(".")
    count = 1
    #Find the author name and year in reference part
    for i in xml_text_split:
        matches = re.findall(r"\b\d{4}\b", i)
        if count==1:
            auth_name = i.split(",")[0]
            count+=1
        elif "&" in i:
            i = i[1:]
            auth_name += i.split(",")[0]
        elif matches:
            if matches[0] in i:
                auth_name += ","+i
                break
    
    variables["ref_text_link"].append(auth_name)
    # print(variables["ref_text_link"])

    text=f'<ref id="ref-{variables["ref_id"]}">{xml_text}</ref>'
    
    variables["ref_id"]+=1
    #print(text)
    return text
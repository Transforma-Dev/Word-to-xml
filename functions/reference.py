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
    elif "fn" in variables["back_start"]:   #fn is already is there then not anames back tag
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
    
    # xml_text = re.sub(r'^\[\d+\]', '', xml_text)

    # names = volume = alt_title = year = source = issue = page = pub_id = ''

    # match = re.search(r'\b[A-Za-z]{3}\. \d{2}, \d{4}\b| \d{4}\b',xml_text)
    # # Extract the matched date if found
    # result = match.group() if match else None
    # if result:
    #     year += f'<year>{result}</year>'
    #     xml_text = re.sub(re.escape(result), "", xml_text).strip()
    
    # aa = xml_text.strip().split(",")
    # # print(aa)
    
    # matches = re.findall(r'"(.*?)"', xml_text)
    # # Print the results
    # for match in matches:
    #     alt_title = f'<article-title>{match}</article-tite>'
    
    # # match = re.search(r'\b\d{3}-\d{3}\b | \b\d{2}-\d{2}\b | \b\d{4}-\d{4}\b',xml_text)
    # # # Extract the matched date if found
    # # result = match.group() if match else None
    # # hh = f'<year>{result}</year>'

    # # if "Applied" in xml_text:
    # #     print("plo")
    
    
    # for i in aa:
    #     if "." in i:
    #         # print(aa)
    #         i = i.replace("and","")
    #         split_i = i.strip().split(".")
    #         # print(split_i)
    #         if len(split_i[0])<2 and len(split_i[0])!=0: 
    #             names += f'<string-name><surname>{split_i[-1]}</surname><given-names>{"".join(split_i[:-1])}</given-names></string-name>,'
    #             # print(names)
    #         elif "vol" in split_i:
    #             volume = f'<volume>{split_i[1]}</volume>'
    #         elif "no." in i:
    #             issue = f'<issue>{i}</issue>'
    #         elif "pp." in i:
    #             i = i.split("-")
    #             page = f'<fpage>{i[0]}</fpage>-<lpage>{i[1]}</lpage>'
    #         elif "doi" in i:
    #             pub_id += f'<pub-id>{i}</pub-id>'
    #     elif "italic" in i:
    #         i = i.replace('"','').replace('<italic>','').replace('</italic>','')
    #         source += f'<source>{i}</souce>'
        
    # names = names[:-1]

    
    # xml_text = f'<label>{variables["ref_id"]}.</label><mixed-citation publication-type="journal"><person-group person-group-type="author">{names}</person-group>.{alt_title}{source}{year}{volume}{issue}{page}{pub_id}</mixed-citation>'
    # # print(aa)

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
    # print(text)
    return text
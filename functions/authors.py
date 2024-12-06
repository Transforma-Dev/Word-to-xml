import re

#Define function to find author name
def author_name(xml_text,variables):
    variables["author_id"]=1
    #Remove italic and bold tag present in author name
    xml_text = re.sub(r'</?(italic|bold)>', '', xml_text)
    if "<sup>" not in xml_text and any(char.isdigit() or "*" for char in xml_text):
        #superscript text in normal text then write regex to identify them
        pattern = r'([A-Za-z\s\-]*)([\d\,\*]*)'
        matche = re.findall(pattern, xml_text)
        split_string = []
        matches = []
        for name, numbers in matche:
            split_string.append(name.strip())   #It holds the author names
            matches.append(numbers.strip())     #It holds the numbers
    else:
        xml_t = re.split(r',\s*[A-Za-z]| and |;\s*', xml_text)
        pattern = re.compile(r'<sup>(.*?)</sup>(\*)?')
        matches = []
        for i in xml_t:
            i = i+"</sup>"
            matche = pattern.findall(i)     #Get superscipt tag text
            add = ''
            for j in matche:
                j,i = j
                add += j+i
            matches.append(add)
        string = re.sub(pattern, '', xml_text)  #Get non superscript text
        split_string = re.split(r',\s*| and |;\s*', string)

    text=f'''</article-title>
                    <alt-title alt-title-type="left-running-head">{variables["noman_store"]}</alt-title>
                    <alt-title alt-title-type="right-running-head">{variables["noman_store"]}</alt-title>
                </title-group>
                <contrib-group content-type="authors">'''  
    for i in split_string:
        auth = [value for value in i.split() if value]
        if auth:
            if variables["author_id"]==1:
                text+=f'<contrib id="author-{variables["author_id"]}" contrib-type="author" corresp="yes"><contrib-id contrib-id-type="orcid"></contrib-id><name name-style="western"><surname>{auth[-1]}</surname><given-names>'
            else:
                text+=f'<contrib id="author-{variables["author_id"]}" contrib-type="author"><contrib-id contrib-id-type="orcid"></contrib-id><name name-style="western"><surname>{auth[-1]}</surname><given-names>'
            variables["author_id"]+=1
            variables["copyright_state"]+=auth[-1]+" and "
            auth=auth[:-1]
            #Print all text except last in given names tag
            text += ' '.join(i for i in auth if i!="and") + ' '
            text+=f'</given-names></name>'
            if matches and matches!=",":
                mat=matches[0]
                mat = mat.replace(",","")
                matches=matches[1:]
                for j in mat:
                    if j.strip()=="":
                        continue
                    if j and j != "*":
                        text += f'<xref ref-type="aff" rid="aff-{j}" href="#aff-{j}">{j}</xref>'
                    elif j == "*":
                        text += '<mail>demo@email.com</mail>'
                # print(text)
            text+=f'</contrib>'

    variables["noman_store"] = ""
    variables["para_count"]+=1
    #print(text)
    return text


#Define function to find aff text
def aff_para(xml_text,variables):
    # print(xml_text)
    split_last=xml_text.split(";")
    xml_text=split_last[0]
    text=""
    pattern = re.compile(r'<sup>\d\d*</sup>')
    matches = pattern.findall(xml_text)     #Get superscipt tag text
    string = re.sub(pattern, '', xml_text)  #Get non superscript text
    string = string.replace("<sup>","").replace("</sup>","")
    if any(keyword in xml_text.lower() for keyword in ["running title:", "orcid:"]):
        return text
    else:
        text=f'<aff id="aff-{variables["aff_id"]}">'
        run_text=string.split(",")
        if matches:
            text+=f'<label>{matches[0]}</label>'
        #Add all text except last one
        institution_text = " ".join(run_text[:-1])
        #Add the institution and country information
        text += f'<institution>{institution_text}</institution><country>{run_text[-1]}</country></aff>'
        variables["aff_id"]+=1

    #print(text)
    return text


#Define function to find coresponding author
def corres_author(xml_text,variables):
    
    #Replace specific HTML tags with appropriate XML tags for email and labels
    xml_text=xml_text.replace("<sup>","<label>").replace("</sup>","</label>").replace("<link>","<email>").replace("</link>","</email>")
    
    #Remove empty label tag
    matches = re.findall(r'<label>(.*?)</label>', xml_text, re.DOTALL)
    num = 0
    for match in matches:
        if len(match.strip())==0:
            num += 1
    if len(matches)!=0 and len(matches)==num:
        xml_text = xml_text.replace("<label>","").replace("</label>","")
    
    if variables["para_count"]==3:
        text=f'</contrib-group><author-notes><corresp id="cor1">{xml_text}'
    elif ".com" in xml_text:
        text=f'</corresp></author-notes><author-notes><corresp id="cor2">{xml_text}'
    else:
        text=f'</corresp></author-notes><author-notes><corresp id="cor2">{xml_text}'
    
    variables["para_count"]+=1
    variables["aff_tag"]=False
    #print(text)
    return text
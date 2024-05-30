import re


#Define function to find abstract paragraph in document
def abstract(xml_text,variables,filename):
    copy_xml=xml_text
    res = ''
    #Find the contend in resume in TSP_PO_49526.docx
    if variables["noman_store"]:
        variables["noman_store"] = variables["noman_store"].lower().split("mots cles")
        res = f'<abstract><p>{variables["noman_store"][0]}</p></abstract>'

    if "keyword" in xml_text.lower():
        split_xml = re.split(r'keyword\s*', xml_text, flags=re.IGNORECASE)
        split_xml[1]="KEYWORD"+split_xml[1]
        xml_text=split_xml[0]
            
    xml_text = re.sub(r'<bold>.*?abstract:.*?</bold>|abstract:', '', xml_text,flags=re.IGNORECASE)
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
                    <copyright-statement>&#x00A9; 2024 </copyright-statement>
                    <copyright-year>2024</copyright-year>
                    <copyright-holder>et al.</copyright-holder>
                    <license xlink:href="https://creativecommons.org/licenses/by/4.0/">
                        <license-p>This is an open access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original source is cited.</license-p>
                    </license>
                </permissions>
                <self-uri content-type="pdf" xlink:href="{filename}"></self-uri>{res}<abstract abstract-type="abstract"><p>{xml_text}</p>'''
    if "keyword" in copy_xml.lower():
        text += keyword_text(split_xml[1],variables)

    #Find the contend in resume in TSP_PO_49526.docx
    if variables["noman_store"]:
        variables["noman_text"] = False
        text += keyword_text(variables["noman_store"][1],variables)
        text = text.replace("</article-meta></front><body>","")
    
    #print(text)
    return text


#Define funcion to find keywords in document
def keyword_text(xml_text,variables):
    #Remove keyword text and bold tag in string
    xml_text = re.sub(r'keywords?:|key\s*words', '', xml_text, flags=re.IGNORECASE)
    xml_text= re.sub(r'<bold>.*?</bold>', '', xml_text)
    xml_text=xml_text.replace(":","").replace(";", ",")

    #Split the string into individual keywords
    xml_text = [keyword for keyword in xml_text.split(",") if "keyword" not in keyword.lower()]
    if variables["noman_text"]:
        text=f'<kwd-group kwd-group-type="author">'
        for i in xml_text:
            text+=f'<kwd>{i}</kwd>'
        text+=f'</kwd-group></article-meta></front><body>'
        variables["noman_text"] = False
    else:
        text=f'</abstract><kwd-group kwd-group-type="author">'
        for i in xml_text:
            text+=f'<kwd>{i}</kwd>'
        text+=f'</kwd-group></article-meta></front><body>'

        if variables["noman_store"]:
            variables["noman_text"] = True
            variables["noman_store"] = ''
        else:
            variables["noman_text"] = False

    #print(text)
    return text
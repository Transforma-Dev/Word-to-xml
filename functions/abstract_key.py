import re
from datetime import datetime


#Define function to find abstract paragraph in document
def abstract(xml_text, variables, filename):
    try:
        copy_xml = xml_text
        res = ''
        #print copyright statement
        ss = variables["copyright_state"].count("and")
        if ss > 3:
            variables["copyright_state"] = variables["copyright_state"].split("and")
            variables["copyright_state"] = variables["copyright_state"][0]+"et al."
        else:
            variables["copyright_state"] = variables["copyright_state"].strip()[:-3]

        #Find the contend in resume in TSP_PO_49526.docx
        if variables["noman_store"]:
            variables["noman_store"] = variables["noman_store"].lower().split("mots cles")
            res = f'<abstract><p>{variables["noman_store"][0]}</p></abstract>'

        if "keyword" in xml_text.lower():
            split_xml = re.split(r'keyword\s*', xml_text, flags = re.IGNORECASE)
            split_xml[1] = "KEYWORD"+split_xml[1]
            xml_text = split_xml[0]

        #Find the recived date in document
        d1 = d2 = 00
        m1 = m2 = 0
        y1 = y2 = 2024 
        if variables["recive"]:
            variables["recive"] = variables["recive"].replace(";","").replace(",","").replace(":","").replace("Received","").replace("Accepted","")
            date = variables["recive"].split()
            mon = []
            for find in date:
                if find.strip().lower() in ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]:
                    mon.append(datetime.strptime(find, "%B").month)
            d1, m1, y1, d2, m2, y2 = date[0], mon[0], date[2], date[3], mon[1], date[5]

        xml_text = re.sub(r'<bold>.*?abstract:.*?</bold>|abstract:', '', xml_text, flags=re.IGNORECASE)
        text = f'''</corresp></author-notes>
                    <pub-date pub-type="epub" date-type="pub" iso-8601-date="2024-00-00">
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
                            <day>{d1}</day>
                            <month>{m1}</month>
                            <year>{y1}</year>
                        </date>
                        <date date-type="accepted">
                            <day>{d2}</day>
                            <month>{m2}</month>
                            <year>{y2}</year>
                        </date>
                    </history>
                    <permissions>
                        <copyright-statement>&#x00A9; 2024 {variables["copyright_state"]}</copyright-statement>
                        <copyright-year>2024</copyright-year>
                        <copyright-holder>{variables["copyright_state"]}</copyright-holder>
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
            text = text.replace("</article-meta></front><body>", "")

        if variables["key_store"]:
            text += f'{variables["key_store"]}'  

        variables["key_first"] = False  
    except Exception as e:
        print("Error in abstract_key function.", e)
        text = ""

    return text


#Define function to find keywords in document
def keyword_text(xml_text,variables):
    try:
        #Remove keyword text and bold tag in string
        xml_text = re.sub(r'keywords?:|key\s*words', '', xml_text, flags=re.IGNORECASE)
        xml_text = re.sub(r'<bold>.*?</bold>', '', xml_text)
        xml_text = xml_text.replace(":", "").replace(";", ",")
        
        #Split the string into individual keywords
        xml_text = [keyword for keyword in xml_text.split(",") if "keyword" not in keyword.lower()]
        if variables["noman_text"]:
            text = f'<kwd-group kwd-group-type="author">'
            for i in xml_text:
                text += f'<kwd>{i}</kwd>'
            text += f'</kwd-group></article-meta></front><body>'
            variables["noman_text"] = False
        else:
            text = f'</abstract><kwd-group kwd-group-type="author">'
            for i in xml_text:
                text += f'<kwd>{i}</kwd>'
            text += f'</kwd-group></article-meta></front><body>'

            if variables["noman_store"]:
                variables["noman_text"] = True
                variables["noman_store"] = ''
            else:
                variables["noman_text"] = False
        
        if variables["key_first"]:
            variables["key_store"] = text
            text = ''
    except Exception as e:
        print("Error in abstract_key function.", e)
        text = ""

    return text
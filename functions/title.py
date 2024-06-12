import json
import re


#Define the function to find title of the document
def title(para,xml_text,variables,data,journal,file_name):
    
    text=''
    #Skip the all words in document
    keywords = ["doi:", "commentary", "type:", "article", "running title:"]
    if any(keyword in para.text.lower() for keyword in keywords):
        return text

    #Adjust the journal list based on its length
    if len(journal)==1:
        journal=file_name.split("-")
    elif len(journal)==3:
        journal=journal[1:]
        
    #Extract numbers from the last part of the journal
    numbers_only = re.findall(r'\d+',journal[-1])

    #Replace bold tag to empty
    xml_text=xml_text.replace("<bold>","").replace("</bold>","")
        
    if variables["para_count"]==2:
        variables["para_count"]-=1
            
        text=f'{xml_text}'
    else:
        text=f'''<front>
            <journal-meta>
                <journal-id journal-id-type="pmc">{journal[0]}</journal-id>
                <journal-id journal-id-type="nlm-ta">{journal[0]}</journal-id>
                <journal-id journal-id-type="publisher-id">{journal[0]}</journal-id>
                <journal-title-group>
                    <journal-title>{data[journal[0]]['journal_title']}</journal-title>
                </journal-title-group>
                {data[journal[0]]['issn_no']}
                <publiher>
                    <publisher-name>{data[journal[0]]['publisher_name']}</publisher-name>
                    <publisher-loc>{data[journal[0]]['publisher_loc']}</publisher-loc>
                </publisher>
            </journal-meta>
            <article-meta>
                <article-id pub-id-type="publisher-id">{numbers_only[0]}</article-id>
                <article-id pub-id-type="doi">{data[journal[0]]['article_id']}{numbers_only[0]}</article-id>
                <article-categories>
                    <subj-group subj-group-type="heading">
                        <subject>{data[journal[0]]['subject']}</subject>
                    </subj-group>
                </article-categories>
            <title-group><article-title>{xml_text}'''
            
    variables["noman_store"] += xml_text
    variables["para_count"]+=1
    #print(text)
    return text
#import neccessary librarys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os,sys
import re
import json
import spacy
import index

class TSP_styles:

    def __init__(self):
        self.article_tit = False

    #Replace text or add space or remove space in this function
    def change_space_text(self,element,data):   #https://github.com/Transforma-Dev/Word-to-xml/issues/22#issue-2385189744

        #Replace text
        for i in data["replace_text"]:
            if element.text and i["text"] in element.text:
                element.text = element.text.replace(i["text"], i["replace"])
            if element.tail and i["text"] in element.tail:
                element.tail = element.tail.replace(i["text"], i["replace"])

        #Replace and add space text
        for i in data["space_add_text"]:
            if element.text and i in element.text:
                    pattern = fr"\s*\{i}\s*"
                    element.text = re.sub(pattern, f' {i} ', element.text)

            if element.tail and i in element.tail:
                pattern = fr"\s*\{i}\s*"
                element.tail = re.sub(pattern, f' {i} ', element.tail)

        #Replace and remove space text
        for i in data["space_remove_text"]:     #https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
            if element.text and i in element.text:
                pattern = fr"\s*\{i}\s*"
                element.text = re.sub(pattern, f'{i}', element.text)
            if element.tail and i in element.tail:
                pattern = fr"\s*\{i}\s*"
                element.tail = re.sub(pattern, f'{i}', element.tail)

        #Replace and add space only before text
        for i in data["space_before_text"]:
            if element.text and i in element.text.lower():
                # print(element.text)
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, element.text,re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        match1 = match[0]
                        match2 = match[1:]
                        element.text = element.text.replace(match, f'{match1} {match2.strip()}')

            if element.tail and i in element.tail.lower():
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, element.tail,re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        match1 = match[0]
                        match2 = match[1:]
                        element.tail = element.tail.replace(match, f'{match1} {match2.strip()}')

        #Replace and add space only after text
        for i in data["space_after_text"]:
            if element.text and i in element.text.lower():
                pattern = fr"{i}\s*\d"     #r"\bno\.\d+"
                matchs = re.findall(pattern, element.text,re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        match1 = match[0]
                        match2 = match[1:]
                        element.text = element.text.replace(match, f'{match1} {match2.strip()}')

            if element.tail and i in element.tail.lower():
                pattern = fr"{i}\s*\d"
                matchs = re.findall(pattern, element.tail,re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        match1 = match[:-1]
                        match2 = match[-1]
                        element.tail = element.tail.replace(match, f'{match1} {match2.strip()}')

        #Find the continuous text and add "," and last will add "and" 
        for symbol in data["add_and"]:
            if element.text:
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern,element.text,re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i:
                            split = i.split(",")
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1]
                            element.text = re.sub(i,simple,element.text)
            if element.tail:
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern,element.tail,re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i:
                            split = i.split(",")
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1]
                            element.tail = re.sub(i,simple,element.tail)

        #Find the repeated text with unit and get the same unit name remove them and add unit in last of the string
        for symbol in data["add_all"]:
            if element.text:
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*a*n*d*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern,element.text,re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i or "and" in i:
                            split = re.split(r'\s*,\s*|\s*and\s*', i)
                            j = ''
                            for sec in split:
                                j += ''.join(k for k in sec if k.isalpha())
                                if j:
                                    break
                            split = [sec.replace(j, '') for sec in split]
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1] + j
                            element.text = element.text.replace(i,simple)
                            # element.text = [:-1]
            if element.tail:
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*a*n*d*\s*\d+\.*\d*\s*{symbol}\.*)*' 
                result = re.findall(pattern,element.tail,re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i or "and" in i:
                            split = re.split(r'\s*,\s*|\s*and\s*', i)
                            j = ''
                            for sec in split:
                                j += ''.join(k for k in sec if k.isalpha())
                                if j:
                                    break
                            split = [sec.replace(j, '') for sec in split]
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1] + j
                            element.tail = element.tail.replace(i,simple)

        #Chnage the SI_unit minutes,seconds,hours with min,s,h
        for si_unit in data["si_units"]:
            if element.text and si_unit["text"] in element.text:
                pattern = fr'\d+\s*{si_unit["text"]}[s]*'
                result = re.findall(pattern, element.text,re.IGNORECASE)
                if result:
                    for i in result:
                        new_text = i[0] + " " + si_unit["replace"]
                        element.text = re.sub(i,new_text,element.text)
            if element.tail and si_unit["text"] in element.tail:
                pattern = fr'\d+\s*{si_unit["text"]}[s]*'
                result = re.findall(pattern, element.tail,re.IGNORECASE)
                if result:
                    for i in result:
                        new_text = i[0] + " " + si_unit["replace"]
                        element.tail = re.sub(i,new_text,element.tail)

        #Remove the ref or refs text present in middle of the paragraph
        pattern = r"\w\sRefs*\s"    #https://github.com/Transforma-Dev/Word-to-xml/issues/20#issue-2385186827
        if element.text is not None:
            match = re.findall(pattern,element.text,re.IGNORECASE)
            if match:   
                element.text = re.sub(match[0],match[0][:2],element.text)
        if element.tail is not None:
            match = re.findall(pattern,element.tail,re.IGNORECASE)
            if match:   
                element.tail = re.sub(match[0],match[0][:2],element.tail)

    #Find the article title,heading tag and capitalie the article title,heading text except remove conjuction and preposition
    def find_artitle(self,element,data,nlp):    #https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
        if element.text and element.text.strip():
            # print(element.text)
            doc = nlp(element.text)
            # for word in doc:
            text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP","DET","CCONJ"] else word.text.lower() for word in doc])
            element.text = text.strip()[0].upper() + text.strip()[1:]

        if element.tail and element.tail.strip():
            doc = nlp(element.tail)
            # for word in doc:
            text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ not in ["ADP","DET","CCONJ"] else word.text.lower() for word in doc])
            element.tail = " " + text.strip()[0].upper() + text.strip()[1:]
          
    #Remove dot in end of affliation tag and replace the perticuler text
    def find_aff(self,element,data,nlp):    #https://github.com/Transforma-Dev/Word-to-xml/issues/9#issue-2379911935
        for child in element:
            self.change_text(child,nlp)
            #Replace text
            for i in data["aff_replace_text"]:
                if child.text and i["text"] in child.text:
                    child.text = child.text.replace(i["text"], i["replace"])
        
        if child.text and child.text.strip().endswith('.'):
            child.text = child.text[:-1]
        # new_tag = ET.Element("new")
        # new_tag.text = "mew"
        # element.append(new_tag)

    #Find if date is not present in document then add query tag 
    def find_history(self,element):     #https://github.com/Transforma-Dev/Word-to-xml/issues/11#issue-2385178216
        tag = False
        children_to_remove = []
        for child in element:
            for chil in child:
                if chil.tag == "day":
                    if chil.text.strip() == "0":
                        tag = True
                    #Add 0 for single digit day value
                    elif len(element.text.strip()) == 1:
                        chil.text = "0" + chil.text.strip()
            if tag:
                children_to_remove.append(child)
                
        for child in children_to_remove:
            element.remove(child)
        if tag:
            new_tag = ET.Element("Query")
            new_tag.text = "No History details present in the document"
            element.append(new_tag)

    #Remove dot in end of kwd-group tag and change the first letter as capital others all are small
    def find_key(self,element,nlp):     #https://github.com/Transforma-Dev/Word-to-xml/issues/14#issue-2385180471
        try:
            n=1
            for child in element:
                if child.text!=None:
                    self.change_text(child,nlp)
                    docs = nlp(child.text)
                    child_text = " ".join([word.text if word.text.isupper() else word.text.lower() for word in docs])
                    doc = nlp(child_text)
                    if n==1 and child.text.strip():
                        child_ext = ' '.join([word.text if not word.text.isupper() else word.text for word in doc])
                        child.text = " " + child_ext.strip().capitalize() + " "
                        n+=1
                    else:
                        child.text = ' '.join([word.text if not word.text.isupper() else word.text for word in doc])

                        # child.text = child.text.lower()
            if child.text!=None:
                if child.text.strip().endswith('.'):
                    child.text = " " + child.text.strip()[:-1]
        except Exception as e:
            print("Error in find_key in tsp_styles.", e)

    #Change the table title and figure title in sentance case.
    def find_fig_title(self,element,nlp):       #https://github.com/Transforma-Dev/Word-to-xml/issues/17#issue-2385183456
        try:
            if element.text and element.text.strip():
                # print(element.text)
                doc = nlp(element.text)                 #https://github.com/Transforma-Dev/Word-to-xml/issues/18#issue-2385184522
                text = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])

                #Remove extra spaces around commas and inside parentheses
                text = re.sub(r'\s+([,.])', r'\1', text)  # Remove space before commas and periods
                text = re.sub(r'\(\s*', '(', text)     # Remove space after opening parenthesis
                text = re.sub(r'\s*\)', ')', text)     # Remove space before closing parenthesis                
                element.text = text.strip()[0].upper() + text.strip()[1:]
                # print(element.text,"----")
                for child in element:
                    if child.text and child.text.strip():
                        nlp = spacy.load("en_core_web_sm")
                        doc = nlp(child.text)
                        child_text = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])
                        split = child_text.split(".")
                        for id,i in enumerate(split):
                            if len(i.strip())!=0:
                                if id == 0:
                                    child.text = i
                                else:
                                    child.text += "." + i.strip()[0].upper() + i.strip()[1:]
                    if child.tail is not None and child.tail.strip():
                        doc = nlp(child.tail)
                        child_tail = ' '.join([word.text if word.text.isupper() else word.text.lower() for word in doc])
                        split = child_tail.split(".")
                        for id,i in enumerate(split):
                            if len(i.strip())!=0:
                                if id == 0:
                                    child.tail = i
                                else:
                                    child.tail += "." + i.strip()[0].upper() + i.strip()[1:]
                if element.text and element.text.strip().endswith('.'):
                    element.text = " " + element.text[:-1]
        except:
            print("error in find_fig_title in tsp_style")

    def find_xref(self,element):
        if element.text and element.text.strip():
            if "-" in element.text.lower() or "and" in element.text.lower():
                element.text = element.text.lower().replace("figures","Figs.",)
            elif "figure" in element.text.lower():
                element.text = element.text.lower().replace("figure","Fig.",)

    def find_reference(self, element):
        if element.text:
            change_ref = index.TSP_ref(element.get('id'), element.text, "ieee")
            # print(f"Changed Reference: {change_ref}")
            # print(change_ref)
            print(change_ref)
            soup = ET.fromstring(change_ref)
            element.clear()
            element.append(soup)
            # for child in soup.find_all(True):  # Finds all the tags in the parsed XML
            #     print(child)
            #     # element.append(child)
            #     # print(child)
            # pretty_xml = element.prettify()
            # element.text = pretty_xml
        # print(element.text)
        # print(type(element.text))

    #Correct the back matter order in fn-group tag
    def back_order(self,fn_elements,fn_group):      #https://github.com/Transforma-Dev/Word-to-xml/issues/24#issue-2397382765
        funding = availability = author = conflict = ethics = None
        for fn in fn_elements:
            bold = fn.find("./p/bold")
            p = fn.find("./p")
            if bold is not None and bold.text:
                if "fund" in bold.text.strip().lower():
                    funding = fn
                    # bold.tail = "kdngjsij byf"
                elif "author" in bold.text.strip().lower():
                    author = fn
                elif "availability" in bold.text.strip().lower():
                    availability = fn
                elif "ethics" in bold.text.strip().lower():
                    ethics = fn
                elif "conflict" in bold.text.strip().lower():
                    conflict = fn

        fn_group.clear()

        #Remove and append tag order
        if funding:
            fn_group.append(funding)
        if author:
            fn_group.append(author)
        if availability:
            fn_group.append(availability)
        if ethics:
            fn_group.append(ethics)
        if conflict:
            fn_group.append(conflict)




    #Find the tags in xml and replace the content
    def change_text(self, element, nlp):
        # print(element.text,"----",element.tail,element)

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

        #Find the article title tag inside the front tag
        if element.tag == "article-title" or self.article_tit:
            # alt_title = element.find('./front//article-title')
            self.find_artitle(element,data,nlp)
            self.article_tit = False
            for child in element:
                self.article_tit = True
                self.change_text(child,nlp)
                # self.find_artitle(child,data,nlp)
            
        #Find the affliation tag
        if element.tag == "aff":
            self.find_aff(element,data,nlp)

        #Find the kwd-group tag
        if element.tag == "kwd-group":
            self.find_key(element,nlp)

        #Find the history tag
        if element.tag == "history":
            self.find_history(element)

        #Find heading title in sec tag and change in title case(ULC)
        for heading in element.findall("./sec/title1"):
            # print(heading.text)
            self.find_artitle(heading,data,nlp)

        #Find the table title tag
        for title in element.findall('./fig'):
            image_title = title.find('.//title1')
            if image_title is not None:
                self.find_fig_title(image_title,nlp)

        #Find the table title tag
        for title in element.findall('./table-wrap'):
            table_title = title.find('.//title1')
            if table_title is not None:
                self.find_fig_title(table_title,nlp)

        #Find the xref tag and change it
        if element.tag == "xref":
            self.find_xref(element)

        #Find the th tag
        for th in element.findall("./th"):
            if th.text is not None and element.text.strip():
                self.find_fig_title(th,nlp)

        #Find the fn-group tag and change the order of fn group
        fn_elements = element.findall(".//fn")
        fn_group = element.find("./fn-group")
        if fn_group is not None:
            self.back_order(fn_elements,fn_group) 

        #Find the reference text in ref tag
        if element.tag == "ref":
            self.find_reference(element)

        #Replace text or add or remove space in text
        self.change_space_text(element,data)

        for child in element:
            self.change_text(child,nlp)

    
    def modify_xml(self,input_file,output_file):
        #Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        nlp = spacy.load("en_core_web_sm")

        self.change_text(root,nlp)

        #Save the modified XML to a new file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"The modified XML file has been saved as '{output_file}'.")

# if __name__ == "__main__":
#     #Get file name using command line argument
#     command_arg = sys.argv[1]
#     input_file_name = os.path.basename(command_arg) if "/" in command_arg else command_arg

#     #Get the directory of the python file
#     script_path = os.path.abspath(__file__)

#     #Get the directory of the script
#     script_directory = os.path.dirname(script_path)
#     input_file = os.path.join(script_directory, "output",input_file_name)

#     #Output folder name
#     output_file = 'output.xml'

#     #Create object for class TSP_styles
#     xml_modifier = TSP_styles()
#     xml_modifier.modify_xml(input_file, output_file)

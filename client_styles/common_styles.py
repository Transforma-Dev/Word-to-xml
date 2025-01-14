#import neccessary librarys
import xml.etree.ElementTree as ET
import re
import json
import spacy

class Common_styles:

    #Replace text or add space or remove space in this function
    def change_space_text(self, element, data):   #https://github.com/Transforma-Dev/Word-to-xml/issues/22#issue-2385189744

        #Replace text
        for i in data["replace_text"]:
            if element.text and i["text"] in element.text:
                element.text = element.text.replace(i["text"], i["replace"])
            if element.tail and i["text"] in element.tail:
                element.tail = element.tail.replace(i["text"], i["replace"])

        #Replace and add space text
        for i in data["space_add_text"]:
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f' {i} ', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f' {i} ', element.tail)

        #Replace and remove space text
        for i in data["space_remove_text"]:     #https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f'{i}', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f'{i}', element.tail)

        #Replace and add space only before text
        for i in data["space_before_text"]:
            def func1(elem):
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]} {match[1:].strip()}')
                return elem
                        
            if element.text and i in element.text:
                element.text = func1(element.text)
                
            if element.tail and i in element.tail:
                element.tail = func1(element.tail)

        #Replace and remove space only before text
        for i in data["space_remove_before_text"]:
            
            def func2(elem):
                pattern = fr"\d\s*{i}"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        elem = elem.replace(match, f'{match[0]}{match[1:].strip()}')
                return elem
                
            if element.text:
                element.text = func2(element.text)
                
            if element.tail:
                element.tail = func2(element.tail)
                
        #Find the continuous text and add "," and last will add "and" 
        for symbol in data["add_and"]:
            def func3(elem):
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern, elem, re.IGNORECASE)
                if result:
                    for i in result:
                        if "," in i:
                            split = i.split(",")
                            simple = split[0] + (", " + ", ".join(split[1:-1]) if len(split) > 2 else "") + " and " + split[-1]
                            elem = re.sub(i, simple, elem)
                return elem
                            
            if element.text:
                element.text = func3(element.text)
                
            if element.tail:
                element.tail = func3(element.tail)

        #Find the repeated text with unit and get the same unit name remove them and add unit in last of the string
        for symbol in data["add_all"]:
            def func4(elem):
                pattern = fr'\d+\.*\d*\s*{symbol}(?:\s*,*\s*a*n*d*\s*\d+\.*\d*\s*{symbol}\.*)*'
                result = re.findall(pattern, elem, re.IGNORECASE)
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
                            elem = elem.replace(i, simple)
                return elem
                
            if element.text:
                element.text = func4(element.text)
                
            if element.tail:
                element.tail = func4(element.tail)

        #Chnage the SI_unit minutes,seconds,hours with min,s,h
        for si_unit in data["si_units"]:
            def func5(elem):
                pattern = fr'\d+\s*{si_unit["text"]}[s]*'
                result = re.findall(pattern, elem, re.IGNORECASE)
                if result:
                    for i in result:
                        new_text = i[0] + " " + si_unit["replace"]
                        elem = re.sub(i, new_text, elem)
                return elem
                
            if element.text and si_unit["text"] in element.text:
                element.text = func5(element.text)
                
            if element.tail and si_unit["text"] in element.tail:
                element.tail = func5(element.tail)

             

    #Find the tags in xml and replace the content
    def change_text(self, element, nlp, refere):


        #from journal load the json file
        with open("json_folder/TSP_styles.json", 'r') as file:
            data = json.load(file)

        #Find the reference text in ref tag
        if element.tag == "ref":
            refere = True

        #Replace text or add or remove space in text
        if not refere:
            self.change_space_text(element, data)

        for child in element:
            self.change_text(child, nlp, refere)

    
    def modify_xml(self, input_file, output_file):
        #Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        nlp = spacy.load("en_core_web_sm")

        refere = False

        self.change_text(root, nlp, refere)

        #Save the modified XML to a new file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"The modified XML file has been saved as '{output_file}'.")

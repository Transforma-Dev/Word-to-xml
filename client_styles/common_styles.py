#import neccessary librarys
import xml.etree.ElementTree as ET
import os,sys
import re
import json
import spacy

class Common_styles:

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
            if element.text and i in element.text:
                pattern = fr"\s*{i}\s*"
                element.text = re.sub(pattern, f' {i}', element.text)
            if element.tail and i in element.tail:
                pattern = fr"\s*{i}\s*"
                element.tail = re.sub(pattern, f' {i}', element.tail)

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

             

    #Find the tags in xml and replace the content
    def change_text(self, element, nlp):


        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

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












'''#Styles add for label and title based on heading
        for sec in element.findall('./sec'):
            title = sec.find('./title')
            label = sec.find('./label')
            
            if len(label.text.strip())>4 :      #Heading level 3 then add i tag
                if title is not None and title.text is not None:
                    self.apply_styles(title, italic=True)
                if label is not None and label.text is not None:
                    self.apply_styles(label, italic=True)
            elif 5>len(label.text.strip())>2:       #Heading level 2 then add b,i tag
                if title is not None and title.text is not None:
                    self.apply_styles(title, bold=True, italic=True)
                if label is not None and label.text is not None:
                    self.apply_styles(label, bold=True, italic=True)
            else:       #Heading level 1 then add b tag
                if title is not None and title.text is not None:
                    self.apply_styles(title, bold=True)
                if label is not None and label.text is not None:
                    self.apply_styles(label, bold=True)


#Functions to add tags style
    def apply_styles(self, element, bold=False, italic=False):
        text = element.text
        element.text = ""
        if bold and italic:
            b_elem = ET.SubElement(element, 'b')
            i_elem = ET.SubElement(b_elem, 'i')
            i_elem.text = text
        elif bold:
            b_elem = ET.SubElement(element, 'b')
            b_elem.text = text
        elif italic:
            i_elem = ET.SubElement(element, 'i')
            i_elem.text = text
        else:
            element.text = text'''
import xml.etree.ElementTree as ET
import os,sys
import re
import json
import spacy

class TSP_styles:

    #Change the table title and figure title in sentance case.
    def find_fig_title(self,element):       #https://github.com/Transforma-Dev/Word-to-xml/issues/17#issue-2385183456
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(element.text)
        text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ == 'NOUN' or word.pos_ == 'PROPN' else word.text.lower() for word in doc])
        element.text = text.strip()[0].upper() + text.strip()[1:]
        for child in element:
            if child.text is not None:
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(child.text)
                child_text = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ == 'NOUN' or word.pos_ == 'PROPN' else word.text.lower() for word in doc])
                split = child_text.split(".")
                for id,i in enumerate(split):
                    if len(i.strip())!=0:
                        if id == 0:
                            child.text = i
                        else:
                            child.text += "." + i.strip()[0].upper() + i.strip()[1:]
            if child.tail is not None:
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(child.tail)
                child_tail = ' '.join([word.text if word.text.isupper() else word.text.capitalize() if word.pos_ == 'NOUN' or word.pos_ == 'PROPN' else word.text.lower() for word in doc])
                split = child_tail.split(".")
                for id,i in enumerate(split):
                    if len(i.strip())!=0:
                        if id == 0:
                            child.tail = i
                        else:
                            child.tail += "." + i.strip()[0].upper() + i.strip()[1:]

            # print(child.tail)
        # print(text)

    #Find the tags in xml and replace the content
    def change_text(self, element):

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

        #Find the table title tag
        for title in element.findall('./fig'):
            image_title = title.find('.//title')
            if image_title is not None:
                self.find_fig_title(image_title)

        #Find the table title tag
        for title in element.findall('./table-wrap'):
            table_title = title.find('.//title')
            if table_title is not None:
                self.find_fig_title(table_title)

        for child in element:
            self.change_text(child)

    
    def modify_xml(self,input_file,output_file):
        #Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        self.change_text(root)

        #Save the modified XML to a new file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"The modified XML file has been saved as '{output_file}'.")

if __name__ == "__main__":
    #Get file name using command line argument
    command_arg = sys.argv[1]
    input_file_name = os.path.basename(command_arg) if "/" in command_arg else command_arg

    #Get the directory of the python file
    script_path = os.path.abspath(__file__)

    #Get the directory of the script
    script_directory = os.path.dirname(script_path)
    input_file = os.path.join(script_directory, "output",input_file_name)

    #Output folder name
    output_file = 'output.xml'

    #Create object for class TSP_styles
    xml_modifier = TSP_styles()
    xml_modifier.modify_xml(input_file, output_file)












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
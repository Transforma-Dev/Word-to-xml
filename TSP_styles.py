import xml.etree.ElementTree as ET
import os,sys
import re
import json

class TSP_styles:

    def change_text(self, element):

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

        #Find the article title tag inside the front tag and capitalie the article title text except remove conjuction and preposition
        if element.find('./front//article-title') is not None:
            alt_title = element.find('./front//article-title')
            alt_title.text = ' '.join(word.lower() if word.lower() in data["skip_words"] else word.capitalize() for word in alt_title.text.split())
        #Remove dot in end of affliation tag
        if element.tag == "aff":
            for child in element:
                self.change_text(child)
                #Replace text
                for i in data["aff_replace_text"]:
                    if child.text and i["text"] in child.text:
                        child.text = child.text.replace(i["text"], i["replace"])
                    
            child.text = child.text.replace(".","")
            # new_tag = ET.Element("new")
            # new_tag.text = "mew"
            # element.append(new_tag)
        #Remove dot in end of kwd-group tag and change the first letter as capital others all are small
        if element.tag == "kwd-group":
            n=1
            for child in element:
                self.change_text(child)
                if n==1 and child.text.strip():
                    child.text = child.text.strip().capitalize()
                    n+=1
                else:
                    child.text = child.text.lower()
            child.text = child.text.replace(".","")
        #Add 0 before single digit number
        if element.tag == "day" and len(element.text.strip()) == 1:
            element.text = "0" + element.text.strip()


        #Replace text
        for i in data["replace_text"]:
            if element.text and i["text"] in element.text:
                element.text = element.text.replace(i["text"], i["replace"])

        #Space before and after
        if element.text and "+" in element.text:
            pattern = r"\s*\+\s*"
            element.text = re.sub(pattern, " + ", element.text)

        for child in element:
            self.change_text(child)

    
    def modify_xml(self,input_file,output_file):
        #Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        #Replace 'dept' with 'department' in text
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
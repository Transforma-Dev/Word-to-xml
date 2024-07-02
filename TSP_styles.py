import xml.etree.ElementTree as ET
import os,sys
import re
import json

class TSP_styles:

    #Replace text or add space or remove space in this function
    def change_space_text(self,element,data):   #https://github.com/Transforma-Dev/Word-to-xml/issues/22#issue-2385189744
        #Replace text
        for i in data["replace_text"]:
            if element.text and i["text"] in element.text:
                element.text = element.text.replace(i["text"], i["replace"])

        #Replace and add space text
        for i in data["space_add_text"]:
            if element.text and i in element.text:
                pattern = fr"\s*\{i}\s*"
                element.text = re.sub(pattern, f' {i} ', element.text)

        #Replace and remove space text
        for i in data["space_remove_text"]:     #https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
            if element.text and i in element.text:
                pattern = fr"\s*\{i}\s*"
                element.text = re.sub(pattern, f'{i}', element.text)

        #Replace and add space only before text
        for i in data["space_before_text"]:
            if element.text and i in element.text:
                pattern = fr"\s*{i}\s*"
                element.text = re.sub(pattern, f' {i}', element.text)

    #Find the article title tag inside the front tag and capitalie the article title text except remove conjuction and preposition
    def find_artitle(self,element,data):    #https://github.com/Transforma-Dev/Word-to-xml/issues/8#issue-2379909859
        alt_title = element.find('./front//article-title')
        alt_title.text = ' '.join(word.lower() if word.lower() in data["skip_words"] else word.capitalize() for word in alt_title.text.split())
    
    #Remove dot in end of affliation tag and replace the perticuler text
    def find_aff(self,element,data):    #https://github.com/Transforma-Dev/Word-to-xml/issues/9#issue-2379911935
        for child in element:
            self.change_text(child)
            #Replace text
            for i in data["aff_replace_text"]:
                if child.text and i["text"] in child.text:
                    child.text = child.text.replace(i["text"], i["replace"])
                    
        if child.text.endswith('.'):
            child.text = child.text[:-1]
        # new_tag = ET.Element("new")
        # new_tag.text = "mew"
        # element.append(new_tag)

    #Remove dot in end of kwd-group tag and change the first letter as capital others all are small
    def find_key(self,element):     #https://github.com/Transforma-Dev/Word-to-xml/issues/14#issue-2385180471
        n=1
        for child in element:
            self.change_text(child)
            if n==1 and child.text.strip():
                child.text = child.text.strip().capitalize()
                n+=1
            else:
                child.text = child.text.lower()
        if child.text.endswith('.'):
            child.text = child.text[:-1]

    def find_history(self,element):
        tag = False
        children_to_remove = []
        for child in element:
            for chil in child:
                if chil.tag == "day":
                    if chil.text.strip() == "0":
                        tag = True
                    elif len(element.text.strip()) == 1:
                        chil.text = "0" + chil.text.strip()
            if tag:
                children_to_remove.append(child)
                
        for child in children_to_remove:
            element.remove(child)
        if tag:
            new_tag = ET.Element("Query")
            new_tag.text = "No History detail is there in the document"
            element.append(new_tag)




    #Find the tags in xml and replace the content
    def change_text(self, element):

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

        #Find the article title tag inside the front tag
        if element.find('./front//article-title') is not None:
            self.find_artitle(element,data)
            
        #Find the affliation tag
        if element.tag == "aff":
            self.find_aff(element,data)

        #Find the kwd-group tag
        if element.tag == "kwd-group":
            self.find_key(element)

        if element.tag == "history":
            self.find_history(element)
            
        #Add 0 before single digit number
        if element.tag == "day" and len(element.text.strip()) == 1:     #https://github.com/Transforma-Dev/Word-to-xml/issues/11#issue-2385178216
            element.text = "0" + element.text.strip()

        if element.find('./table-wrap//title') is not None:
            table_title = element.find('./table-wrap//title')
            # table_title.text = 

        #Replace text or add or remove space in text
        self.change_space_text(element,data)

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
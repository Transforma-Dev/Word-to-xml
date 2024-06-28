import xml.etree.ElementTree as ET
import os,sys

class TSP_styles:

    def change_text(self, element):

        #Find the article title tag inside the front tag and capitalie the article title text except remove conjuction and preposition
        if element.find('./front//article-title') is not None:
            alt_title = element.find('./front//article-title')
            skip_words = ["and", "or", "but","so", "in", "on", "at", "for", "with", "to", "from","of","into","a"]
            alt_title.text = ' '.join(word.lower() if word.lower() in skip_words else word.capitalize() for word in alt_title.text.split())
        #Remove dot in end of affliation tag
        if element.tag == "aff":
            for child in element:
                self.change_text(child)
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

        replace_text = {"People’s Republic of China",""}
        #Replace china
        if element.text and 'People’s Republic of China' in element.text:
            element.text = element.text.replace('People’s Republic of China', 'China')
        #Replace department
        if element.text and 'Dept.' in element.text:
            element.text = element.text.replace('Dept.', 'Department')
        #Replace department
        if element.text and ('i.e.' in element.text or 'e.g.' in element.text):
            element.text = element.text.replace('i.e.', 'i.e.,').replace('e.g.', 'e.g.,')

        for child in element:
            self.change_text(child)

    def modify_xml(self,input_file,output_file):
        #Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        #Replace 'dept' with 'department' in text
        self.change_text(root)

        #Save the modified XML to a new file
        tree.write(output_file)

        print(f"The modified XML file has been saved as '{output_file}'.")

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

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

    

    def find_reference(self, element):
        if element.text:
            change_ref = index.TSP_ref(element.get('id'), element.text, "ieee")
            # print(f"Changed Reference: {change_ref}")
            # print(change_ref)
            print(change_ref)
            soup = ET.fromstring(change_ref)
            element.clear()
            element.append(soup)

    #Find the tags in xml and replace the content
    def change_text(self, element, nlp):
        # print(element.text,"----",element.tail,element)

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        # print(data)

        #Find the reference text in ref tag
        if element.tag == "ref":
            self.find_reference(element)

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

xml_modifier = TSP_styles()
xml_modifier.modify_xml("output/TSP_CMC_54886.xml","output/TSP_CMC_54886.xml")

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

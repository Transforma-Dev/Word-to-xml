import xml.etree.ElementTree as ET
import os
import sys
import json
import re

class TSP_styles:

    # Change text content and tail in the XML tree
    def change_text(self, element):

        #from journal load the json file
        with open("json_folder/TSP_styles.json",'r') as file:
            data = json.load(file)
        
        fn_elements = element.findall(".//fn")
        fn_group = element.find(".//fn-group")
        
        if fn_group is not None:
            funding = availability = author = conflict = ethics = None
            for fn in fn_elements:
                bold = fn.find("./p/bold")
                p = fn.find("./p")
                if bold is not None and bold.text:
                    if "Funding" in bold.text.strip():
                        funding = fn
                        # bold.tail = "kdngjsij byf"
                    elif "Author" in bold.text.strip():
                        author = fn
                    elif "Availability" in bold.text.strip():
                        availability = fn
                    elif "Conflicts" in bold.text.strip():
                        conflict = fn
                    elif "Ethics" in bold.text.strip():
                        ethics = fn
                
            if funding:
                fn_group.remove(funding)
                fn_group.append(funding)
            if author:
                fn_group.remove(author)
                fn_group.append(author)
            if availability:
                fn_group.remove(availability)
                fn_group.append(availability)
            if conflict:
                fn_group.remove(conflict)
                fn_group.append(conflict)
            if ethics:
                fn_group.remove(ethics)
                fn_group.append(ethics)

        for child in element:
            self.change_text(child)

    def modify_xml(self, input_file, output_file):
        # Load the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Call change_text to update text content and tail
        self.change_text(root)

        # Save the modified XML to a new file
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"The modified XML file has been saved as '{output_file}'.")

if __name__ == "__main__":
    # Get file name using command line argument
    command_arg = sys.argv[1]
    input_file_name = os.path.basename(command_arg) if "/" in command_arg else command_arg

    # Get the directory of the script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_directory, "output", input_file_name)

    # Output folder name
    output_file = 'output.xml'

    # Create object for class TSP_styles
    xml_modifier = TSP_styles()
    xml_modifier.modify_xml(input_file, output_file)

#import neccessary librarys
import xml.etree.ElementTree as ET
import re
   
   
#Replace specific text in a sentence based on the provided data.
def replace_text(element, data, logger):
    
    try:
        #Replace text
        for i in data["replace_text"]:
            pattern = fr"{re.escape(i['text'])},*"
            if element.text and i["text"] in element.text:
                element.text = re.sub(pattern, f'{i["replace"]}', element.text)
            if element.tail and i["text"] in element.tail:
                element.text = re.sub(pattern, f'{i["replace"]}', element.text)
            
    except Exception as e:
        print(f"Error in (replace_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (replace_text function) (common_styles.py)-file {e}")

#Add spaces before and after arithmetic operators in the sentence.  
def space_add_text(element, data, logger):
    
    try:
        #Replace and add space text
        for i in data["space_add_text"]:
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f' {i} ', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f' {i} ', element.tail)
            
    except Exception as e:
        print(f"Error in (space_add_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_add_text function) (common_styles.py)-file {e}")

#Remove spaces before and after special characters in the sentence.
def space_remove_text(element, data, logger):
    
    try:
        #Replace and remove space text
        for i in data["space_remove_text"]:     #https://github.com/Transforma-Dev/Word-to-xml/issues/21#issue-2385187570
            pattern = fr"\s*\{i}\s*"
            if element.text and i in element.text:
                element.text = re.sub(pattern, f'{i}', element.text)
            if element.tail and i in element.tail:
                element.tail = re.sub(pattern, f'{i}', element.tail)
    except Exception as e:
        print(f"Error in (space_remove_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_remove_text function) (common_styles.py)-file {e}")
            
#Add a space before specific units like 'm', 'kg', 'cm', 'k', etc., in the sentence.
def space_before_text(element, data, logger):
    
    try:
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
    except Exception as e:
        print(f"Error in (space_before_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_before_text function) (common_styles.py)-file {e}")

#Add a space after specific words like 'no.' in the sentence.
def space_after_text(element, data, logger):
    
    try:
        # Replace and add space only after text
        for i in data["space_after_text"]:
            def func2(elem):
                pattern = fr"{i}\s*\d"
                matchs = re.findall(pattern, elem, re.IGNORECASE)
                if matchs:
                    for match in matchs:
                        mat = match.split(i)
                        elem = elem.replace(match, f'{i} {mat[-1].strip()}')
                return elem 
            
            if element.text and i in element.text.lower():
                element.text = func2(element.text)

            if element.tail and i in element.tail.lower():
                element.tail = func2(element.tail)
    except Exception as e:
        print(f"Error in (space_after_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (space_after_text function) (common_styles.py)-file {e}")
            
#Remove a space before specific words like '℃' in the sentence.
def remove_space_before_text(element, data, logger):
    
    try:
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
    except Exception as e:
        print(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (remove_space_before_text function) (common_styles.py)-file {e}")
       
# Add comma and and in continues sentence     
def add_and(element, data, logger):
    
    try:
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
    except Exception as e:
        print(f"Error in (add_and function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (add_and function) (common_styles.py)-file {e}")
            
#Find the repeated text with unit and get the same unit name remove them and add unit in last of the string
def add_all(element, data, logger):
    
    try:
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
    except Exception as e:
        print(f"Error in (add_all function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (add_all function) (common_styles.py)-file {e}")
            
#Chnage the SI_unit minutes,seconds,hours with min,s,h
def si_units(element, data, logger):
    
    try:
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
    except Exception as e:
        print(f"Error in (si_units function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (si_units function) (common_styles.py)-file {e}")

# Remove the ref or refs text present in middle of the paragraph
# https://github.com/Transforma-Dev/Word-to-xml/issues/20#issue-2385186827
def remove_ref(element, data, logger):
    
    try:
        pattern = r"\w\sRefs*\s"
        if element.text is not None:
            match = re.findall(pattern, element.text, re.IGNORECASE)
            if match:
                element.text = re.sub(match[0], match[0][:2], element.text)
        if element.tail is not None:
            match = re.findall(pattern, element.tail, re.IGNORECASE)
            if match:
                element.tail = re.sub(match[0], match[0][:2], element.tail)
    except Exception as e:
        print(f"Error in (remove_ref function) (common_styles.py)-file {e}")
        #Error log message
        logger.error(f"Error in (remove_ref function) (common_styles.py)-file {e}")
        
#Find the tags in xml and replace the content
def change_text(element, refere, function_name, data, logger):
    
    if element is None:
        return  # Safely handle if element is None

    #Find the reference text in ref tag
    if element.tag == "ref":
        refere = True

    #Replace text or add or remove space in text
    if not refere and element is not None:
        function = globals().get(function_name)
        if function:
            function(element, data, logger)
        else:
            raise ValueError(f"Function '{function_name}' not found.")

    for child in element:
        change_text(child, refere, function_name, data, logger)


# if __name__ == "__main__":
#     import os, sys
#     #Get file name using command line argument
#     command_arg = sys.argv[1]
#     input_file_name = command_arg
    
#     #Get the directory of the python file
#     script_path = os.path.abspath(__file__)
    
#     #Get the directory of the script
#     script_directory = os.path.dirname(script_path)
#     input_file = os.path.join(script_directory, "output",input_file_name)

#     #Output folder name
#     output_file = 'output.xml'
    
#     #Load the XML file
#     tree = ET.parse(input_file)
#     root = tree.getroot()
    
#     refere = False

#     nlp = spacy.load("en_core_web_sm")
    
#     change_text(root, nlp, refere, "add_and")
    
#     tree.write(output_file, encoding='utf-8', xml_declaration=True)
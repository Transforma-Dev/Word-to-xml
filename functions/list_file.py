#Define function to find the List paragraph
def list_para(xml_text,variables,xml,root):
    #Check the numid present in xml 
    num_id = root.find('.//w:numId', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
    
    if num_id is not None:
        list_type = num_id.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
    else:
        text=f'<p>{xml_text}</p>'
        return text
    
    list_type = "order" if int(list_type)==3 else "unorder"    

    if variables["list_count"]==1:
        text=f'<list list-type="{list_type}"><list-item><p>{xml_text}</p></list-item>'
    else:
        text=f'<list-item><p>{xml_text}</p></list-item>'
    
    variables["list_end"]=True
    variables["list_count"]+=1
    #print(text)
    return text

#Define function to find the last list pragraph
def list_close(xml_text,variables,para):
    if len(para.text)!=0:
        xml_text=f'</list><p>{xml_text}</p>'
        variables["list_end"]=False
        variables["list_count"]=1
    else:
        xml_text+=f'</list>'
        variables["list_end"]=False
        variables["list_count"]=1    

    return xml_text
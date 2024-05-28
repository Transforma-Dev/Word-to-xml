#Define function to find the List paragraph
def list_para(xml_text,variables):
    if variables["list_count"]==1:
        text=f'<list list-type="order"><list-item><p>{xml_text}</p></list-item>'
    else:
        text=f'<list-item><p>{xml_text}</p></list-item>'
    
    variables["list_end"]=True
    variables["list_count"]+=1
    #print(text)
    return text


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
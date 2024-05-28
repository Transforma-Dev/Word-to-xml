import re


#Define function to find the figure caption text
def image_caption(xml_text,variables):

    xml_text=xml_text.replace(":","")
    copy_text=xml_text
    xml_text = re.sub(r'<bold>.*?FIGURE.*?</bold>|<bold>.*?\d+\d*.*?</bold>', '', xml_text, flags=re.IGNORECASE)
    path_image=re.findall(r'<graphic[^>]*>', variables["images_path"])
    count_graphic=variables["images_path"].count("graphic")
    text=""
    figure=xml_text
    for i in range(count_graphic):
        if "<" in figure:
            figure=figure.replace("<","&#60;")
        figure=figure.replace("Figure","").replace(str(variables["fig_caption"]),"").replace("Fig","").replace(".","")
        figure = re.sub(r'^\s*\d\d*', '',figure,flags=re.IGNORECASE)
        if ("fig" in copy_text.lower() or copy_text.lower().startswith("(")):
            text+=f'<fig id="fig-{variables["fig_caption"]}"><label>Fig.{variables["fig_caption"]}</label><caption><title>{figure}</title></caption>{path_image[i]}</fig>'
        else:
            text+=f'<fig id="fig-{variables["fig_caption"]}"><label>Fig.{variables["fig_caption"]}</label><caption><title></title></caption>{path_image[i]}</fig>{figure}'
        variables["fig_caption"]+=1
    variables["fig"]=False
    variables["images_path"]=""
    variables["image_find"]=False
    variables["image_next_para"]=False
    #print(text)
    return text


#Define function to find the table heading text
def table_heading(xml_text,variables):
    if ":" in xml_text:
        xml_text=xml_text.split(":")
        text=f'<table-wrap id="table-{variables["table_no"]}"><label>{xml_text[0]}</label><caption><title>{xml_text[1]}</title></caption>'
    else:
        text=f'<table-wrap id="table-{variables["table_no"]}"><label>table</label><caption><title>{xml_text}</title></caption>'

    variables["table_title"]=True
    #print(text)
    return text


def row_col_span(r,c,row,cell,table,li,tt,tr,xml_text):
            
    try:
        #Find the rowspan
        rowspan, colspan = 1, 1
        for merge in range(r + 1, len(table.rows)):
            if table.rows[merge].cells[c].text == cell.text and cell.text!="" :
                rowspan += 1
                tt=True
                li.append((merge,c))
            else:
                break

        #Find the columnspan
        for merge in range(c + 1, len(row.cells)):
            if row.cells[merge].text == cell.text and cell.text!="" :
                colspan += 1
                tr=True
                li.append((r, merge))
            else:
                break            
        #Find the total number of merged cell and append in list for skip the cell
        if tt and tr:
            oo,pp,rr,cc=r,c,rowspan-1,colspan-1
            for k in range(rr):
                th=True
                for l in range(cc):
                    if th:
                        oo+=1
                        th=False
                    pp+=1
                    li.append((oo, pp))
        tt=False
        tr=False
    except:
        print("table")

    #Present first row in th tag other present in td tag
    tag = "th" if r == 0 else "td"
    if colspan == 1 and rowspan == 1:
        xml_text += f"<{tag}>"
    elif colspan > 1 and rowspan == 1:
        xml_text += f"<{tag} colspan='{colspan}'>"
    elif rowspan > 1 and colspan == 1:
        xml_text += f"<{tag} rowspan='{rowspan}'>"
    else:
        xml_text += f"<{tag} rowspan='{rowspan}' colspan='{colspan}'>"
    
    return r,c,row,cell,table,li,tt,tr,xml_text
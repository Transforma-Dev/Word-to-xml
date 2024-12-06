from functions import eq_link
import re


# Define function to find the figure caption text
def image_caption(xml_text, variables):
    copy_text = xml_text
    src = ""
    xml_text = re.sub(r'<bold>|</bold>', '', xml_text, flags=re.IGNORECASE)
    path_image = re.findall(r'<graphic[^>]*>', variables["images_path"])
    src = re.findall(r'<img[^>]*>', variables["images_path"])
    count_graphic = variables["images_path"].count("graphic")
    text = ""
    figure = xml_text
    if count_graphic == 0:
        pattern = r"^((Fig|Figure)((\.|\s)*|\s)+\d+((\.|\s)*|(\:|\s)*|\s)+)(.+)"
        match = re.match(pattern, figure.strip(), re.IGNORECASE)

        if "<disp-formula" in xml_text:
            pattern = r"^((Fig|Figure)((\.|\s)*|\s)+\d+((\:|\s)*|\s)+)(.+)"
            match = re.match(pattern, xml_text, re.IGNORECASE)
            part1 = match.group(1)
            if part1.strip()[-1] == ".":
                part1 = part1.strip()[:-1]

            add_text = figure.replace(part1, "")
            part1 = part1.replace(":", "")

            text += f'<fig id="fig-{variables["fig_caption"]}"><label>{part1}</label><caption><title1>{add_text}</title1></caption>No Image</fig>'
        else:
            if match:
                part1 = match.group(1)
                if part1.strip()[-1] == ".":
                    part1 = part1.strip()[:-1]
                part2 = match.group(7)
                if part2 is None:
                    part2 = match.group(8)
                part2 = part2.replace(":", "")

                text += f'<fig id="fig-{variables["fig_caption"]}"><label>{part1}</label><caption><title1>{part2}</title1></caption>No Image</fig>'
            else:
                figure = eq_link.add_tag(figure)
                text += f'<fig id="fig-{variables["fig_caption"]}"><label>Figure {variables["fig_caption"]}</label><caption><title1></title1></caption>No Image</fig><p>{figure}</p>'
    for i in range(count_graphic):
        pattern = r"^((Fig|Figure)((\.|\s)*|\s)+\d+((\.|\s)*|(\:|\s)*|\s)+)(.+)"
        match = re.match(pattern, figure.strip(), re.IGNORECASE)

        if "<disp-formula" in xml_text:
            pattern = r"^((Fig|Figure)((\.|\s)*|\s)+\d+((\:|\s)*|\s)+)(.+)"
            match = re.match(pattern, xml_text, re.IGNORECASE)

            if match:
                part1 = match.group(1)
                if part1.strip()[-1] == ".":
                    part1 = part1.strip()[:-1]

                add_text = figure.replace(part1, "")
                part1 = part1.replace(":", "")

                text += f'<fig id="fig-{variables["fig_caption"]}"><label>{part1}</label><caption><title1>{add_text}</title1></caption>{path_image[i]}{src[0]}</fig>'
            elif figure.strip().startswith(":"):
                figure1 = figure.strip()[1:]
                text += f'<fig id="fig-{variables["fig_caption"]}"><label>Figure {variables["fig_caption"]}</label><caption><title1>{figure1}</title1></caption>{path_image[i]}{src[0]}</fig>'
            else:
                variables["fig_caption"] = variables["fig_caption"] - 1
                figure = eq_link.add_tag(figure)
                text += f'<fig id="fig-{variables["fig_caption"]}"><label>Figure {variables["fig_caption"]}</label><caption><title1></title1></caption>{path_image[i]}{src[0]}</fig><p>{figure}</p>'

        else:
            if match:
                part1 = match.group(1)
                if part1.strip()[-1] == ".":
                    part1 = part1.strip()[:-1]
                part2 = match.group(7)
                if part2 is None:
                    part2 = match.group(8)
                part2 = part2.replace(":", "")

                text += f'<fig id="fig-{variables["fig_caption"]}"><label>{part1}</label><caption><title1>{part2}</title1></caption>{path_image[i]}{src[0]}</fig>'
            elif figure.strip().startswith(":"):
                figure1 = figure.strip()[1:]
                text += f'<fig id="fig-{variables["fig_caption"]}"><label>Figure {variables["fig_caption"]}</label><caption><title1>{figure1}</title1></caption>{path_image[i]}{src[0]}</fig>'
            else:
                figure = eq_link.add_tag(figure)
                text += f'<fig id="fig-{variables["fig_caption"]}"><label>Figure {variables["fig_caption"]}</label><caption><title1></title1></caption>{path_image[i]}{src[0]}</fig><p>{figure}</p>'

        variables["fig_caption"] += 1
    variables["fig"] = False
    variables["images_path"] = ""
    variables["image_find"] = False
    variables["image_next_para"] = False

    return text


# Define function to find the table heading text
def table_heading(xml_text, variables):
    xml_text = xml_text.replace("<bold>", "").replace("</bold>", "")

    match = re.findall("^Table\s*\w+", xml_text, re.IGNORECASE)
    if match:
        xml_text = xml_text.split(match[0], 1)
        xml_text = re.sub("(^\.|\:)+", "", xml_text[1])

        text = f'<table-wrap id="table-{variables["table_no"]}"><label>{match[0]}</label><caption><title1>{xml_text}</title1></caption>'

    variables["table_title"] = True

    return text


# Find row span and colspan in table
def row_col_span(r, c, row, cell, table, li, tt, tr, xml_text):

    # Find the rowspan
    rowspan, colspan = 1, 1
    for merge in range(r + 1, len(table.rows)):
        if table.rows[merge].cells[c].text == cell.text and cell.text != "":
            rowspan += 1
            tt = True
            li.append((merge, c))
        else:
            break

    # Find the columnspan
    for merge in range(c + 1, len(row.cells)):
        if row.cells[merge].text == cell.text and cell.text != "":
            colspan += 1
            tr = True
            li.append((r, merge))
        else:
            break
    # Find the total number of merged cell and append in list for skip the cell
    if tt and tr:
        oo, pp, rr, cc = r, c, rowspan-1, colspan-1
        for k in range(rr):
            th = True
            for l in range(cc):
                if th:
                    oo += 1
                    th = False
                pp += 1
                li.append((oo, pp))
    tt = False
    tr = False

    # Present first row in th tag other present in td tag
    tag = "th" if r == 0 else "td"
    if colspan == 1 and rowspan == 1:
        xml_text += f"<{tag}>"
    elif colspan > 1 and rowspan == 1:
        xml_text += f"<{tag} colspan='{colspan}'>"
    elif rowspan > 1 and colspan == 1:
        xml_text += f"<{tag} rowspan='{rowspan}'>"
    else:
        xml_text += f"<{tag} rowspan='{rowspan}' colspan='{colspan}'>"

    return r, c, row, cell, table, li, tt, tr, xml_text

from configparser import ConfigParser
from bs4 import BeautifulSoup
import json
import jmespath
ieee_config = json.load(open("ref_json2xml_poc/config_ieee.json"))
# csl_json = json.load(open("inp.json"))

def Add_tag(res, style):
    doi = res[0]["doi_metadata"]

    if doi:
        ref = res[0]["doi_metadata"]
    else:
        ref = res[0]["parsed"]
    not_in_json = []
    csl_json = ref
    def func(k):
        xml_tag = list(k.keys())[0]
        mix = soup.new_tag(xml_tag)
        if "child" in k[xml_tag]:
            for child_item in k[xml_tag]["child"]:
                child_tag = func(child_item)
                mix.append(child_tag)

            # Set value if "value" exists
        if "value" in k[xml_tag]:
            csl_value = k[xml_tag]["value"]
            if csl_value:
                if "." in csl_value or "[" in csl_value:  # For jmespath expressions
                    xml_text = jmespath.search(csl_value, csl_json)
                    if xml_text is not None:
                        mix.string = str(xml_text)
                    else:
                        mix.string = str(csl_value)
                else:
                    xml_text = csl_json.get(csl_value)
                    if xml_text is not None:
                        mix.string = str(xml_text)
                    else:
                        mix.string = str(csl_value)

        # Add attributes if present
        if "attributes" in k[xml_tag]:
            for attribute in k[xml_tag]["attributes"]:
                for attr_key, attr_value in attribute.items():
                    mix[attr_key] = attr_value["value"]
                    xml_text = csl_json.get(attr_value["value"])
                    if xml_text is not None:
                        if attr_value["value"] == "URL":
                            mix[attr_key] = csl_json[attr_value["value"]]
        
        return mix

    soup = BeautifulSoup(features='xml')
    for k in ieee_config:
        root_tag = func(k)
        soup.append(root_tag)

    lpage_tag = soup.find('lpage')

    #If the <lpage> tag exists and its value is lpage string, remove it
    if lpage_tag.string == "lpage":
        lpage_tag.decompose()

    print(soup.prettify())
    return soup.prettify()
        # tag = list(i.keys())[0]
        # # print(tag)
        # label = soup.new_tag(tag)
        # # label.string = references_json[0]["id"]
        # mix.append(label)
        # # print(tag)
        # # csl = i[tag]["value"]
        # for j in i[tag]:
        #     # print(j)
        #     if j == "value":
        #         csl = i[tag]["value"]
        #         if csl:
        #             if "." in csl or "[" in csl:
        #                 xml_text = jmespath.search(csl, csl_json)
        #                 label.string = str(xml_text)
        #             else:
        #                 xml_text = csl_json.get(csl)
        #                 label.string = xml_text

        #     if j == "child":
        #         for id, y in enumerate((i[tag][j])):
        #             in_tag = list(i[tag][j][id].keys())[0]
        #             label1 = soup.new_tag(in_tag)
        #             label.append(label1)
        #             csl = i[tag][j][id][in_tag]["value"]
        #             # print(csl,"--")
        #             # print(in_tag,"===")
        #             if csl:
        #                 if "." in csl or "[" in csl:
        #                     xml_text = jmespath.search(csl, csl_json)
        #                     label1.string = str(xml_text)
        #                 else:
        #                     xml_text = csl_json.get(csl)
        #                     label1.string = xml_text

        #     if j == "attributes":
        #         for id, y in enumerate((i[tag][j])):
        #             in_tag = list(i[tag][j][id].keys())[0]
        #             csl = i[tag][j][id][in_tag]["value"]
        #             label[in_tag] = csl

        # if i[tag]["child"]:
        #     print(i[tag]["child"])
        
        # if csl:
        #     if "." in csl or "[" in csl:
        #         xml_text = jmespath.search(csl, csl_json)
        #     else:
        #         xml_text = csl_json.get(csl)
        #         label.string = xml_text
        # for attribute in attributes:
    # print(soup.prettify())
        # print(tag, xml_text)
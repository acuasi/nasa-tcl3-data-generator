import json
import re
import requests

class SwaggerHubParser():
    def __init__(self, MOP_NAME, json_file="", file_path="", link=""):
        if json_file:
            swaggerHubJSON = json.load(json_file)
        elif file_path:
            swaggerHubJSON = json.load(open(file_path, "r"))
        elif link:
            swaggerHubJSON = self.scrapeSwaggerHubSpec(link)
        else:
            print("The Swaggerhub spec location was not provided!")
            exit()
        if 'definitions' not in swaggerHubJSON or MOP_NAME not in swaggerHubJSON['definitions']:
            print(MOP_NAME, "could not be found in the given JSON!")
            exit()
        self.mopName = MOP_NAME
        self.swaggerHubJSON = swaggerHubJSON
        self.ignoreList = ["required", "description", "example", "format"]
        self.keySwapList = {
            "items": "match",
            "properties": "children",
            "minItems": "minLength",
            "maxItems": "maxLength"
        }
        self.valueSwapList = {
            "string": "str",
            "number": "float|int",
            "object": "dict",
            "array": "list",
            "integer": "int"
        }
        self.validKeywords = ["exception", "exact", "type", "pattern", "minLength", "maxLength", "maximum", "minimum", "enum", "children"]

    def replaceAllReferences(self):
        propertiesJSON = self.swaggerHubJSON['definitions'][self.mopName]['properties']

        def replaceReferences(innerJSON):
            tempJSON = {}
            for key, value in innerJSON.items():
                if key in self.keySwapList.keys():
                    key = self.keySwapList[key]
                if isinstance(value, dict):
                    tempJSON[key] = replaceReferences(value)
                elif key == "$ref":
                    refName = re.search(r"""(?<=#/definitions/).+""", value).group(0)
                    value = replaceReferences(self.swaggerHubJSON['definitions'][refName])
                    # end of the line - $ref is always the only key in its parent's scope
                    return value
                elif key in self.ignoreList:
                    pass
                else:
                    if not isinstance(value, list) and value in self.valueSwapList.keys():
                        value = self.valueSwapList[value]
                    tempJSON[key] = value
            return tempJSON

        return replaceReferences(propertiesJSON)

    def recursivelyFormStructure(self, fullSpec):
        tempJSON = {}
        for key, value in fullSpec.items():
            if isinstance(value, dict):
                noMatchedParams = True
                if key != "match" and "children" in value:
                    tempJSON[key] = self.recursivelyFormStructure(value['children'])
                    continue
                elif key != "match":
                    for validKeyword in self.validKeywords:
                        if validKeyword in value.keys():
                            if "match" in value:
                                value["children"] = {"match": value["match"]}
                                value.pop("match", None)
                            tempJSON[key] = {"match": self.recursivelyFormStructure(value)}
                            noMatchedParams = False
                            break
                if noMatchedParams:
                    tempJSON[key] = self.recursivelyFormStructure(value)
            else:
                tempJSON[key] = value
        return tempJSON


    def parse(self):
        fullSpec = self.replaceAllReferences()
        fullSpec = self.recursivelyFormStructure(fullSpec)
        return fullSpec

    def scrapeSwaggerHubSpec(self, link):
        download_url = link.replace("apis", "apiproxy/schema/file") + "/swagger.json"
        spec_json = requests.get(download_url).json()
        return spec_json


if __name__ == '__main__':
    jsonFile = open("test.json", "r")
    parser = SwaggerHubParser("CNS1_MOP", json_file=jsonFile, file_path="test.json", link="https://app.swaggerhub.com/apis/utm/tcl3-cns/v2")
    spec = parser.parse()

    with open("test_out.json", "w") as jsonWriter:
        jsonWriter.write(json.dumps(spec, indent=4, separators=(',', ': ')))

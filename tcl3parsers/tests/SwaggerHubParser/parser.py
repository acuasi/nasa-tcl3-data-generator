import json
import re


class SwaggerHubParser():
    def __init__(self, swaggerHubFile, MOP_NAME):
        swaggerHubJSON = json.load(swaggerHubFile)
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
            "array": "list"
        }
        self.validKeywords = ["exception", "exact", "type", "pattern", "minLength", "maxLength", "maximum", "minimum", "enum", "children"]

    def replaceAllReferences(self, swagger_json):
        propertiesJSON = swagger_json['definitions'][self.mopName]['properties']

        def replaceReferences(innerJSON):
            tempJSON = {}
            for key, value in innerJSON.items():
                if isinstance(value, dict):
                    if key in self.keySwapList.keys():
                        key = self.keySwapList[key]
                    tempJSON[key] = replaceReferences(value)
                elif key == "$ref":
                    refName = re.search(r"""(?<=#/definitions/).+""", value).group(0)
                    value = replaceReferences(swagger_json['definitions'][refName])
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
                if key != "match":
                    for validKeyword in self.validKeywords:
                        if validKeyword in value.keys():
                            tempJSON[key] = {"match": self.recursivelyFormStructure(value)}
                            noMatchedParams = False
                            break
                if noMatchedParams:
                    tempJSON[key] = self.recursivelyFormStructure(value)
            else:
                tempJSON[key] = value
        return tempJSON


    def parse(self):
        fullSpec = self.replaceAllReferences(self.swaggerHubJSON)
        fullSpec = self.recursivelyFormStructure(fullSpec)
        return fullSpec


if __name__ == '__main__':
    jsonFile = open("test.json", "r")
    parser = SwaggerHubParser(jsonFile, "CNS1_MOP")

    spec = parser.parse()

    with open("test_out.json", "w") as jsonWriter:
        jsonWriter.write(json.dumps(spec, indent=4, separators=(',', ': ')))

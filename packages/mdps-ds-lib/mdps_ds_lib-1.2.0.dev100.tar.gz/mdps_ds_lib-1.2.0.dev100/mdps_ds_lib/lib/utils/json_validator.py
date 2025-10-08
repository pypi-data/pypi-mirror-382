import fastjsonschema


class JsonValidator:
    def __init__(self, schema: dict):
        self.__schema = fastjsonschema.compile(schema)

    def validate(self, input_json: dict):
        try:
            self.__schema(input_json)
            return None
        except Exception as e:
            return str(e)

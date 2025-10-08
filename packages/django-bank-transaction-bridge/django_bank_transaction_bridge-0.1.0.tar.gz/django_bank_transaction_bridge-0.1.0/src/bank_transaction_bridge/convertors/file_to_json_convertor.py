from abc import ABC, abstractmethod
import json
import pandas


class _FileToBridgeJSONConvertor(ABC):
    def __init__(self, file, mapping=None):
        self.file = file
        self.mapping = mapping

    def _mapped_data(self, raw_json_data):
        if not self.mapping:
            return raw_json_data
        output = []
        for raw_data in raw_json_data:
            output.append({})
            for transaction_field_name, raw_field_name in self.mapping.items():
                output[-1][transaction_field_name] = raw_data[raw_field_name]
        return output

    @abstractmethod
    def get_json_data(self) -> list[dict]:
        pass


class CSVFielToBridgeJSONConvertor(_FileToBridgeJSONConvertor):
    def get_json_data(self) -> list[dict]:
        csv = pandas.read_csv(self.file, sep=";")
        raw_json_data = json.loads(csv.to_json(orient="records"))
        return self._mapped_data(raw_json_data)

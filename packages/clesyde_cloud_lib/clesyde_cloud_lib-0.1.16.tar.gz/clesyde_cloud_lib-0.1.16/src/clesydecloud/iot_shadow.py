from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE, )
@dataclass(frozen=True)
class ShadowContent:
    remote_cert_sn: Optional[str] = None

    def extract_existing_keys(self):
        return [key for key in self.__dict__ if self.__dict__[key] is not None]


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass(frozen=True)
class IotShadowUpdate:
    desired: ShadowContent
    delta: ShadowContent


'''
json_str = '{\n  "state": {\n    "desired": {\n      "remoteCertSn": "396318736086317984504724300857618443341278"\n, "machin":"truc"    },\n    "delta": {\n      "remoteCertSn": "396318736086317984504724300857618443341278"\n    }\n  }\n}'
json_obj = json.loads(json_str)

if "state" in json_obj:
    shadow = IotShadowUpdate.from_dict(json_obj["state"])
    print(shadow.desired.extract_existing_keys())
    print(shadow.delta.extract_existing_keys())
'''
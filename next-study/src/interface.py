"""Proposed pure-JSON interface boundary. No pilot tasks or evaluator references."""
import math

class ContractError(ValueError):
    def __init__(self, code):
        self.code=code
        super().__init__(code)

def json_value(value,depth=0):
    if depth>5:raise ContractError('depth_limit')
    if value is None or type(value) in (bool,int):return
    if type(value)is float:
        if not math.isfinite(value):raise ContractError('nonfinite_number')
        return
    if type(value)is str:
        if len(value)>1000:raise ContractError('string_limit')
        return
    if type(value)is list:
        for item in value:json_value(item,depth+1)
        return
    if type(value)is dict:
        for key,item in value.items():
            if type(key)is not str:raise ContractError('nonstring_key')
            json_value(key,depth+1);json_value(item,depth+1)
        return
    raise ContractError('not_json')

def validate_records(records):
    if type(records)is not list:raise ContractError('records_not_list')
    if len(records)>100:raise ContractError('record_limit')
    for record in records:
        if type(record)is not dict:raise ContractError('record_not_object')
        json_value(record)

# Error codes and depth convention are proposals until evaluator agrees and freeze lands.
# No transformation semantics or evaluation tasks are defined here.

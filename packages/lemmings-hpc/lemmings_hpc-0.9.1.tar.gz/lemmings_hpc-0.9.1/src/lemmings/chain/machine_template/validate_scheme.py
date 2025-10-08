import yaml
from jsonschema import validate
from opentea.noob.validate_light import validate_light

with open("cobalt.yml", "r") as fin:
    dict_ = yaml.load(fin, Loader=yaml.FullLoader)

with open("machine_schema.yml", "r") as fin:
    dict_schema = yaml.load(fin, Loader=yaml.FullLoader)


# validate_light(dict_, dict_schema)
validate(dict_, dict_schema)

flagSCHEMA = 0
if flagSCHEMA:
    from genson import SchemaBuilder

    builder = SchemaBuilder(schema_uri="http://json-schema.org/draft-04/schema#")
    builder.add_object(dict_)
    schema = builder.to_schema()

    flagWriteYaml = 0
    if flagWriteYaml:
        with open("test_schema.yml", "w") as yaml_out:
            yaml.dump(schema, yaml_out, indent=2)

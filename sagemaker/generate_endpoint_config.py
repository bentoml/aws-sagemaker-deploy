import json


def generate_endpoint_config(model_name, initial_instance_count, instance_type):
    production_variants = [{
        "VariantName": model_name,
        "ModelName": model_name,
        "InitialInstanceCount": int(initial_instance_count),
        "InstanceType": instance_type
    }]
    return json.dumps(production_variants)

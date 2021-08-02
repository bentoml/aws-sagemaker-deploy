import re


def generate_aws_compatible_string(*items, max_length=63):
    """
    Generate a AWS resource name that is composed from list of string items. This
    function replaces all invalid characters in the given items into '-', and allow user
    to specify the max_length for each part separately by passing the item and its max
    length in a tuple, e.g.:

    >> generate_aws_compatible_string("abc", "def")
    >> 'abc-def'  # concatenate multiple parts

    >> generate_aws_compatible_string("abc_def")
    >> 'abc-def'  # replace invalid chars to '-'

    >> generate_aws_compatible_string(("ab", 1), ("bcd", 2), max_length=4)
    >> 'a-bc'  # trim based on max_length of each part
    """
    trimmed_items = [
        item[0][: item[1]] if type(item) == tuple else item for item in items
    ]
    items = [item[0] if type(item) == tuple else item for item in items]

    for i in range(len(trimmed_items)):
        if len("-".join(items)) <= max_length:
            break
        else:
            items[i] = trimmed_items[i]

    name = "-".join(items)
    if len(name) > max_length:
        raise Exception(
            "AWS resource name {} exceeds maximum length of {}".format(name, max_length)
        )
    invalid_chars = re.compile("[^a-zA-Z0-9-]|_")
    name = re.sub(invalid_chars, "-", name)
    return name


def generate_resource_names(deployment_name, bento_version=""):
    sagemaker_model_repo_name = generate_aws_compatible_string(deployment_name, "repo")
    sagemaker_model_name = generate_aws_compatible_string(
        deployment_name, "model", bento_version
    )
    sagemaker_endpoint_config_name = generate_aws_compatible_string(
        deployment_name, "config"
    )
    sagemaker_endpoint_name = generate_aws_compatible_string(
        deployment_name, "endpoint"
    )

    api_gateway_name = generate_aws_compatible_string(deployment_name, "api")
    return (
        sagemaker_model_repo_name,
        sagemaker_model_name,
        sagemaker_endpoint_config_name,
        sagemaker_endpoint_name,
        api_gateway_name,
    )

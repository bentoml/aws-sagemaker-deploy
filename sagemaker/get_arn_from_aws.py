import boto3


def get_arn_role_from_current_aws_user(sts_arn, iam_role=None):
    sts_arn_list = sts_arn.split(":")
    type_role = sts_arn_list[-1].split("/")
    iam_client = boto3.client("iam")

    if iam_role is not None:
        role_response = iam_client.get_role(RoleName=iam_role)
        return role_response["Role"]["Arn"]
    elif type_role[0] in ("user", "root"):
        role_list = iam_client.list_roles()
        arn = None
        for role in role_list["Roles"]:
            policy_document = role["AssumeRolePolicyDocument"]
            statement = policy_document["Statement"][0]
            if (
                "Service" in statement["Principal"]
                and statement["Effect"] == "Allow"
                and "sagemaker.amazonaws.com" in statement["Principal"]["Service"]
            ):
                arn = role["Arn"]
        if arn is None:
            raise Exception(
                "Can't find proper Arn role for Sagemaker, please create one and try "
                "again"
            )
        return arn
    elif type_role[0] in ["role", "assumed-role"]:
        role_response = iam_client.get_role(RoleName=type_role[1])
        return role_response["Role"]["Arn"]

    raise Exception(
        "Not supported role type {}; sts arn is {}".format(type_role[0], sts_arn)
    )


def get_arn_from_aws(iam_role=None):
    sts_client = boto3.client("sts")
    identity = sts_client.get_caller_identity()
    sts_arn = identity["Arn"]
    account = identity["Account"]
    arn = get_arn_role_from_current_aws_user(sts_arn, iam_role)

    return arn, account

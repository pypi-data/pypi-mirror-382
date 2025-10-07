from troposphere import iam
from troposphere import Parameter
from troposphere import Ref
from troposphere import Sub
from troposphere import Template

from hyperscale.ozone import cfn_nag
from hyperscale.ozone.pipelines import StaxPipeline


class RoleVendingMachine:
    def create_template(self) -> Template:
        template = Template()
        template.set_description("Role Vending Machine")
        self.add_resources(template)
        return template

    def add_resources(self, template: Template) -> None:
        admin_role_arn_param = template.add_parameter(
            Parameter(
                "AdminRoleArn",
                Type="String",
                Description="The ARN of the admin role to use for stack set operations "
                "in the admin account",
            )
        )
        execution_role_name = template.add_parameter(
            Parameter(
                "ExecutionRoleName",
                Type="String",
                Description="The name of the execution role to use for stack set "
                "operations in the target accounts",
            )
        )
        pipelines = StaxPipeline(
            admin_role_arn=admin_role_arn_param,
            execution_role_name=execution_role_name,
        )
        pipelines.add_resources(template)

        template.add_resource(
            iam.Role(
                "RvmMainRole",
                Metadata=cfn_nag.suppress(
                    [
                        cfn_nag.rule(
                            id="W28",
                            reason="Static role name so it can be easily referred to "
                            "in the RVM workflow role policy",
                        )
                    ]
                ),
                RoleName="RvmMainRole",
                AssumeRolePolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "sts:AssumeRole",
                            "Principal": {"Service": "cloudformation.amazonaws.com"},
                            "Condition": {
                                "StringEquals": {
                                    "aws:SourceAccount": Ref("AWS::AccountId")
                                },
                                "ArnLike": {
                                    "aws:SourceArn": Sub(
                                        "arn:${AWS::Partition}:cloudformation:*:${AWS::AccountId}:stackset/pch-role-vending-machine-*"
                                    )
                                },
                            },
                        }
                    ],
                },
                Policies=[
                    iam.Policy(
                        PolicyName="RVMPolicy",
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "sts:AssumeRole",
                                    "Resource": Sub(
                                        "arn:${AWS::Partition}:iam::*:role/RvmWorkflowRole"
                                    ),
                                }
                            ],
                        },
                    )
                ],
            )
        )


class WorkflowRole:
    """
    Role Vending Machine workflow roles that get deployed to each RVM managed account.
    """

    def create_template(self) -> Template:
        template = Template()
        template.set_description(
            "Role Vending Machine workflow roles that get deployed to each RVM "
            "managed account."
        )
        self.add_resources(template)
        return template

    def add_resources(self, template: Template) -> None:
        template.add_parameter(
            Parameter(
                "RvmAccount",
                Type="String",
                Description="The ID of the RVM account",
            )
        )
        template.add_resource(
            iam.Role(
                "RvmWorkflowRole",
                Metadata=cfn_nag.suppress(
                    [
                        cfn_nag.rule("W11", "Need to be able to manage all roles"),
                        cfn_nag.rule(
                            "W28",
                            "Static role name so it can be easily referred to in "
                            "the RVM main role policy",
                        ),
                    ]
                ),
                RoleName="RvmWorkflowRole",
                Description="The role assumed by the RVM Main Role from the RVM "
                "account to vend new roles",
                AssumeRolePolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": Sub(
                                    "arn:${AWS::Partition}:iam::${RvmAccount}:role/RvmMainRole"
                                )
                            },
                            "Action": "sts:AssumeRole",
                        }
                    ],
                },
                Policies=[
                    iam.Policy(
                        PolicyName="AllowManagePermissions",
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:AttachRolePolicy",
                                        "iam:CreateRole",
                                        "iam:CreatePolicy",
                                        "iam:CreatePolicyVersion",
                                        "iam:DeleteRolePolicy",
                                        "iam:DeleteRole",
                                        "iam:DeletePolicy",
                                        "iam:DetachRolePolicy",
                                        "iam:GetPolicy",
                                        "iam:GetPolicyVersion",
                                        "iam:GetRole",
                                        "iam:GetRolePolicy",
                                        "iam:ListAttachedRolePolicies",
                                        "iam:ListRoles",
                                        "iam:ListPolicies",
                                        "iam:UpdateRole",
                                        "iam:PutRolePolicy",
                                        "iam:SetDefaultPolicyVersion",
                                        "iam:TagRole",
                                    ],
                                    "Resource": "*",
                                }
                            ],
                        },
                    ),
                    iam.Policy(
                        PolicyName="AllowManageRvmStacks",
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "cloudformation:*",
                                    ],
                                    "Resource": "*",
                                },
                            ],
                        },
                    ),
                ],
            )
        )

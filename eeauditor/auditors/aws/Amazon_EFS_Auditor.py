# This file is part of ElectricEye.

# ElectricEye is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ElectricEye is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with ElectricEye.
# If not, see https://github.com/jonrau1/ElectricEye/blob/master/LICENSE.

import boto3
import datetime
from check_register import CheckRegister

registry = CheckRegister()

# import boto3 clients
efs = boto3.client("efs")
# loop through EFS file systems
def describe_file_systems(cache):
    response = cache.get("describe_file_systems")
    if response:
        return response
    cache["describe_file_systems"] = efs.describe_file_systems()
    return cache["describe_file_systems"]


@registry.register_check("efs")
def efs_filesys_encryption_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EFS.1] EFS File Systems should have encryption enabled"""
    response = describe_file_systems(cache)
    myFileSys = response["FileSystems"]
    for filesys in myFileSys:
        encryptionCheck = str(filesys["Encrypted"])
        fileSysId = str(filesys["FileSystemId"])
        fileSysArn = f"arn:{awsPartition}:elasticfilesystem:{awsRegion}:{awsAccountId}:file-system/{fileSysId}"
        # ISO Time
        iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        if encryptionCheck == "False":
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": fileSysArn + "/efs-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": fileSysArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "HIGH"},
                "Confidence": 99,
                "Title": "[EFS.1] EFS File Systems should have encryption enabled",
                "Description": "EFS file system "
                + fileSysId
                + " does not have encryption enabled. EFS file systems cannot be encrypted after creation, consider backing up data and creating a new encrypted file system.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "For EFS encryption information refer to the Data Encryption in EFS section of the Amazon Elastic File System User Guide",
                        "Url": "https://docs.aws.amazon.com/efs/latest/ug/encryption.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsElasticFileSystem",
                        "Id": fileSysArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {"Other": {"fileSystemId": fileSysId}},
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3",
                    ],
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE",
            }
            yield finding
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": fileSysArn + "/efs-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": fileSysArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EFS.1] EFS File Systems should have encryption enabled",
                "Description": "EFS file system " + fileSysId + " has encryption enabled.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "For EFS encryption information refer to the Data Encryption in EFS section of the Amazon Elastic File System User Guide",
                        "Url": "https://docs.aws.amazon.com/efs/latest/ug/encryption.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsElasticFileSystem",
                        "Id": fileSysArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {"Other": {"fileSystemId": fileSysId}},
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3",
                    ],
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED",
            }
            yield finding

@registry.register_check("efs")
def efs_filesys_policy_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EFS.2] EFS File Systems should not use the default file system policy"""
    response = describe_file_systems(cache)
    myFileSys = response["FileSystems"]
    for filesys in myFileSys:
        fileSysId = str(filesys["FileSystemId"])
        fileSysArn = f"arn:{awsPartition}:elasticfilesystem:{awsRegion}:{awsAccountId}:file-system/{fileSysId}"
        # ISO Time
        iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        
        try:
            response = efs.describe_file_system_policy(
                FileSystemId=fileSysId
            )
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": fileSysArn + "/efs-policy-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": fileSysArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EFS.2] EFS File Systems should not use the default file system policy",
                "Description": "EFS file system " + fileSysId + " is not using the default file system policy.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "For EFS policies information refer to the Identity and Access Management in EFS section of the Amazon Elastic File System User Guide",
                        "Url": "https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsElasticFileSystem",
                        "Id": fileSysArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {"Other": {"fileSystemId": fileSysId}},
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST CSF PR.AC-1",
                        "NIST CSF PR.AC-4",
                        "NIST SP 800-53 IA-1",
                        "NIST SP 800-53 IA-2",
                        "NIST SP 800-53 IA-5",
                        "AICPA TSC CC6.1",
                        "AICPA TSC CC6.3",
                        "ISO 27001:2013 A.9.1.1",
                        "ISO 27001:2013 A.9.4.1",
                    ],
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED",
            }
            yield finding
        
        except efs.exceptions.FileSystemNotFound:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": fileSysArn + "/efs-policy-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": fileSysArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "MEDIUM"},
                "Confidence": 99,
                "Title": "[EFS.2] EFS File Systems should not use the default file system policy",
                "Description": "EFS file system " + fileSysId + " is using a default file system policy.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "For EFS policies information refer to the Identity and Access Management in EFS section of the Amazon Elastic File System User Guide",
                        "Url": "https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsElasticFileSystem",
                        "Id": fileSysArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {"Other": {"fileSystemId": fileSysId}},
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST CSF PR.AC-1",
                        "NIST CSF PR.AC-4",
                        "NIST SP 800-53 IA-1",
                        "NIST SP 800-53 IA-2",
                        "NIST SP 800-53 IA-5",
                        "AICPA TSC CC6.1",
                        "AICPA TSC CC6.3",
                        "ISO 27001:2013 A.9.1.1",
                        "ISO 27001:2013 A.9.4.1",
                    ],
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE",
            }
            yield finding
        
        except: 
            pass
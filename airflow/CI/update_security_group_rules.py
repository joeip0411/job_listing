import sys

import boto3


def update_emr_security_group_rule(security_group_id, ip_address, direction):
    """
    Update the inbound rule of the specified security group to allow TCP traffic on port 10001.
    """
    ec2 = boto3.client('ec2')

    if direction == 'grant':
        try:
            response = ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 10001,
                        'ToPort': 10001,
                        'IpRanges': [
                            {'CidrIp': f"{ip_address}/32",
                            'Description':'GitHub Action host machine to EMR Spark Thrift',
                            },
                            ],
                    },
                ]
            )
            print("Inbound rule added successfully!")
            return response
        except Exception as e:
            print(f"Failed to add inbound rule: {e}")
            return None
    elif direction =='revoke':
        try:
            response = ec2.revoke_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 10001,
                        'ToPort': 10001,
                        'IpRanges': [
                            {'CidrIp': f"{ip_address}/32"},
                            ],
                    },
                ]
            )
            print("Inbound rule revoked successfully!")
            return response
        except Exception as e:
            print(f"Failed to revoke inbound rule: {e}")
            return None
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_security_group.py <security_group_id> <ip_address> <direction>")
        sys.exit(1)

    security_group_id = sys.argv[1]
    ip_address = sys.argv[2]
    direction = sys.argv[3]
    
    update_emr_security_group_rule(security_group_id, ip_address, direction)

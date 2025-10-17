import boto3
from botocore.exceptions import ClientError

def tag_ec2_instances(instance_ids, tags, region='us-east-1'):
    """
    Tag EC2 instances with given tags.
    
    :param instance_ids: List of EC2 instance IDs to tag
    :param tags: Dictionary of tag key-value pairs
    :param region: AWS region (default: us-east-1)
    """
    ec2 = boto3.client('ec2', region_name=region)

    # Convert dictionary to list of dicts as required by Boto3
    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]

    try:
        response = ec2.create_tags(
            Resources=instance_ids,
            Tags=tag_list
        )
        print(f"Successfully tagged instances: {instance_ids}")
    except ClientError as e:
        print(f"Error tagging instances: {e}")

# === Example usage ===
if __name__ == "__main__":
    # Replace with your actual instance IDs and desired tags
    instance_ids = ['i-0123456789abcdef0', 'i-0fedcba9876543210']
    tags = {
        'Environment': 'Dev',
        'Owner': 'YourName',
        'Project': 'TaggingScript'
    }
    
    tag_ec2_instances(instance_ids, tags, region='us-west-2')


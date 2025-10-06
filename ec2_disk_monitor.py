import shutil
import boto3
import socket
import datetime
import requests
import argparse
import sys
import os

# === Argument parsing ===
parser = argparse.ArgumentParser(description="Send disk usage metric to CloudWatch.")
parser.add_argument("mount_point", help="Mount point to check (e.g. /, /mnt, /data)")
args = parser.parse_args()

mount_point = args.mount_point

# === Validate mount point ===
if not os.path.ismount(mount_point):
    print(f"Error: '{mount_point}' is not a valid mount point.")
    sys.exit(1)

# === EC2 Metadata fetching ===
def get_instance_metadata(path):
    """Fetch metadata from EC2 IMDSv2."""
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        ).text

        response = requests.get(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=2
        )
        return response.text
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None

instance_id = get_instance_metadata("instance-id")
az = get_instance_metadata("placement/availability-zone")
region_name = az[:-1] if az else "us-east-1"

# === Disk usage calculation ===
total, used, free = shutil.disk_usage(mount_point)
usage_percent = round((used / total) * 100, 2)

# === CloudWatch client ===
cloudwatch = boto3.client("cloudwatch", region_name=region_name)

# === Push custom metric ===
response = cloudwatch.put_metric_data(
    Namespace="EC2/DiskUsage",
    MetricData=[
        {
            'MetricName': 'DiskSpaceUtilization',
            'Dimensions': [
                {'Name': 'InstanceId', 'Value': instance_id},
                {'Name': 'MountPath', 'Value': mount_point}
            ],
            'Timestamp': datetime.datetime.utcnow(),
            'Value': usage_percent,
            'Unit': 'Percent'
        }
    ]
)

print(f"[{datetime.datetime.utcnow()}] Sent {usage_percent}% disk usage for {mount_point} on {instance_id} to CloudWatch ({region_name}).")


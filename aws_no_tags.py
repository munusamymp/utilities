import boto3
import csv

regions = [r['RegionName'] for r in boto3.client('ec2').describe_regions()['Regions']]
client = boto3.client('resourcegroupstaggingapi')

untagged_resources = []

for region in regions:
    print(f"Scanning {region}...")
    client = boto3.client('resourcegroupstaggingapi', region_name=region)
    paginator = client.get_paginator('get_resources')

    for page in paginator.paginate():
        for resource in page['ResourceTagMappingList']:
            if len(resource.get('Tags', [])) == 0:
                untagged_resources.append({
                    'Region': region,
                    'ResourceARN': resource['ResourceARN']
                })

# Write results to CSV
with open('untagged_resources.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Region', 'ResourceARN'])
    writer.writeheader()
    writer.writerows(untagged_resources)

print(f"✅ Found {len(untagged_resources)} untagged resources. Saved to untagged_resources.csv")


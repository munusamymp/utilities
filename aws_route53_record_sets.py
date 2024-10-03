import boto3
import pandas as pd

def get_aws_client(service_name):
    """Initialize and return an AWS client for a given service."""
    session = boto3.session.Session()
    return session.client(service_name)

def get_hosted_zone_ids(client):
    """Retrieve and return the list of hosted zone IDs."""
    result = client.list_hosted_zones()
    return [hz['Id'].split('/')[2] for hz in result['HostedZones']]

def get_record_sets(client, hosted_zone_id):
    """Retrieve the record sets for a given hosted zone ID."""
    result = client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
    return result['ResourceRecordSets']

def parse_records(client):
    """Parse the DNS records and return them in a list of dictionaries."""
    final_result = []
    
    for hosted_zone_id in get_hosted_zone_ids(client):
        for record_set in get_record_sets(client, hosted_zone_id):
            record_data = {
                'Name': record_set['Name'],
                'Type': record_set['Type'],
                'TTL': record_set.get('TTL', '-')
            }

            if 'ResourceRecords' in record_set:
                record_data['ResourceRecords'] = ", ".join(
                    record['Value'] for record in record_set['ResourceRecords']
                )
            else:
                record_data['ResourceRecords'] = record_set['AliasTarget']['DNSName']
            
            final_result.append(record_data)

    return final_result

def save_to_excel(records, filename=file_name):
    """Save the parsed DNS records to an Excel file."""
    df = pd.DataFrame(records)
    df.to_excel(filename, index=False)

if __name__ == '__main__':
    client = get_aws_client('route53')
    records = parse_records(client)
    save_to_excel(records, 'dns_record_sets.xlsx')


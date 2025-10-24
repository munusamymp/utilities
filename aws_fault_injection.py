import boto3

# Initialize clients
fis = boto3.client('fis')
elbv2 = boto3.client('elbv2')
ec2 = boto3.client('ec2')

# Step 1: Find target instances behind your Load Balancer
target_group_arn = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-target-group/abc123"

targets = elbv2.describe_target_health(TargetGroupArn=target_group_arn)
instance_ids = [t['Target']['Id'] for t in targets['TargetHealthDescriptions']]
print(f"Target instances: {instance_ids}")

# Step 2: Create the FIS Experiment Template
experiment_template = fis.create_experiment_template(
    description='Fault injection test: stop one instance behind ALB',
    roleArn='arn:aws:iam::123456789012:role/FIS-Experiment-Role',
    stopConditions=[{'source': 'none'}],
    targets={
        'Instances': {
            'resourceType': 'aws:ec2:instance',
            'resourceArns': [f"arn:aws:ec2:us-east-1:123456789012:instance/{instance_ids[0]}"]
        }
    },
    actions={
        'StopInstance': {
            'actionId': 'aws:ec2:stop-instances',
            'parameters': {'startInstancesAfterDuration': 'PT2M'},
            'targets': {'Instances': 'Instances'}
        }
    },
    tags={'Test': 'LoadBalancerFaultInjection'}
)

print(f"Created FIS experiment template: {experiment_template['experimentTemplate']['id']}")

# Step 3: Start the experiment
experiment = fis.start_experiment(experimentTemplateId=experiment_template['experimentTemplate']['id'])
print(f"Started experiment: {experiment['experiment']['id']}")


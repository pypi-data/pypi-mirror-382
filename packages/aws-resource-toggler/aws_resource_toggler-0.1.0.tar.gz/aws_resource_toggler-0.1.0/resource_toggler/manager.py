import boto3
import os
import json
from botocore.exceptions import ClientError

# --- Shared Utilities ---

def get_tag_filters():
    """Reads required tag key/value pairs from environment variables (for Lambda mode)."""
    tag_filters = []
    i = 0
    while True:
        key = os.environ.get(f'TAG_{i}_KEY')
        value = os.environ.get(f'TAG_{i}_VALUE')
        if key and value:
            tag_filters.append({'Key': key, 'Value': value})
            i += 1
        else:
            break
    return tag_filters

def check_tags(resource_tags, required_filters):
    """Checks if a list of resource tags contains ALL required filters."""
    return all(
        any(t.get('Key') == tf['Key'] and t.get('Value') == tf['Value'] for t in resource_tags)
        for tf in required_filters
    )

# --- Helper Function for EC2 Management ---
def manage_ec2_instances(client, tag_filters, results):
    """Finds and toggles the state of EC2 instances based on tags."""
    print("\n--- Processing EC2 Instances ---")
    try:
        # 1. Create Boto3 filters in a single list comprehension
        filters = [{'Name': f'tag:{tf["Key"]}', 'Values': [tf["Value"]]} for tf in tag_filters]
        filters.append({'Name': 'instance-state-name', 'Values': ['running', 'stopped']})

        instance_ids = {'stopped': [], 'running': []}
        
        # 2. Collect instances and categorize by state
        paginator = client.get_paginator('describe_instances')
        for page in paginator.paginate(Filters=filters):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    state = instance['State']['Name']
                    if state in instance_ids:
                        instance_ids[state].append(instance['InstanceId'])
                    else:
                        results['ec2']['no_action'].append(instance['InstanceId'])

        start_ids, stop_ids = instance_ids['stopped'], instance_ids['running']

        if not (start_ids or stop_ids or results['ec2']['no_action']):
            results['ec2']['no_resources_found'] = True
            return

        # 3. Perform actions and update results
        if start_ids:
            client.start_instances(InstanceIds=start_ids)
            results['ec2']['started'].extend(start_ids)
        if stop_ids:
            client.stop_instances(InstanceIds=stop_ids)
            results['ec2']['stopped'].extend(stop_ids)

    except ClientError as e:
        results['ec2']['errors'].append(f"Error managing EC2 instances: {str(e)}")


# --- Helper Function for RDS Management ---
def manage_rds_instances(client, tag_filters, results):
    """Finds and toggles the state of RDS instances based on tags."""
    print("\n--- Processing RDS Instances ---")
    try:
        processed_count = 0
        paginator = client.get_paginator('describe_db_instances')
        
        for page in paginator.paginate():
            for db_instance in page['DBInstances']:
                arn = db_instance['DBInstanceArn']
                db_identifier = db_instance['DBInstanceIdentifier']
                
                # Manual tag check required for RDS
                db_tags = client.list_tags_for_resource(ResourceName=arn)['TagList']
                
                if check_tags(db_tags, tag_filters):
                    processed_count += 1
                    status = db_instance['DBInstanceStatus']
                    
                    try:
                        if status == 'stopped':
                            client.start_db_instance(DBInstanceIdentifier=db_identifier)
                            results['rds']['started'].append(db_identifier)
                        elif status == 'available':
                            client.stop_db_instance(DBInstanceIdentifier=db_identifier)
                            results['rds']['stopped'].append(db_identifier)
                        else:
                            results['rds']['no_action'].append(db_identifier)
                    except ClientError as e:
                        results['rds']['errors'].append(f"Error with RDS instance '{db_identifier}': {str(e)}")

        if processed_count == 0:
            results['rds']['no_resources_found'] = True
                
    except ClientError as e:
        results['rds']['errors'].append(f"Error describing RDS instances: {str(e)}")


# --- Helper Function for ECS Management ---
def manage_ecs_services(client, tag_filters, ecs_desired_count_tag, results):
    """Finds and scales ECS services up or down based on tags."""
    print("\n--- Processing ECS Services ---")
    try:
        processed_count = 0
        
        # 1. Iterate through all clusters
        for cluster_arn in client.list_clusters().get('clusterArns', []):
            cluster_name = cluster_arn.split('/')[-1]
            
            # 2. Paginate through all services in the cluster
            for service_page in client.get_paginator('list_services').paginate(cluster=cluster_arn, schedulingStrategy='REPLICA'):
                if not service_page['serviceArns']: continue
                
                # 3. Describe services to get tags and state
                response = client.describe_services(cluster=cluster_arn, services=service_page['serviceArns'], include=['TAGS'])
                
                for service in response['services']:
                    tags = service.get('tags', [])
                    
                    # 4. Check tags and process action immediately
                    if check_tags(tags, tag_filters):
                        processed_count += 1
                        service_name_full = f"{cluster_name}/{service['serviceName']}"
                        
                        try:
                            desired_count = service['desiredCount']
                            service_arn = service['serviceArn']
                            
                            if desired_count == 0:
                                # Scale UP: Retrieve original count from tag, default to 1
                                original_count = next((int(t['value']) for t in tags if t['key'] == ecs_desired_count_tag), 1)
                                client.update_service(cluster=cluster_arn, service=service_arn, desiredCount=original_count)
                                results['ecs']['scaled_up'].append(f"{service_name_full} (to {original_count})")
                            
                            elif desired_count > 0:
                                # Scale DOWN: Tag resource with current desired count and set to 0
                                # Note: boto3 tag_resource expects [{'key': 'X', 'value': 'Y'}] format
                                tagging_list = [{'key': tf['Key'], 'value': tf['Value']} for tf in tag_filters]
                                tagging_list.append({'key': ecs_desired_count_tag, 'value': str(desired_count)})
                                client.tag_resource(resourceArn=service_arn, tags=tagging_list)
                                
                                client.update_service(cluster=cluster_arn, service=service_arn, desiredCount=0)
                                results['ecs']['scaled_down'].append(f"{service_name_full} (from {desired_count})")
                                
                            else:
                                results['ecs']['no_action'].append(service_name_full)
                                
                        except ClientError as e:
                            results['ecs']['errors'].append(f"Error with ECS service '{service_name_full}': {str(e)}")

        if processed_count == 0:
            results['ecs']['no_resources_found'] = True

    except ClientError as e:
        results['ecs']['errors'].append(f"Error describing ECS clusters/services: {str(e)}")

# --- Library Entry Point ---

def toggle_resources(tag_filters, region=None, ecs_desired_count_tag='OriginalDesiredCount'):
    """
    Manages AWS resources (EC2, RDS, ECS) based on tags and current state.
    
    Args:
        tag_filters (list): A list of dictionaries, e.g., [{'Key': 'Environment', 'Value': 'Dev'}].
        region (str, optional): The AWS region to operate in. If None, uses default Boto3 configuration.
        ecs_desired_count_tag (str): The tag key used to store the original ECS desired count.
        
    Returns:
        dict: A summary report of all actions taken.
    """
    
    if not tag_filters:
        raise ValueError("Tag filters must be provided.")

    filter_str = " AND ".join([f"'{f['Key']}={f['Value']}'" for f in tag_filters])
    print(f"Managing resources with tags in region {region or 'default'}: {filter_str}")

    # Initialize Boto3 clients
    client_config = {'region_name': region} if region else {}
    clients = {
        'ec2': boto3.client('ec2', **client_config), 
        'rds': boto3.client('rds', **client_config), 
        'ecs': boto3.client('ecs', **client_config)
    }

    # Initialize results dictionary
    results = {s: {'started': [], 'stopped': [], 'scaled_up': [], 'scaled_down': [], 'no_action': [], 'no_resources_found': False, 'errors': []} for s in clients}

    manage_ec2_instances(clients['ec2'], tag_filters, results)
    manage_rds_instances(clients['rds'], tag_filters, results)
    manage_ecs_services(clients['ecs'], tag_filters, ecs_desired_count_tag, results)

    # --- Build the final report dictionary ---
    summary_report = {
        service: {
            k: v for k, v in data.items() 
            if v and k not in ['no_resources_found']
        } 
        for service, data in results.items()
    }
    
    # Add 'no_resources_found' status if applicable and no actions were taken
    for service, data in results.items():
        if data['no_resources_found'] and not summary_report.get(service):
             summary_report[service] = {'status': f"No resources found matching the tags {filter_str}."}
             
    return summary_report


# --- Original Lambda Handler (for backward compatibility) ---
def lambda_handler(event, context):
    """
    Orchestrates resource management based on tags from environment variables.
    This remains as the entry point for Lambda deployment.
    """
    
    tag_filters = get_tag_filters()
            
    if not tag_filters:
        print("CRITICAL ERROR: No tag filters defined in environment variables.")
        return {'statusCode': 400, 'body': json.dumps({"error": "No tag filters defined in environment variables."})}

    ECS_DESIRED_COUNT_TAG = os.environ.get('ECS_DESIRED_COUNT_TAG', 'OriginalDesiredCount')

    # Use the new flexible function
    summary_report = toggle_resources(
        tag_filters=tag_filters,
        region=os.environ.get('AWS_REGION'), # Use environment region from Lambda context
        ecs_desired_count_tag=ECS_DESIRED_COUNT_TAG
    )

    # --- Print the summary to logs (for easy viewing in CloudWatch) ---
    print("\n--- FINAL SUMMARY REPORT (LOGS) ---")
    print(json.dumps(summary_report, indent=2))
    
    # --- Return the detailed report as the function's output ---
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(summary_report, indent=2)
    }

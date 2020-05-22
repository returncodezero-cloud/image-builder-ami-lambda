import boto3
from os import environ

client = boto3.client('ec2')

def lambda_handler(event, context):
    # Find launch template
    responseLT = client.describe_launch_templates(
        LaunchTemplateNames=[
            environ['LaunchTemplateName'],
        ]
    )
    LaunchTemplateId = responseLT['LaunchTemplates'][0]['LaunchTemplateId']
    DefaultVersionNumber = responseLT['LaunchTemplates'][0]['DefaultVersionNumber']

    # Describe latest Launch Template version & get current AMI ID used
    responseLTVersion = client.describe_launch_template_versions(
        LaunchTemplateId=LaunchTemplateId,
        Versions=[
            str(DefaultVersionNumber),
        ]
    )
    currLTVersionImageID = responseLTVersion['LaunchTemplateVersions'][0]['LaunchTemplateData']['ImageId']

    # Get latest AMI version
    responseAMI = client.describe_images(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    environ['AMIName'],
                ]
            }
        ]
    )
    amis = sorted(responseAMI['Images'],
              key=lambda x: x['CreationDate'],
              reverse=True)
    latestImageID =  amis[0]['ImageId']

    if currLTVersionImageID != latestImageID:
        print("There is new AMI ID: {}. Template should be updated.".format(latestImageID))
        
        # Create new Launch Template version
        responseCreateLTVersion = client.create_launch_template_version(
            LaunchTemplateId=LaunchTemplateId,
            SourceVersion=str(DefaultVersionNumber),
            LaunchTemplateData={
                'ImageId': latestImageID
            }
        )
        newLTVersion = responseCreateLTVersion['LaunchTemplateVersion']['VersionNumber']
        print("New template version created with number: {}".format(newLTVersion))
        
        # Modify default template version
        responseModifyTPVersion = client.modify_launch_template(
            LaunchTemplateId=LaunchTemplateId,
            DefaultVersion=str(newLTVersion)
        )
        print("Template was modified and newly created version was set as default")
    else:
        print("Latest AMI already used in latest template version.")
    return "Finished."


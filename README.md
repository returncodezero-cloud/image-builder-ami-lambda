# image-builder-ami-lambda
Lambda function to update launch template's latest AMI id when Image Builder Pipeline creates new AMI

As time goes, our AMI images get older, not up to date with latest software and packages we want them to have. Are you manually updating and creating new images? In this article I will explain how we can automate AMI image creation that will be used by our EC2 instances later on (which we also automate).

## Automated pipeline
EC2 Image Builder (Image Pipeline) -> SNS Topic -> Lambda -> EC2 Launch Templates -> Auto Scaling Group

After our AMI images are created, we want to use them. We suppose that our application is using ALB, Target Group and Auto Scaling Group which uses EC2 Launch Template (which includes the AMI). Now we want to automate the process of creating new Launch Template version, which will include our latest AMI image id, so later, new instances launched by Auto Scaling, will use the latest and updated AMI. As you remember, we created SNS topic where EC2 Image Builder Pipeline publishes message when new image is built. So we will subscribe our Lambda function to this SNS topic, so Lambda will be triggered every time a new AMI image is present and it will update our Launch Template with the latest AMI. 

This lambda functions uses 2 environmental variables, where we define the Launch Template Name we want to modify and the AMI Name we defined in our Image Builder Pipeline Output. Example:

AMIName            = TEST-AMI*
LaunchTemplateName = TEST-LT

In order for our Lambda function to interact with the AWS services, we need to create custom managed policy and attach to our Lambda role. This policy is very granule and only provides the API actions we need in order to accomplish the AMI id updating in our Launch Template. 

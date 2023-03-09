## https://t.me/SpatialSurveyBot

# Spatial Survey Bot

## Description
Being inspired by the convenience and functionality of ArcGIS Survey 123,
a spatial data gathering solution for Esri products, the author decided to challenge his
skills by creating another survey solution in the form of a Telegram bot which collects 
coordinates of spatial objects, their text and media description. Collected data can be 
viewed as a Web Map, freely downloaded as a Shapefile or GeoJSON and then can be used 
in any GIS software for further processing and analysis.  

## Usage
Find SpatialSurveyBot in Telegram. Press START (<b>/start</b> 
command can be used anytime to return to the first step of the bot). Then follow the 
prompts: 
- Create Survey (the creator can collect, view and download data, participants have
the collect only permission)
- Set questions for your survey
- Enter the survey name
- Press Collect
- Choose Point or Polygon
- Enter geolocation either manually or using Telegram Location
- Attach media (optional)
- Answer the survey question(s)
- Submit
- Press Map to view the Web Map with collected data, Shapefile or GeoJSON to download data,
or Delete to delete your survey data.

## Technology stack
Python, PostgreSQL & PostGIS, HTML5, JavaScript, Bash

## Deployment
Amazon Web Services.

The author is aware about the serverless architecture in AWS using Amazon API Gateway & 
AWS Lambda. However, to get deeper experience in AWS the classic approach 
was chosen.

- Two Amazon S3 buckets were created. One for connecting the current repository to AWS 
via Amazon CodeDeploy. Another as a media file storage with the proper permissions and
Amazon CloudFront as a CDN. Every bucket has the access point for connecting to a VPC 
via its endpoint.
- The Virtual Private Cloud (VPC) was created in an AWS region with several subnets
in different availability zones (AZ) of the region. The Internet gateway was assigned 
to the VPC. Proper route tables were created and assigned to the subnets
- Amazon RDS PostgreSQL database was created with a subnet group incorporating several
subnets in several AZs
- Proper security groups and IAM roles were created to protect EC2 instances and other
AWS services
- Amazon EC2 Launch Template was fully configured to instantly create a virtual machine
and start the bot on its boot
- Amazon EC2 Auto Scaling group was created (within several AZs) to automatically keep 
the required number of running EC2 instances started from the Launch Template
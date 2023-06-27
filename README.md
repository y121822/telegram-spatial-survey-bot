## https://t.me/SpatialSurveyBot

# Spatial Survey Bot

## Description
Being inspired by the convenience and functionality of ArcGIS Survey 123,
a spatial data gathering solution for Esri products, the author decided to challenge his
skills and create a free survey solution in the form of a Telegram bot, which collects 
coordinates of spatial objects, their text and media description. Collected data can be 
viewed as a Web Map, downloaded as a Shapefile or GeoJSON and then can be used 
in any GIS software for further processing and analysis.  

## Usage
Find SpatialSurveyBot in Telegram. Press START (<b>/start</b> 
command can be used anytime to return to the first step of the bot). Then follow the 
prompts: 
- Create Survey (the creator can collect, view and download data, participants have
the collect only permission). Share the Survey name with your participants if needed.
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

<p align="center">
    <img src="https://d19ehgb5eebwoa.cloudfront.net/output.JPG" alt="ponit & polygon" width="80%">
<br>
Output: Web Map, Shapefile and GeoJSON files
</p>

<p align="center">
    <img src="https://d19ehgb5eebwoa.cloudfront.net/geometries.JPG" alt="ponit & polygon" width="80%">
<br>
Web Map with collected sample data
</p>

<p align="center">
    <img src="https://d19ehgb5eebwoa.cloudfront.net/qgis_loaded.JPG" alt="ponit & polygon" width="80%">
<br>
QGIS: loaded GeoJSON file with collected sample data
</p>

<p align="center">
    <img src="https://d19ehgb5eebwoa.cloudfront.net/point_table.JPG" alt="ponit & polygon" width="80%">
<br>
QGIS: attribute table of a loaded geometry
</p>

## Technology stack
Python, PostgreSQL & PostGIS, HTML5, JavaScript, Bash

## Deployment
Amazon Web Services: S3, VPC, RDS, EC2, EC2 Auto Scaling group


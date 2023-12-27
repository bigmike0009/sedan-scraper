# Sedan Scraper

This is a comissioned data subscription service for a car dealership in Central Florida. Notifies dealership on price and inventory changes in their competitor dealerships.

![Project](https://zak-rentals.s3.amazonaws.com/secaremail.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Infrastructure](#Infrastructure)


## Introduction

This is a python solution deployed to AWS serverless. 
It leverages selenium web scraping, DBFS stored in S3 and  simple email service in order to monitor changes on a car dealership site

## Features

- Inventory state stored in S3 dbfs, allowing additional visibility to customer as needed
- Web driver files are contained in s3 and loaded into the container as a lambda layer
- CICD deployment of web artifacts as well as AWS lambda
- Serverless instances of selenium webscraper that can be spun up and run on automated schedule
- HTML formatted notification email as part of our process
- Cost optimized runtime environment with adjustable scheduling

## Infrastructure

AWS S3 is used for artifact and data storage. 
The code is deployed into AWS lambda where we can scehdule it using Amazon Eventbridge subscriptions.

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
- CICD deployment of web artifacts and python code
- Serverless instances of selenium webscraper are spun up on a schedule
- HTML customizable notification emails
- Cost optimized runtime environment with adjustable scheduling

## Infrastructure

AWS S3 is used for artifact and data storage. 
The code is deployed into AWS lambda where we specify python environment, dependencies, and secret keys
We can schedule lambda runs using Amazon Eventbridge subscriptions.

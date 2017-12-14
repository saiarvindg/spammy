# Spammy
Spammy is an Alexa Skill to keep track of spam numbers.

## Deliverables
[Demo Video](https://www.youtube.com)

[Archtecture Diagram](https://github.com/saiarvindg/spammy/blob/master/SpammyFinalArch.png)

## Inspiration
I wanted a way to keep track of all the spam numbers that called me. Sometimes the same spam number keep calling me and I can't always remember the specific number off the top of my head. So I can just tell Alexa which spam number called me and Alexa will keep track of the number for me.

## Components
#### Amazon Alexa 
A user can ask Alexa to either add a number, delete a number, get a number, or send a spam report/summary. The invocation name is "Spammy".
Examples:
> "Alexa ask Spammy to add 5555555555 as a spam number"

> "Alexa ask Spammy to remove 5555555555 from the list of spam numbers"

> "Alexa ask Spammy if 5555555555 has called me before"

> "Alexa ask Spammy to send me a spam report"

#### AWS Lambda
The Alexa Skill Kit triggers an AWS Lambda function. The Lambda function calls all other AWS services and processes.

#### Amazon DynamoDB
All the numbers and their respective counts are stored in DynamoDB.

#### Amazon Simple Notification Service (SNS)
If the user requests a spam report/summary, then the Lambda function will query the user's DynamoDB table and retrieve all the records. If there are five or less records, then the Lambda function sends the user a text message via SNS.

#### Amazon Simple Email Service (SES)
Similar to the SNS component, however if there are six or more records in ther user's DynamoDB table, then Lambda function send the user a email via SES.

## Challenges
Initially, I wanted to implement a central database table that would store the numbers and count of all number reported by users. However, when I was designing the schema I thought I could use one table for all users by using a map of the user to another map or tuple of the phone number and count. This implementation would allow me to use one table for both all
users and the central database. In turn, I would just have to perform one query (or one set of queries) to get all spam numbers across all users. However, this became more complicated than was I initially expected. So I ended using a different table for each user and using the phone number as the partition/primary key. But in the end, I scrapped the central database as users could mistakenly report a number as spam but in reality the number was not.

In addition, I currently hardcod the phone numbers and email addresses of the example user (me). I wanted to the user link their Amazon account information (giving access to their email and potentially phone number), but the account linking process needed several different resources and services for essentially two pieces of information. I think this issue could be solved by having a the user speak their email address and phone number directly to Alexa and store it in the database. But the email addresses would have to be verified before they are used.

Finally, I wanted to implement mutliple users but intially I could not find a way to uniquely figure out in the Lambda function which user issued a request. So I went ahead and built the application wih just one user and database to get it working. However, towards the end of the project, I realized there is a `userId` field in every Alexa request which identifies the Alexa the request came from. I could use the `userId` field to create a unique table for every users. This is a feature that can implemented easily but will be time consuming as I have to rewrite parts of the Lambda function. I can implement this feature in the future.

## What I learned and next steps
While I theoretically I understood that serverless computing was useful, I never practially understood its usefulness until I did this project. Previously for most of my projects, I had a cloud VPC and I would host my services/server on the VPC. However, the VPC service still required configuration and could be fairly expensive for how much I acutally used it. After using (and understanding) Lambda and other AWS services, it became apparent how easy it was to just think about the code/logic instead of all the configuration. I could just code, hit run, and everything else is taken care of. And I'm only billed for the resources I use.

My next steps are to implement a rudimentary multi-user system using the `userId` field I discovered (too late). Then create phrases the user can speak to Alexa to input their email address and phone number. Finally, I want to integrate this service into a smartphone app that has access to call logs and incoming calls to provide instant feedback on whether the incoming call is a number the user classified as spam.

## Setting up and running the project

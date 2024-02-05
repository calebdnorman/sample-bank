**Senior Engineer Technical Project (Backend)**

This is a friendly coding challenge that should model a real world project you’ll see in the finance space. We are looking for a backend that will stand-up and respond to Postman calls with realistic requests / responses for the functional requirements, and are less concerned about completeness (database persistence, authorization, moving money, etc) under the hood.

A few important notes before we begin,

- The target time spent is 3 hours
  - We are not expecting a fully functional application in this time frame, that would be absurd! 
    - Work on what you think is the most important functionality to display progress, hand wave any fluff (with comments, obviously), and make tradeoffs to complete the functional requirements in the given timeframe.

Some tips,

- Naming and types can communicate more than business logic
  - Utilize classes and function stubbing to hand-wave particular behavior (e.g making a bank transfer)
    - Skip things like AuthZ and AuthN, they’re out of scope and would take far too long

Please do not spend 20 hours building the perfect application.

**Background**

Using a modern RESTful framework (Flask, FastAPI, or Django recommended) and a modern distributed task library (e.g Celery) bootstrap a project of your choice given the following functional requirements.

**Github Repository**

Create a GitHub repository for this project, this will be what you share with us. Be sure to break up your work using commits with descriptions you would use at your typical job. **Don’t commit everything in one go!**

**Problem 1: Technical Requirements**

Using the following information, write a list of ticket titles (no descriptions) to implement the following functional requirements. Create a file  [TICKETS.md ](http://tickets.md/)and push this to your repository.

For example,

1. Create GET /bank/<id>/reimbursements
1. Create POST /reimbursements
1. Create BankingService Class
1. …

**Personas**

class Bank:![](Aspose.Words.4c7be0ca-33bc-45b9-9705-fab3d8d8095b.001.png)

// A bank in our database id: int

uid: uuid

name: str

location: str

class BankAccount:![](Aspose.Words.4c7be0ca-33bc-45b9-9705-fab3d8d8095b.002.png)

`  `id: int

`  `bank\_id: int

`  `bank\_member\_id: int

class BankAdministrator:

// Employee of the bank, manages reimbursements for members id: int

uid: uuid

first\_name: str

last\_name: str

`  `// is there anything missing? adjust as necessary

class BankMember:

// Customer of the bank, submits reimbursements for approval id: int

uid: uuid

first\_name: str

last\_name: str

`  `// is there anything missing? adjust as necessary

**Functional requirements**

As a member of the bank, I can:

- submit a reimbursement with the following details:
  - Bank account
    - Amount
      - Description
  - receive a confirmation email when my reimbursement is approved by an administrator (NOTE: stub out emailing)
- receive a rejection email when my reimbursement is denied by an administrator 
- fetch a list of submitted reimbursements, with the three details I submitted as well as:
  - the date when the request was initially submitted by the member
    - the request’s current status (either pending, approved, denied)

As a bank administrator, I can:

- fetch a list of reimbursements for a particular bank
  - filter to see which reimbursements have a pending status (have not yet been approved or denied by an administrator)
- approve or deny a pending reimbursement request

**Problem 2: Build a Backend**

Using the tickets from the previous problem and a modern REST framework, implement CRUD endpoints to fulfill the required functional requirements. Use the basics from an asynchronous task library (e.g Celery) to stub out code that you would offload from the REST endpoints.

- Backend code should be under a  backend/ subdirectory
  - Write models for the above functionality, making any improvements you see necessary and writing additional models required to process payments successfully
    - Write endpoints (persisting to the database is optional) that perform the required actions
- Write unit tests for any classes or non-REST functions you wrote (yes, this is also a hint)
  - Write functional tests for any REST endpoints you wrote (feel free to  @patch the database calls if you’re cutting a corner on persistence)
- Don’t forget to test realistic edge cases using  side\_effects or similar functionality
  - Don’t forget a [README.md](http://readme.md/)

**Problem 3: Terraform** 

Using DOKS (Digital Ocean Kubernetes) and Kubernetes providers as a guide, write the **rough** (doesn’t need to work perfectly, but should communicate terraform fundamentals and clean terraform code) Terraform necessary to stand up your applications across development, staging, and production. 

- Terraform code should be under  /infrastructure in your repository
  - Skip VPCs and other components, we’re just looking for code to stand up what you wrote
- Don’t forget a [README.md ](http://readme.md/)

**Submission**

Send us a GitHub link to your personal project. If the project needs to remain private, invite the following emails

- kaleb@jawntpass.com![](Aspose.Words.4c7be0ca-33bc-45b9-9705-fab3d8d8095b.003.png)
  - <garrett@jawntpass.com>![](Aspose.Words.4c7be0ca-33bc-45b9-9705-fab3d8d8095b.004.png)

Your project should have,

- TICKETS.md
  - Backend ( backend/ )
    - Infrastructure ( infrastructure/ )
      - README.md
        - High level summary
          - Instructions for running project

Afterwards, we will schedule a series of calls to review your code, the tradeoffs you made, and ask theoretical questions.
Senior Engineer  Technical Project (Backend) 5

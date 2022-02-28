![logo](https://github.com/maticha84/oc_p12_repository/blob/master/image/logo.png)

# README for Epic Events API
___
## Description
___
This application is a CRM application for an event management company. 

It will essentially allow users to create clients, add contracts to those clients and attach an event per signed contract.
The application leverages API endpoints that will serve the data.
You will find in the Image folder the EDR diagram to understand the global architecture of the application. 

The application is accessible to the management team at the following address: http://127.0.0.1:8000/management.

For the sales and support teams, access will only be via the API endpoints. 

The documentation of the endpoints is here <[click](https://documenter.getpostman.com/view/16915168/UVkmRcZd) >(_Made with postman_)


## Entity diagram relationship
___

![EDR](https://github.com/maticha84/oc_p12_repository/blob/master/image/edr.png)

## Installation
___
At first, you have to install python3 (I use the 3.9.6 version). You can find on the official site Python your version for Windows /Linux/ Mac.

Then you need to install a new environment for running the application, containing the packages included in the file requirement.txt .To do this, please follow the instructions below:

Clone this code repository with the command 

`$ git clone clone https://github.com/maticha84/oc_p12_repository.git`  (you can also download the code as a [zip archive](https://github.com/maticha84/oc_p12_repository/archive/refs/heads/master.zip))


Create a virtual environment at the root of the project, using the command `python -m venv env`. Then, activate this environment :

---
    Windows: venv\Scripts\activate.bat
---
    Linux & Mac: source venv/Scripts/activate
---
After that, install the requirement.txt with using this command : `pip install -r requirements.txt`

First, you have to migrate the project using the command bellow to create a new database : 

---
    ../> py manage.py migrate
---
Creating the superuser (user with administrative rights) :
from the terminal > `$ python manage.py createsuperuser`
enter the Email and the password (invisible when typing in the terminal)

Then, go to the root project folder, and run the following command: 

---
    ../> py manage.py runserver
---

It will be start the server to this address : [127.0.0.1:8000](http://127.0.0.1:8080)
Only members of the management team (and the superuser) have access to the django administration console.
The administration page is [here](http://127.0.0.1:8080/management/)
When the server is started, you can use the enpoints of the API, above using the documentation provided below
___
___
## List of endpoints (URI): 
___


|  #  | Endpoints of the CRM API description                                      |  HTTP Method | URI                                        |
|:---:|---------------------------------------------------------------------------|:------------:|:--------------------------------------------|
|  1. | User's registration                                                       |     POST     | /registration/                              |
|  2. | User's connexion                                                          |     POST     | /login/                                     |
|  3. | User's token refresh                                                      |     POST     | /login/refresh/                             |
|  4. | Company's get list                                                        |     GET      | /companies/                                 |
|  5. | Company's get by id                                                       |     GET      | /companies/{id}/                            |
|  6. | Company's creation                                                        |    POST     | /companies/                                 |
|  7. | Company's name modification                                               |     PUT      | /companies/{id}/                            |
|  8. | Company's deletion                                                        |     DELETE   | /companies/{id}/                            |
|  9. | Client's information get list - all clients or by filter                  |     GET      | /clients/                                   |
|  10.| Client's information by id                                                |     GET      | /clients/{id}                               |
|  11.| Client's creation                                                         |     POST     | /companies/{id}/client_by_company/          |
|  12.| Client's modification                                                     |     PUT      | /companies/{id}/client_by_company/{id}/     |
|  13.| Client's deletion                                                         |     DELETE   | /companies/{id}/client_by_company/{id}/     |
|  14.| Contract's information get list - all contracts or by filter              |     GET      | /contracts/                                 |
|  15.| Contract's information by id                                              |     GET      | /contracts/{id}                             |
|  16.| Contract's creation                                                       |     POST     | /clients/{id}/contracts_by_client/          |
|  17.| Contract's modification                                                   |     PUT      | /clients/{id}/contracts_by_client/{id}/     |
|  18.| Contract's deletion                                                       |     DELETE   | /clients/{id}/contracts_by_client/{id}/     |
|  19.| Event's information get list - all contracts or by filter                 |     GET      | /events/                                    |
|  20.| Event's information by id                                                 |     GET      | /events/{id}                                |
|  21.| Event's creation                                                          |     POST     | /contracts/{id}/event_by_contract/          |
|  22.| Event's modification                                                      |     PUT      | /contracts/{id}/event_by_contract/{id}/     |
|  23.| Event's deletion                                                          |     DELETE   | /contracts/{id}/event_by_contract/{id}/     |

|  #  | Filters for /clients/                     | HTTP Method  |    URI                                           |
|:---:|-------------------------------------------|:------------:|:-------------------------------------------------|
|  1. | Search by company name                    | GET          |    /clients/?company_name=_partial_company_name_ |
|  2. | Search by client email                    | GET          |    /clients/?email=_exact_email_                 |


|  #  | Filters for /contracts/                   | HTTP Method  |    URI                                            |
|:---:|-------------------------------------------|:------------:|:--------------------------------------------------|
|  1. | Search by company name                    |  GET         |    /contracts/?company_name=_partial_company_name_|
|  2. | Search by client email                    |  GET         |    /contracts/?email=_exact_email_                |
|  3. | Search by date of contract                |  GET         |    /contracts/?date_contract=_yyyy-mm-dd_         |
|  4. | Search by amount                          |  GET         |    /contracts/?amount=_0123456789_                |


|  #  | Filters for /events/                      | HTTP Method  |    URI                                            |
|:---:|-------------------------------------------|:------------:|:--------------------------------------------------|
|  1. | Search by company name                    |  GET         |    /events/?company_name=_partial_company_name_   |
|  2. | Search by client email                    |  GET         |    /events/?email=_exact_email_                   |
|  3. | Search by date of events                  |  GET         |    /events/?date_event=_yyyy-mm-dd_               |

You will find the [Postman documentation here](https://documenter.getpostman.com/view/16915168/UVkmRcZd).


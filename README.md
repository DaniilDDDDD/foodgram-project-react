# Foodgram
Product assistant
Users can post here their recipes, tag them, add recipes to favourites, add recipes to shopping cart and easily get file with shopping list. 

## Getting Started
Clone repository with project from [GitHub](https://github.com/DaniilDDDDD/foodgram-project-react.git).
Create ```.env``` file with environment variables settings. Something like that:

```
SECRET_KEY=3=r6q=h=n!&j2y8rg4rf1vr)6we0rc5^^)j=n03qg6x*q*jewri9
ALLOWED_HOSTS=*
DEBUG=True

# парамметры для базы данных
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=qwerty1234
DB_HOST=db
DB_PORT=5432
```
Activate Docker on your computer.
Open command line, go to the folder ```infra``` of the project and write:
```
docker-compose up --build -d
```
Project is active
You can choose ports in file docker-compose.yaml

### Prerequisites

Install Docker using official [cite](https://www.docker.com/products/docker-desktop)

### Deployment

To create superuser you can enter container 
```docker exec -it <CONTAINER ID> bash```
Then activate virtual environment, go to the root folder of the project and write the same as in [Django-docs](https://docs.djangoproject.com/en/3.1/topics/auth/default/#creating-superusers)
### Authors

* **Daniil Panyushin** - *Initial work* - [DaniilDDDDD](https://github.com/DaniilDDDDD)
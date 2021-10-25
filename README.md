# Foodgram
Product assistant

Server's address with working application: 34.88.21.167

Users can post here their recipes, tag them, add recipes to "favourites", add recipes to shopping cart and easily get file with shopping list. 

##Getting Started
Fork repository with project from [GitHub](https://github.com/DaniilDDDDD/foodgram-project-react.git).
Create ```.env``` file with environment variables settings. Something like that:

```
SECRET_KEY=3=r6q=h=n!&j2y8rg4rf1vr)6we0rc5^^)j=n03qg6x*q*jewri9
ALLOWED_HOSTS=*
DEBUG=True

# database configuration
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

##Prerequisites

Install Docker using official [cite](https://www.docker.com/products/docker-desktop)

##Deployment

To create superuser you can enter container 
```docker exec -it <CONTAINER ID> bash```
Then activate virtual environment, go to the root folder of the project and write the same as in [Django-docs](https://docs.djangoproject.com/en/3.1/topics/auth/default/#creating-superusers)

##Project's technical task

###Base models

####User
Fields:

* Username - Varchar(200), Unique
* Email - Varchar(200), Unique
* First name - Varchar(200)
* Last name - Varchar(200)
* Password - Varchar(200) - password is stored encrypted
* Role - Varchar(200)
* Last login - Datetime


####Recipe
Fields:

* Author - Foreign key to User model
* Name - Varchar(200)
* Image - Varchar(1000)
* Description - Text
* Tag - Foreign key to Tag model
* Ingredients - Foreign key to RecipeIngredient model
* Cooking time - Integer
* Publication date - Datetime

####Tag
Fields: 

* Name - Varchar(200), Unique
* Color - Varchar(100), Unique
* Slug - Varchar(200), Unique

Tags are preset. Only admin can change list of tags.

####Ingredient
Fields:

* Name - Varchar(200), Unique
* Measurement unit - Varchar(200), Unique

Ingredients are preset. Only admin can change list of ingredients.

####RecipeIngredient
Fields:

* Recipe - Foreign key to Recipe model
* Ingredient - Foreign key to Ingredient model
* Amount - Integer(>=1)

####Favourites
Fields:

* Recipe - Foreign key to Recipe model
* User - Foreign key to User model

####ShoppingCart
Fields:

* Recipe - Foreign key to Recipe model
* User - Foreign key to User model

####Follow
Fields:
* User - Foreign key to User model
* Author - Foreign key to User model

###Services and project's pages
Project's design you can watch [here](https://www.figma.com/file/HHEJ68zF1bCa7Dx8ZsGxFh/Продуктовый-помощник-(Final)?node-id=0%3A1).

####Home page
Home Page Content is a list of the first six recipes sorted by publication date (newest to oldest). The rest of recipes are available on the following pages: there is a pagination at the bottom of the page.

####Recipe page
The page provides a complete description of the recipe. For authorized users - ability to add a recipe to favorites and to shopping list, ability to subscribe to author of the recipe. Recipe's author can change recipe data.

####User's profile
On page - username, all recipes posted by this user and possibility to subscribe the user.

####Subscribing to Authors
Subscription to publications is available only to an authorized user. Subscription page is only available to the owner.
User behavior scenario:
* User goes to another user's page or to the recipe page and subscribes to the author's publications by clicking on the "Subscribe to author" button.
* User goes to the "My Subscriptions" page and views list of recipes published by authors they subscribed to. Sorting records - by date of publication (from newest to oldest).
* If necessary, user can unsubscribe from the author: he goes to the author's page or to the page of his recipe and clicks “Unsubscribe from the author”.

####Favorites list
Only an authorized user can work with the favorites list. Only the owner of the favorites list can see it.
User behavior scenario:
* User marks one or several recipes by clicking on the "Add to favorites" button.
* User navigates to the Favorites List page and views a personalized list of favorites.
* If necessary, user can remove recipe from the favorites. 

####Shopping list
Working with the shopping list is available to authorized users. The shopping list can only be viewed by its owner.
User behavior scenario:
* User marks one or more recipes by clicking on the "Add to purchases" button.
* User goes to the Shopping list page, where all the recipes added to the list are available. The user clicks the Download List button and receives a file with a summarized list and the amount of required ingredients for all recipes saved in the "Shopping List".
* If necessary, user can remove the recipe from the shopping list.

The shopping list is downloaded in .txt format.
When downloading a shopping list, the ingredients in the resulting list should not be duplicated; if two recipes contain sugar (one recipe has 5 g, the other has 10 g), then there should be one item on the list: Sugar - 15 g.
As a result, the shopping list looks like this:
- Minced meat (lamb and beef) (g) - 600
- Processed cheese (g) - 200
- Onions (g) - 50
- Potatoes (g) - 1000
- Milk (ml) - 250
- Chicken egg (pcs) - 5
- Soy sauce (tbsp) - 8
- Sugar (g) - 230
- Refined vegetable oil (tbsp. L.) - 2
- Salt (to taste) - 4
- Black pepper (pinch) - 3

####Filtering by tags
Clicking on a tag name displays a list of recipes marked with this tag. Filtration can be carried out by several tags in the combination "or": if several tags are selected - as a result, recipes should be shown that are marked with at least one of these tags.
When filtering on the user page, only the recipes of the selected user should be filtered. The same principle is followed when filtering the favorites list.

####Registration and authorization
There are of registrations and authorization systems in project.

Required fields for the user:
- Login
- Password
- Email
- Name
- Surname

User access levels:
- Guest (unauthorized user)
- Authorized user
- Administrator

####Unauthorized users' permissions
- Create an account.
- View recipes on the main page.
- View individual recipe pages.
- View user pages.
- Filter recipes by tags.

####Authorized users' permissions
- Log in to the system using your username and password.
- Log out (log out).
- Change your password.
- Create / edit / delete your own recipes
- View recipes on the main page.
- View user pages.
- View individual recipe pages.
- Filter recipes by tags.
- Work with your personal favorites list: add recipes to it or delete them, view your favorites page.
- Work with a personal shopping list: add / delete any recipes, upload a file with the amount of required ingredients for recipes from the shopping list.
- Subscribe to and unsubscribe from recipe authors, view your subscriptions page.

####Admins' permissions
The administrator has all the rights of an authorized user.
Plus, he can:
- change the password of any user,
- create / block / delete user accounts,
- edit / delete any recipes,
- add / remove / edit ingredients.
- add / remove / edit tags.

####Opportunities for functionality extending
It's possible to create filtering by ingredients' composition. For this you must create two more models: "ChemicalElement" and "IngredientComposition". The first model would store information about possible chemical elements of any ingredient. The second one would store chemical composition about every ingredient, stored in Ingredient table.  

## Authors

* **Daniil Panyushin** - *Initial work* - [DaniilDDDDD](https://github.com/DaniilDDDDD)

####Problem: Clicking individual deals is too time consuming and it hard to find out which deal is best for you on craigist. For ex: If I had $4,000, is to better to spend it on 2003 model with 100k miles, or a 2005 model with 130k miles.

*Craigdeals is a proof-of-concept website that shows how these problems could be solved. Craigdeals grabs all the Craigslist car postings in the Bay Area and automatically shows you the best deals. It knows how much each car should be priced, based on the model, year, and mileage. Cars that are priced lower than Craigdeals expects them to be are shown at the top of the list.*

To determine how much each car should be priced, Craigdeals doesn’t use Kelley Blue Book, which tends to overprice cars, especially newer models. Instead, Craigdeals builds its own pricing model based on the actual Craigslist market. In particular, it **uses a Random Forest pricing model because, unlike smooth parametric models, Random Forests are able to detect sharp discontinuities** in prices that may be caused by factors such as manufacturer design overhauls.

By selecting cars that are priced much lower than would be expected based on year and mileage, algorithm picks out some incredible deals, as well as the car with an accident history.Once users are dealing with a handful of posts, they can easily inspect the text of the ad to determine which cars are good deals, and which have a history of accidents.

#####**Hiccups: **
* One of the major challenges was Craiglist constantly blacklisting my IP, as a result collecting data was a pain.
* The backend for this project when I started was in MySQL and when I decided to move it to Heroku and migrating my data from MySQL to PostGres created some hiccups, but all is good in the world now. I will share my learning on what to avoid the problems I faced.
* Heroku does not allow you to make slug files larger than **300MB** and does not support scipy and has to be installed throught thiry party buildpack. The conda buildpack recommended at Heroku website will make the slug size larger than *300MB*. Choosing the right build pack is crucial. I found help by using the **https://github.com/thenovices/heroku-buildpack-scipy**. Hope this helps.

#####**Technology Stack**
* **Backend**: Postgres,Python
* **Fronend**: HTML, CSS, Javascript
* **Visualizatoins**: d3.js
* **Framework**: git, Flask, Heroku

#####**Files**:
* **scraper.py**: scrapes all the listings from craigist and stores them in a data frame with save option and also saves them in a local database.
* **pricer.py**: Implements the pricing model and predicts the price using random forest model based on year,miles and model.
* **utilities.py**: creates tables and schmea bases on data frame
* **requirements.txt**: loads all the build dependencies for the project.
* **models.json**: scrapes listing of the cars modles in the models.json.
* **app.py**: This is the file that the gunicorn runs from the Procfile.


#####**Forking the Repo:**
```
* git init 
* git clone https://github.com/singhpawan/craigdeals.git
* git push origin master    - Push changes to the master branch
```

#####**Pushing to Heroku**
```
* heroku create      - will automatically create a remote named heroku
* git push heroku master
* heroku addons:create heroku-postgresql:hobby-dev      - will create a heroku psql engine with a database url
* heroku open
```

** Since Heroku doesn't support Scipy a third party dependency needs to be installed as a buildpack**
```heroku create --buildpack https://github.com/thenovices/heroku-buildpack-scipy```

######Database Migration: 

I started developing this project locally, since pandas inherently supports MySQL and Sqlite. But doesnot suppor the DBAPI for psql. Hence, I need to use the SQLAlchemy create_engine for the creating hte scraper and the priced tables and dataframe respectively. But for retreiving the results after the pricing modle is executed, create engine does not provide dictCursor, hence I switched back to using DBAPI for connecting to the database to fetch results and return them in a json format for d3.js consumption.

#####**Current Work in Progress:** 
The entries tend to contain a lot of duplicate values and hence need to be removed.when entering a database. Hence will be creating an index on the table.


######Future addons: 
* Writing automation scripts and creatign a staging area for the heroku to test new features.
* Write and explaing curcial parts of the program and the pricing model.
* Craiglist tend to block the IP address when you scrape a couple of hundred listings. The next step is to setup a *cron job every morning which scrapes around 500 listing everyday* so that the ip does not **blacklisted**. The other feature would be addition of more cities and comparing different car prices with each other.


**Contributor:** Pawandeep Singh














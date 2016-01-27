#Problem: Clicking individual deals is too time consuming and it hard to find out which deal is best for you on craigist. For ex: If I had $4,000, is to better to spend it on 2003 model with 100k miles, or a 2005 model with 130k miles.

Craigdeals is a proof-of-concept website that shows how these problems could be solved. Craigdeals grabs all the Craigslist car postings in the Bay Area and automatically shows you the best deals. It knows how much each car should be priced, based on the model, year, and mileage. Cars that are priced lower than Craigdeals expects them to be are shown at the top of the list.

To determine how much each car should be priced, Craigdeals doesn’t use Kelley Blue Book, which tends to overprice cars, especially newer models. Instead, Craigdeals builds its own pricing model based on the actual Craigslist market. In particular, it uses a Random Forest pricing model because, unlike smooth parametric models, Random Forests are able to detect sharp discontinuities in prices that may be caused by factors such as manufacturer design overhauls.

By selecting cars that are priced much lower than would be expected based on year and mileage, algorithm picks out some incredible deals, as well as the car with an accident history.Once users are dealing with a handful of posts, they can easily inspect the text of the ad to determine which cars are good deals, and which have a history of accidents.

Future: Craiglist tend to block the IP address when you scrape a couple of hundred listings. The next step is to setup a cron job every morning which scrapes around 500 listing everyday so that the ip does not blacklisted. The other feature would be addition of more cities and comparing different car prices with each other.


Currnt Work in Progress: The entries tend to contain a lot of duplicate values and hence need to be removed.when entering a database. Hence will be making an index soon.




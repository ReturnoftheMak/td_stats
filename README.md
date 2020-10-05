# td_stats
So I wanted to come up with a way to get the aggregated stats from play cricket, that would also be repeatable for other clubs if possible.

To date I've managed to get some match information, batting records by innings and bowling records by innings. From this you can get some interesting stats like which player was quickest to 1000 runs, which captain has had the longest streak of winning/losing the toss etc.

There are functions to get all the html from the result pages, then convert to json and store. The web scraping is the bottleneck for time, so once the html is loaded additional fields can be extracted using BeautifulSoup.

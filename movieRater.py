import urllib,urllib2, json

def getMovieRating(title, year=-1, returnImdbID=False):
    movieScore = 0

    escapedTitle = urllib.quote(title,'')
    url = "http://www.omdbapi.com/?t=%s" % escapedTitle
    print title,url
    if(year != -1):
        url += "&y=%s" % str(year)
    jsontxt = urllib2.urlopen(url).read()
    data = json.loads(jsontxt)
    # print data

    if(data["Response"] != "True"):
        print "parse error: %s (%s)" % (title, str(year))
        ## TODO: return average rating in this case so we don't
        ## just throw stuff out
        if(returnImdbID): return -1, ""
        else: return -1

    if(data["Type"] != "movie"): 
        print "%s (%s) is not a movie! (maybe the date is wrong)" % (title, str(year))
        if(returnImdbID): return -1, ""
        else: return -1

    year = int(data['Year']) # get correct year if we left it out
    imdbID = data['imdbID']
    rating = data['imdbRating']
    numVotes = data['imdbVotes']
    genres = map(lambda x: x.strip(), data['Genre'].split(","))

    genreScore = 0
    # print genres
    for genre in genres:
        if(genre in ["Action", "Adventure", "Comedy", "Fantasy", "Romance", "Sci-Fi"]):
            genreScore += 1
    movieScore += 0.7*genreScore**2 # add square of matched genres; movies with multiple ones are much better!
    # not fair if there's only one genre like for Borat

    votesScore = int(numVotes.replace(",","")) // 250000 # popularity points
    movieScore += votesScore

    ratingScore = 2.0*(float(rating) - 5.0) # yes, this means it can be negative :)
    movieScore += ratingScore

    if(data['Awards'] != "N/A"):
        movieScore += 1

    if(year < 1970): movieScore -= 5 # screw this crap
    elif(year < 1990): movieScore -= 3 # screw this crap
    elif(year < 2000): movieScore -= 1 # screw this crap

    if(returnImdbID):
        return movieScore, imdbID
    else:
        return movieScore

####### uncomment everything below ONCE to test ranking algorithm

# movies = {
# "The Incredible Journey":[0,1963],
# "All Good Things":[0,2010],
# "Idiocracy":[0,2006],
# "Scarface":[0,1983],
# "Puss in Boots":[0,2011],
# "The Expendables":[0,2010],
# "Captain America: The First Avenger":[0,2011],
# "Top Gun":[0,1986],
# "The Outsiders":[0,1983],
# "Half Nelson":[0,2006],
# "Killer Elite":[0,2011],
# "Secondhand Lions":[0,2003],
# "Titanic":[0,1997],
# "Revolutionary Road":[0,2008],
# "The Waterboy":[0,1998],
# "Public Enemies":[0,2009],
# "The New World":[0,2005],
# "Pathfinder":[0,2007],
# "This Is England":[0,2006],
# "Little Manhattan":[0,2005],
# "The Hunger Games":[0,2012],
# "Pearl Harbor":[0,2001],
# "Transformers":[0,2007],
# "Transformers: Revenge of the Fallen":[0,2009],
# "Transformers: Dark of the Moon":[0,2011],
# "Holes":[0,2003],
# "Green Street Hooligans":[0,2005],
# "Requiem for a Dream":[0,2000],
# "Lord of War":[0,2005],
# "Alexander":[0,2004],
# "U-571":[0,2000],
# "Bad Boys":[0,1983],
# "Valhalla Rising":[0,2009],
# "Solomon Kane":[0,2009],
# "Collateral":[0,2004],
# "Frantic":[0,1988],
# "Taken":[0,2008],
# "Misery":[0,1990],
# "Presumed Innocent":[0,1990],
# "Black Hawk Down":[0,2001],
# "Robin Hood: Prince of Thieves":[0,1991],
# "A Few Good Men":[0,1992],
# "Dances with Wolves":[0,1990],
# "The Ghost and the Darkness":[0,1996],
# "The Frisco Kid":[0,1979],
# "Air Force One":[0,1997],
# "Clear and Present Danger":[0,1994],
# "Patriot Games":[0,1992],
# "The Boy in the Striped Pajamas":[0,2008],
# "Troy":[0,2004],
# "American Graffiti":[0,1973],
# "Premonition":[0,2007],
# "Reservoir Dogs":[0,1992],
# "More American Graffiti":[0,1979],
# "Limitless":[0,2011],
# "Almost Famous":[0,2000],
# "Death Race":[0,2008],
# "The A-Team":[0,2010],
# "The Social Network":[0,2010],
# "Training Day":[0,2001],
# "Disturbia":[0,2007],
# "Rise of the Planet of the Apes":[0,2011],
# "A Guide to Recognizing Your Saints":[0,2006],
# "The Runaways":[0,2010],
# "Apocalypse Now":[0,1979],
# "Knight and Day":[0,2010],
# "127 Hours":[0,2010],
# "Reign Over Me":[0,2007],
# "Flipped":[0,2010],
# "The Kids Are All Right":[0,2010],
# "Inception":[0,2010],
# "Atonement":[0,2007],
# "The Eagle":[0,2011],
# "Fight Club":[0,1999],
# "The Bank Job":[0,2008],
# "Chicago":[0,2002],
# "Eastern Promises":[0,2007],
# "Match Point":[0,2005],
# "Dear Frankie":[0,2004],
# "One Flew Over the Cuckoo's Nest":[0,1975],
# "Moonrise Kingdom":[0,2012],
# "One Day":[0,2011],
# "Batman Begins":[0,2005],
# "Pineapple Express":[0,2008],
# "8 Mile":[0,2002],
# "Rescue Dawn":[0,2006],
# "School of Rock":[0,2003],
# "War of the Worlds":[0,2005],
# "21 Jump Street":[0,2012],
# "True Grit":[0,2010],
# "The Avengers":[0,2012],
# "The Believer":[0,2001],
# "Kill the Irishman":[0,2011],
# "The Adventures of Tintin":[0,2011],
# "K-19: The Widowmaker":[0,2002],
# "Sabrina":[0,1995],
# "Trainspotting":[0,1996],
# "Buffalo Soldiers":[0,2001],
# "That's What I Am":[0,2011],
# "Unknown":[0,2011],
# "Paths of Glory":[0,1957],
# "Unforgiven":[0,1992],
# "Borat: Cultural Learnings of America for Make Benefit Glorious Nation of Kazakhstan":[0,2006],
# "Cowboys & Aliens":[0,2011],
# "Anonymous":[0,2011],
# "The Town":[0,2010],
# "Blue Valentine":[0,2010],
# "Eagle Eye":[0,2008],
# "Butch Cassidy and the Sundance Kid":[0,1969],
# "Virginia":[0,2010],
# "The Ides of March":[0,2011],
# "Quills":[0,2000],
# "Defiance":[0,2008],
# "Sideways":[0,2004],
# "I'm Not There.":[0,2007],
# "Murder by Numbers":[0,2002],
# "Contagion":[0,2011],
# "Hanna":[0,2011],
# "The Tree of Life":[0,2011],
# "To Kill a Mockingbird":[0,1962],
# "Cinderella Man":[0,2005],
# "3:10 to Yuma":[0,2007],
# "Blade Runner":[0,1982],
# "Star Wars: Episode I - The Phantom Menace":[0,1999],
# "Star Wars: Episode II - Attack of the Clones":[0,2002],
# "Walk the Line":[0,2005],
# "Letters from Iwo Jima":[0,2006],
# "I Am Legend":[0,2007],
# "Enemy at the Gates":[0,2001],
# "Fiddler on the Roof":[0,1971],
# "RED":[0,2010],
# "The Road":[0,2009],
# "Cassandra's Dream":[0,2007],
# "Iron Sky":[0,2012],
# "Bolt":[0,2008],
# "The Abyss":[0,1989],
# "The Proposition":[0,2005],
# "Casino":[0,1995],
# "Dazed and Confused":[0,1993],
# "Surf's Up":[0,2007],
# "Avatar":[0,2009],
# "Black Book":[0,2006],
# "The Deer Hunter":[0,1978],
# "The Mechanic":[0,2011],
# "The Proposal":[0,2009],
# "Six Days Seven Nights":[0,1998],
# "Hollywood Homicide":[0,2003],
# "Regarding Henry":[0,1991],
# "Witness":[0,1985],
# "A Good Year":[0,2006],
# "Kingdom of Heaven":[0,2005],
# "The Kingdom":[0,2007],
# "Harsh Times":[0,2005],
# "9":[0,2009],
# "Marie Antoinette":[0,2006],
# "Rango":[0,2011],
# "Die Hard":[0,1988],
# "Die Hard 2":[0,1990],
# "Die Hard: With a Vengeance":[0,1995],
# "Live Free or Die Hard":[0,2007],
# "Immortals":[0,2011],
# "50/50":[0,2011],
# "Chapter 27":[0,2007],
# "Prometheus":[0,2012],
# "Safe House":[0,2012],
# "Conception":[0,2011],
# "Up in the Air":[0,2009],
# "The Departed":[0,2006],
# "The Debt":[0,2010],
# "Easy A":[0,2010],
# "The Shawshank Redemption":[0,1994],
# "Invictus":[0,2009],
# "Your Highness":[0,2011],
# "The Adjustment Bureau":[0,2011],
# "The Perfect Storm":[0,2000],
# "Pirates of the Caribbean: On Stranger Tides":[0,2011],
# "Moneyball":[0,2011],
# "The Fighter":[0,2010],
# "Tinker Tailor Soldier Spy":[0,2011],
# "Looper":[0,2012],
# "You Don't Mess with the Zohan":[0,2008],
# "Scott Pilgrim vs. the World":[0,2010],
# "The Dark Knight Rises":[0,2012],
# "We Were Soldiers":[0,2002],
# "The Expendables 2":[0,2012],
# "Death at a Funeral":[0,2010],
# "Zombieland":[0,2009],
# "The Hobbit: An Unexpected Journey":[0,2012],
# "Traffic":[0,2000],
# "Another Earth":[0,2011],
# "Spun":[0,2002],
# "Killing Them Softly":[0,2012],
# "The Dictator":[0,2012],
# "God Bless America":[0,2011],
# "Beowulf":[0,2007],
# "Se7en":[0,1995],
# "Lincoln":[0,2012],
# "Trust":[0,2010],
# "Iron Man":[0,2008],
# "Django Unchained":[0,2012],
# "Flight":[0,2012],
# "Inglourious Basterds":[0,2009],
# "The Perks of Being a Wallflower":[0,2012],
# "The Blind Side":[0,2009],
# "People Like Us":[0,2012],
# "Seven Psychopaths":[0,2012],
# "The Artist":[0,2011],
# "The Wave":[0,2008],
# "Watchmen":[0,2009],
# "Schindler's List":[0,1993],
# "Minority Report":[0,2002],
# "The Karate Kid":[0,1984],
# "Children of Men":[0,2006],
# "V for Vendetta":[0,2005],
# "Kill Bill: Vol. 1":[0,2003],
# "Kill Bill: Vol. 2":[0,2004],
# "Get the Gringo":[0,2012],
# "Juno":[0,2007],
# "Jackie Brown":[0,1997],
# "The Messenger":[0,2009],
# "Extremely Loud & Incredibly Close":[0,2011],
# "The Good German":[0,2006],
# "Gangs of New York":[0,2002],
# "American Pie":[0,1999],
# "American Pie 2":[0,2001],
# "American Wedding":[0,2003],
# "American Reunion":[0,2012],
# "Pitch Perfect":[0,2012],
# "Ratatouille":[0,2007],
# "Persepolis":[0,2007],
# "Frankenweenie":[0,2012],
# "No Country for Old Men":[0,2007],
# "(500) Days of Summer":[0,2009],
# "We Bought a Zoo":[0,2011],
# "Psycho":[0,1960],
# "To Save a Life":[0,2009],
# "Raging Bull":[0,1980],
# "The Way Back":[0,2010],
# "Lars and the Real Girl":[0,2007],
# "Marley & Me":[0,2008],
# "There Will Be Blood":[0,2007],
# "Hugo":[0,2011],
# "Vision":[0,2009],
# "My Week with Marilyn":[0,2011],
# }

# movieList = []
# nMovies = len(movies.keys())
# i = 0
# for movie in movies:
#     year = movies[movie][1]


#     rating = getMovieRating(movie,year)
#     movieList.append([movie,year,rating])

#     print "[%i/%i] %s (%s) | %.1f" % (i,nMovies,movie,year,rating)
#     i+=1
# # print movieList

# movieList.sort(key=lambda x: x[-1])
# for movie in movieList[::-1]:
#     print "%.1f" % movie[2],movie[0],movie[1]
# # print movieList

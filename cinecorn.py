"""
Set up a database of your movies in a given directory, and generate a bunch of
static HTML to use on the Popcorn Hour interface.

GPLv3
"""
import re
from sqlite3 import connect, OperationalError
from imdb import IMDb

class TestSchema:

    """Test the Schema class"""

    conn = None

    def __init__(self):
        """We want a fresh db to play with each time"""
        self.conn = connect(':memory:')

    def test_init(self):
        """Does the init method actually generate a schema?"""
        try:
            self.conn.execute('SELECT count(*) FROM movies')
            assert False, "Shouldn't get here"
        except OperationalError:
            assert True, "'movies' table doesn't exist"

        Schema(self.conn)
        assert self.conn.execute('SELECT count(*) FROM movies'), \
            "Schema should be successfully created"

    def test_already_exists(self):
        """Does the init choke if the schema already exists?"""
        Schema(self.conn)
        self.conn.execute('SELECT count(*) FROM movies')
        Schema(self.conn)

    def test_add_movie(self):
        """Can we add a movie to the DB?"""
        assert False, "Dummy"

    def test_add_person(self):
        """Can we add a person to the DB?"""
        assert False, "Dummy"

    def test_add_rel_acts(self):
        """Can we add an 'acts' relationship to the DB?"""
        assert False, "Dummy"

    def test_add_rel_directs(self):
        """Can we add a 'directs' relationship to the DB?"""
        assert False, "Dummy"

    def test_add_rel_genre(self):
        """Can we add a 'genre' relationship to the DB?"""
        assert False, "Dummy"

class TestFilesystem:

    """Test the Filesystem class"""

    filesys = None

    def __init__(self):
        """Create a filesystem object"""
        self.filesys = FileSystem(['Aliens.avi', 'Terminator.mkv'])

    def test_get_searches(self):
        """Should get a nice list of search terms from the filesystem"""
        assert len(self.filesys.searches) == 2, \
            "Expect the same number of items as we put in"
        assert self.filesys.searches == ['Aliens', 'Terminator'], \
            "Expect searches to be the inputs without the suffixes"

class TestImdb:

    """Test IMDB search"""

    imdb = None

    def __init__(self):
        """Set up a usable Imdb object"""
        self.imdb = Imdb("The Good, the Bad and the Ugly")

    def test_mid(self):
        """Ensure an expected title"""
        assert self.imdb.mid == "0060196", "Referenced MID"

    def test_title(self):
        """Ensure an expected title"""
        assert self.imdb.title == "Il buono, il brutto, il cattivo.", \
            "Referenced title"

    def test_idx(self):
        """Ensure an expected index (first char)"""
        assert self.imdb.idx == "G", \
            "First letter of search after removing common prefixes"

    def test_year(self):
        """Ensure an expected title"""
        assert self.imdb.year == 1966, "Referenced year"

    def test_runtime(self):
        """Ensure an expected runtime"""
        assert self.imdb.runtime == 161, "Referenced runtime"

    def test_rating(self):
        """Ensure an expected rating"""
        assert self.imdb.rating == 9.0, "Referenced rating"

    def test_summary(self):
        """Ensure an expected summary"""
        assert self.imdb.summary == "A bounty hunting scam joins two men in" \
            + " an uneasy alliance against a third in a race to find a" \
            + " fortune in gold buried in a remote cemetery.", \
            "Referenced summary"

    def test_url_thumb(self):
        """Ensure an expected thumb url"""
        assert self.imdb.url_thumb == "http://ia.media-imdb.com/images/M/" \
            + "MV5BOTg1NTQyNjYzMV5BMl5BanBnXkFtZTYwMzA2MTk4._V1._SX95.jpg", \
            "Referenced thumbnail, with specific width set"

    def test_url_image(self):
        """Ensure an expected image url"""
        assert self.imdb.url_image == "http://ia.media-imdb.com/images/M/" \
            + "MV5BOTg1NTQyNjYzMV5BMl5BanBnXkFtZTYwMzA2MTk4._V1._SX300.jpg", \
            "Reference image with specific width set"

    def test_actors(self):
        """Test the structure of the actors variable"""
        assert isinstance(self.imdb.actors, dict), \
            "We want a dict of id => name pairs"
        pid = self.imdb.actors.keys()[0]
        name = self.imdb.actors.values()[0]

        int(pid)

        try:
            int(name)
            assert False, "Should not occur"
        except ValueError:
            assert True, "This should be a normal string"

    def test_directors(self):
        """Test the structure of the directors variable"""
        assert isinstance(self.imdb.directors, dict), \
            "We want a dict of id => name pairs"
        pid = self.imdb.directors.keys()[0]
        name = self.imdb.directors.values()[0]

        int(pid)

        try:
            int(name)
            assert False, "Should not occur"
        except ValueError:
            assert True, "This should be a normal string"

    def test_genres(self):
        """Test the structure of the genres variable"""
        assert isinstance(self.imdb.genres, list), "A list of genres"
        assert self.imdb.genres == ['Adventure', 'Western'], \
            "Referenced genres"

#TODO:
#
#   add movie to db
#   add people to db
#   add rel_directs to db
#   add rel_acts to db
#   add rel_genre to db
#   download box image
#   generate movie page
#   generate movie listing page
#   generate index page

class Schema:

    """Encapsulate all interactions with the db"""

    def __init__(self, conn):
        """Set up the schema"""
        cur = conn.cursor()
        try:
            cur.execute("""
            CREATE TABLE movies (
                    filename       VARCHAR(255)  PRIMARY KEY,
                    idx            VARCHAR(255)  UNIQUE,
                    mid            CHAR(9)       UNIQUE,
                    image_filename VARCHAR(255)  UNIQUE,
                    thumb_filename VARCHAR(255)  UNIQUE,
                    title          VARCHAR(255),
                    runtime        INT,
                    year           INT,
                    rating         FLOAT,
                    summary        TEXT
            );
            """)

            cur.execute("""
            CREATE TABLE people (
                    pid            CHAR(9)       PRIMARY KEY,
                    name           VARCHAR(255)
            );
            """)

            cur.execute("""
            CREATE TABLE rel_directs (
                    pid            CHAR(9),
                    mid            CHAR(9),
                    PRIMARY KEY(pid, mid)
            );
            """)

            cur.execute("""
            CREATE TABLE rel_acts (
                    pid            CHAR(9),
                    mid            CHAR(9),
                    PRIMARY KEY(pid, mid)
            );
            """)

            cur.execute("""
            CREATE TABLE rel_genres (
                    mid            CHAR(9),
                    genre          VARCHAR(255),
                    PRIMARY KEY(mid, genre)
            );
            """)

            conn.commit()

        except OperationalError:
            conn.rollback()

class FileSystem:

    """Interact with the filesystem"""

    def __init__(self, files):
        """Set up the searches based upon a list of files"""
        self.searches = []

        for filename in files:
            search, _ = filename.rsplit('.', 1)
            self.searches.append(search)

class Imdb:

    """Interact with IMDB"""

    API1_PATTERN = "%s_SX%d.jpg"
    THUMB_X =  95
    IMAGE_X = 300

    def __init__(self, search):
        """Setup up variables and initialize with data from IMDb"""
        self.mid = None
        self.title = None
        self.idx = None
        self.year = None
        self.runtime = None
        self.rating = None
        self.summary = None
        self.url_thumb = None
        self.url_image = None
        self.actors = {}
        self.directors = {}
        self.genres = None

        imdb = IMDb(loggingLevel='warn')
        mov = imdb.search_movie(search)[0]

        self.mid = mov.getID()

        data = imdb.get_movie_main(mov.getID()).items()[1][1]

        self.title = data['title']
        self.idx = re.sub("^(The|A|An|Of|At|On|It's|La|Le|Les|Dos|Los|Der) ",
                          "", search)[0].upper()
        self.year = data['year']
        self.runtime = int(data['runtimes'][0])
        self.rating = data['rating']
        self.summary = data['plot outline']

        self.url_thumb, self.url_image = self.image_urls(data['cover url'])

        for role, lookup in [('cast', self.actors),
                             ('director', self.directors)]:
            for person in data[role]:
                lookup[person.getID()] = person.data['name']

        self.genres = data['genres']

    def image_urls(self, url):
        """Given an IMDB image url return two for pre-set sizes"""
        match = re.match(r"http://.*\._V1\.", url)
        if not match:
            return None, None

        return self.API1_PATTERN % (match.group(0), self.THUMB_X), \
               self.API1_PATTERN % (match.group(0), self.IMAGE_X)


# NOTES
#
#import os
#from imdb import IMDb
#
#MOVIE_DIR = '/share/Movies'
#DB_FILE = 'cinecorn.db'
#
#db = sqlite3.connect(DB_FILE)
#cur = db.cursor()
#
#class Filesystem:
#    def __init__():
#os.listdir(MOVIE_DIR)

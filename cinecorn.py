"""
Set up a database of your movies in a given directory, and generate a bunch of
static HTML to use on the Popcorn Hour interface.

GPLv3
"""
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
        assert False

    def test_add_person(self):
        """Can we add a person to the DB?"""
        assert False

    def test_add_rel_acts(self):
        """Can we add an 'acts' relationship to the DB?"""
        assert False

    def test_add_rel_directs(self):
        """Can we add a 'directs' relationship to the DB?"""
        assert False

    def test_add_rel_genre(self):
        """Can we add a 'genre' relationship to the DB?"""
        assert False

class TestFilesystem:

    """Test the Filesystem class"""

    filesys = None

    def __init__(self):
        """Create a filesystem object"""
        self.filesys = FileSystem(['Aliens.avi', 'Terminator.mkv'])

    def test_get_searches(self):
        """Should get a nice list of search terms from the filesystem"""
        assert len(self.filesys.searches) == 2
        assert self.filesys.searches == ['Aliens', 'Terminator']

class TestImdb:

    """Test IMDB search"""

    imdb = None

    def __init__(self):
        """Set up a usable Imdb object"""
        self.imdb = Imdb("Lost in Translation")

    def test_mid(self):
        """Ensure an expected title"""
        assert self.imdb.mid == "0335266"

    def test_title(self):
        """Ensure an expected title"""
        assert self.imdb.title == "Lost in Translation"

    def test_year(self):
        """Ensure an expected title"""
        assert self.imdb.year == 2003

    def test_actors(self):
        """Test the structure of the actors variable"""
        assert isinstance(self.imdb.actors, dict), """We want a dict of
            id => name pairs"""
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
        assert isinstance(self.imdb.directors, dict), """We want a dict of
            id => name pairs"""
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
        assert self.imdb.genres == ['Drama', 'Romance']

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

    searches = []

    def __init__(self, files):
        for filename in files:
            search, _ = filename.rsplit('.', 1)
            self.searches.append(search)

class Imdb:

    """Interact with IMDB"""

    mid = None
    title = None
    year = None
    actors = {}
    directors = {}
    genres = None

    def __init__(self, search):
        imdb = IMDb(loggingLevel='warn')
        mov = imdb.search_movie(search)[0]

        self.mid = mov.getID()
        self.title = mov.smartCanonicalTitle()

        data = imdb.get_movie_main(mov.getID()).items()[1][1]

        self.year = data['year']

        for role, lookup in [('cast', self.actors),
                             ('director', self.directors)]:
            for person in data[role]:
                lookup[person.getID()] = person.data['name']

        self.genres = data['genres']





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
#
#ia = IMDb()
#m = ia.search_movie(filename)[0]
#m.smartCanonicalTitle
#m.getID()
#
#ia.get_movie_main(m.getID()).items()[1][1].keys()
#
#p = data['cast'][0]
#p.getID()
#p.data['name']
#


"""
Set up a database of your movies in a given directory, and generate a bunch of
static HTML to use on the Popcorn Hour interface.

GPLv3
"""
from sqlite3 import connect, OperationalError

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

    def test_title(self):
        """Ensure an expected title"""
        assert self.imdb.title == "Lost in Translation"

    def test_people(self):
        """Test the structure of the people variable"""
        assert isinstance(self.imdb.people, list), """We want a list of
            id, role, name tuples"""
        pid, role, name = self.imdb.people[0]

        int(pid)

        try:
            int(role)
            assert False, "Should not occur"
        except:
            assert True, "This should be a normal string"

        try:
            int(name)
            assert False, "Should not occur"
        except:
            assert True, "This should be a normal string"

    def test_genres(self):
        """Test the structure of the genres variable"""
        assert isinstance(self.imdb.genres, list), "A list of genres"

#TODO:
#
#   imdb search on term
#   add movie to db
#   add people to db
#   add rel_directs to db
#   add rel_acts to db
#   add rel_genres to db
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

    """ Interact with the filesystem """

    searches = []

    def __init__(self, files):
        for filename in files:
            search, _ = filename.rsplit('.', 1)
            self.searches.append(search)



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


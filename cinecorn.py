"""
Set up a database of your movies in a given directory, and generate a bunch of
static HTML to use on the Popcorn Hour interface.

GPLv3
"""
import re
import os
from sqlite3 import connect, OperationalError
from imdb import IMDb
from urllib import urlretrieve

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
        schema = Schema(self.conn)
        schema.add_movie("The Adam.avi", "A", "001", "foo_small.jpg",
            "foo_big.jpg", "The Adam", 120, 1983, 7.8, "An autobiography.")
        assert self.conn.execute("""SELECT count(1)
                                    FROM movies
                                    WHERE filename=?
                                    AND idx=?
                                    AND mid=?
                                    AND thumb_filename=?
                                    AND image_filename=?
                                    AND title=?
                                    AND runtime=?
                                    AND year=?
                                    AND rating=?
                                    AND summary=?""",
            ("The Adam.avi", "A", "001", "foo_small.jpg", "foo_big.jpg",
                "The Adam", 120, 1983, 7.8, "An autobiography.")).\
                    fetchone() == (1,), \
            "Check that the values are in the DB as expected"

    def test_add_person(self):
        """Can we add a person to the DB?"""
        schema = Schema(self.conn)
        schema.add_person("002", "Adam Piper")
        assert self.conn.execute("""SELECT count(1)
                                    FROM people
                                    WHERE pid=?
                                    AND name=?""",
            ("002", "Adam Piper")).fetchone() == (1,), \
            "Check that the values are in the DB as expected"

    def test_add_rel_acts(self):
        """Can we add an 'acts' relationship to the DB?"""
        schema = Schema(self.conn)
        schema.add_rel_acts("002", "001")
        assert self.conn.execute("""SELECT count(1)
                                    FROM rel_acts
                                    WHERE pid=?
                                    AND mid=?""",
            ("002", "001")).fetchone() == (1,), \
            "Check that the values are in the DB as expected"

    def test_add_rel_directs(self):
        """Can we add a 'directs' relationship to the DB?"""
        schema = Schema(self.conn)
        schema.add_rel_directs("002", "001")
        assert self.conn.execute("""SELECT count(1)
                                    FROM rel_directs
                                    WHERE pid=?
                                    AND mid=?""",
            ("002", "001")).fetchone() == (1,),\
            "Check that the values are in the DB as expected"

    def test_add_rel_genre(self):
        """Can we add a 'genre' relationship to the DB?"""
        schema = Schema(self.conn)
        schema.add_rel_genre("001", "Biography")
        assert self.conn.execute("""SELECT count(1)
                                    FROM rel_genres
                                    WHERE mid=?
                                    AND genre=?""",
            ("001", "Biography")).fetchone() == (1,), \
            "Check that the values are in the DB as expected"

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

class TestWeb:

    """Test the Web class"""

    def test_download_thumb(self):
        """Ensure that downloading a thumb works correctly"""
        ifile = "MV5BOTg1NTQyNjYzMV5BMl5BanBnXkFtZTYwMzA2MTk4._V1._SX95.jpg"
        path = Web.download_thumb("http://ia.media-imdb.com/images/M/" + ifile)
        ipath = os.path.join(Web.THUMB_DIR, ifile)
        assert path == ipath, "Check what we think the path should be"
        assert os.path.exists(path), "Check the returned path for a file"
        os.remove(path)

    def test_download_image(self):
        """Ensure that downloading an image works correctly"""
        ifile = "MV5BOTg1NTQyNjYzMV5BMl5BanBnXkFtZTYwMzA2MTk4._V1._SX300.jpg"
        path = Web.download_image("http://ia.media-imdb.com/images/M/" + ifile)
        ipath = os.path.join(Web.IMAGE_DIR, ifile)
        assert path == ipath, "Check what we think the path should be"
        assert os.path.exists(path), "Check the returned path for a file"
        os.remove(path)

#TODO:
#
#   generate movie page
#   generate movie listing page
#   generate index page
#   split code into modules

class Schema:

    """Encapsulate all interactions with the db"""

    def __init__(self, conn):
        """Set up the schema"""
        self.conn = conn
        cur = self.conn.cursor()
        try:
            cur.execute("""
            CREATE TABLE movies (
                    filename       VARCHAR(255)  PRIMARY KEY,
                    idx            VARCHAR(255)  UNIQUE,
                    mid            CHAR(9)       UNIQUE,
                    thumb_filename VARCHAR(255)  UNIQUE,
                    image_filename VARCHAR(255)  UNIQUE,
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

            self.conn.commit()

        except OperationalError:
            self.conn.rollback()

    def _query(self, query, bindings=None):
        """Execute a single query and return True or False if dupe"""
        try:
            self.conn.execute(query, bindings)
            return True
        except OperationalError:
            self.conn.rollback()
            return False

    def add_movie(self, filename, idx, mid, thumb_filename, image_filename,
                  title, runtime, year, rating, summary):
        """Add a movie to the database"""
        return self._query("""INSERT INTO movies (filename, idx, mid,
                                  thumb_filename, image_filename, title,
                                  runtime, year, rating, summary)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (filename, idx, mid, thumb_filename,
                                  image_filename, title, runtime, year,
                                  rating, summary))

    def add_person(self, pid, name):
        """Add a person to the database"""
        return self._query("""INSERT INTO people (pid, name)
                              VALUES (?, ?)""",
                              (pid, name))

    def add_rel_directs(self, pid, mid):
        """Add a "directs" relationship to the database"""
        return self._query("""INSERT INTO rel_directs (pid, mid)
                              VALUES (?, ?)""",
                              (pid, mid))

    def add_rel_acts(self, pid, mid):
        """Add an "acts" relationship to the database"""
        return self._query("""INSERT INTO rel_acts (pid, mid)
                              VALUES (?, ?)""",
                              (pid, mid))

    def add_rel_genre(self, mid, genre):
        """Add a "genre" relationship to the database"""
        return self._query("""INSERT INTO rel_genres (mid, genre)
                              VALUES (?, ?)""",
                              (mid, genre))

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

class Web:

    """Interact with the web"""

    THUMB_DIR = "thumbs"
    IMAGE_DIR = "images"

    @staticmethod
    def _image_file(out_dir, url):
        return os.path.join(out_dir, url.split("/")[-1])

    @staticmethod
    def download_thumb(url):
        """Download a thumb from a url to an output dir"""
        path = Web._image_file(Web.THUMB_DIR, url)
        urlretrieve(url, path)
        return path

    @staticmethod
    def download_image(url):
        """Download an image from a url to an output dir"""
        path = Web._image_file(Web.IMAGE_DIR, url)
        urlretrieve(url, path)
        return path

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

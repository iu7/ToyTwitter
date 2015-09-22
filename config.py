class Config():
    FRONT_PORT  = 8000
    SESSION_PORT= 8001
    USERS_PORT  = 8002
    FEED_PORT   = 8003
    SEARCH_PORT = 8004
    TEST_PORT   = 8010

    DEFAULT_PAGE        = 1
    DEFAULT_PER_PAGE    = 10

    SALT_LENGTH = 3
    SESSION_EXPIRES = 100000
    MESSAGE_LENGTH = 140

    def load_config(self, front, session, users, feed, search):
        self.FRONT_PORT  = front
        self.SESSION_PORT= session
        self.USERS_PORT  = users
        self.FEED_PORT   = feed
        self.SEARCH_PORT = search

import os
from dotenv import load_dotenv
    
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    RAID_HELPER_API_KEY = os.environ.get('RAID_HELPER_API_KEY') or 'you-will-never-guess'
    
    load_dotenv()

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    POSTS_PER_PAGE = 25
    

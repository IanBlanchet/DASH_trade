import os
from dotenv import load_dotenv
load_dotenv()


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu le devinera pas'
	token = os.environ.get('token')

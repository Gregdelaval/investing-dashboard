import shutil
import os


def on_session_created(session_context):
	shutil.rmtree(os.getenv('PATH_CACHE'), ignore_errors=True)
	os.makedirs(os.getenv('PATH_CACHE'), exist_ok=True)


def on_session_destroyed(session_context):
	shutil.rmtree(os.getenv('PATH_CACHE'), ignore_errors=True)


def on_server_loaded(session_context):
	root = '//'.join(__file__.replace('\\', '//').split('//')[0:-1]) + '//'
	os.environ['PATH_ROOT'] = root
	os.environ['PATH_CACHE'] = root + 'cache//'

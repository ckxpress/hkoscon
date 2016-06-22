import logging
import os
import hashlib
from sqlalchemy.sql import select

from skygear import static_assets
from skygear.container import SkygearContainer
from skygear.utils.assets import relative_assets
from skygear.utils.db import conn, get_table

from .chat import plugin as chat_plugin
from .fb_messager import messager_handler

log = logging.getLogger(__name__)


@static_assets(prefix='demo')
def chat_demo():
    return relative_assets('chat/js-sdk/demo')


@messager_handler('fbwebhook')
def echo(evt, postman):
    sender = evt['sender']['id']
    if not get_user_by_username(sender):
        signup(sender)
    if 'message' in evt:
        msg = evt['message']
        if 'text' in msg:
            r = postman.send(sender, msg['text'])
    log.info('Cat cannot handle')


def get_container(user_id):
    return SkygearContainer(
        api_key=os.getenv('MASTER_KEY'),
        user_id=user_id
    )


def get_user_by_username(fb_id):
    with conn() as c:
        users = get_table('_user')
        stmt = select([users.c.id]) \
            .where(users.c.username == fb_id)
        return c.scalar(stmt)


def signup(user_id):
    container = SkygearContainer(
        api_key=os.getenv('API_KEY')
    )
    pw = hashlib.sha1(bytes(user_id + 'Aih2xoopho', 'utf8')).hexdigest()
    result = container.send_action('auth:signup', {
        'username': user_id,
        'password': pw
    })
    log.debug(result)
    return result['id']

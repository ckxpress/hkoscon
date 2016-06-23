import logging
import os
import hashlib
import uuid
from sqlalchemy.sql import select

import skygear
from skygear import static_assets
from skygear.container import SkygearContainer
from skygear.utils.assets import relative_assets
from skygear.utils.db import conn, get_table

from .chat import plugin as chat_plugin
from .fb_messager import messager_handler

log = logging.getLogger(__name__)

CHAT_BOT_ID = os.getenv('CHAT_BOT_ID', '')


@static_assets(prefix='demo')
def chat_demo():
    return relative_assets('chat/js-sdk/demo')

wdict = {
    'a': 'b',
    'b': 'c'
}


@messager_handler('fbwebhook')
def emoji(evt, postman):
    sender = evt['sender']['id']
    if 'message' in evt:
        msg = evt['message']
        if 'text' in msg:
            body = msg['text']
            for key in wdict:
                body = body.replace(key, wdict[key])
            r = postman.send(sender, body)

def echo(evt, postman):
    sender = evt['sender']['id']
    uid = get_user_by_username(sender)
    if not uid:
        uid = signup(sender)
    log.info(uid)
    if 'message' in evt:
        cid = get_conversation_by_uid(uid)
        if not cid:
            cid = create_conversation(uid)
        msg = evt['message']
        if 'text' in msg:
            body = msg['text']
            create_message(cid, uid, body)
            r = postman.send(sender, body)
    log.info('cat cannot handle')


def create_message(cid, uid, body):
    container = SkygearContainer(
        api_key=os.getenv('MASTER_KEY'),
        user_id=uid
    )
    result = container.send_action('record:save', {
        'records': [{
            '_id': 'message/' + uuid.uuid4().urn[9:],
            'conversation_id': cid,
            'body': body 
        }],
        'database_id': '_private'
    })
    log.info(result)
    return result['result'][0]['_id']


def create_conversation(uid):
    container = SkygearContainer(
        api_key=os.getenv('MASTER_KEY'),
        user_id=uid
    )
    result = container.send_action('record:save', {
        'records': [{
            '_id': 'conversation/' + uid + CHAT_BOT_ID,
            'participant_ids': [uid, CHAT_BOT_ID],
            'is_direct_message': True
        }],
        'database_id': '_public'
    })
    log.info(result)
    return result['result'][0]['_id']


def get_conversation_by_uid(uid):
    with conn() as c:
        conversation = get_table('conversation')
        stmt = select([conversation.c._id]) \
            .where(conversation.c._created_by == uid)
        r = c.execute(stmt).fetchone()
        if r is None:
            return None
        else:
            return r[0]


def get_user_by_username(fb_id):
    with conn() as c:
        users = get_table('_user')
        stmt = select([users.c.id]) \
            .where(users.c.username == fb_id)
        r = c.execute(stmt).fetchone()
        if r is None:
            return None
        else:
            return r[0]


def signup(user_id):
    container = SkygearContainer(
        api_key=os.getenv('API_KEY')
    )
    pw = hashlib.sha1(bytes(user_id + 'Aih2xoopho', 'utf8')).hexdigest()
    result = container.send_action('auth:signup', {
        'username': user_id,
        'password': pw
    })
    log.info(result)
    return result['id']

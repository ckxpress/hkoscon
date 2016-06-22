import logging
from skygear import static_assets
from skygear.utils.assets import relative_assets

from .chat import plugin as chat_plugin
from .fb_messager import messager_handler

log = logging.getLogger(__name__)


@static_assets(prefix='demo')
def chat_demo():
    return relative_assets('chat/js-sdk/demo')


@messager_handler('fbwebhook')
def echo(evt, postman):
    sender = evt['sender']['id']
    if 'message' in evt:
        msg = evt['message']
        if 'text' in msg:
            r = postman.send(sender, msg['text'])
    log.info('Cat cannot handle')

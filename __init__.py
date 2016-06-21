from skygear import static_assets
from skygear.utils.assets import relative_assets

from .chat import plugin as chat_plugin


@static_assets(prefix='demo')
def chat_demo():
    return relative_assets('chat/js-sdk/demo')

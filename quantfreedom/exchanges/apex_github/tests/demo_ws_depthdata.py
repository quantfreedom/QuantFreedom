from time import sleep

from apexpro.constants import APEX_WS_TEST
from apexpro.websocket_api import WebSocket


# Connect with authentication!
ws_client = WebSocket(
    endpoint=APEX_WS_TEST,
)

def depth_data(message):
    showDepthdata(message)


lastDepthData = {}

def _find_index(source,  key):
    """
    Find the index in source list of the targeted ID.
    """
    for item in source:
        if item[0] == key:
            return source.index(item)
    return -1

def showDepthdata(message):
    global lastDepthData
    topic = ''

    if message.get('topic') is not None:
        topic = message.get('topic')

    print("new:",  message)
    if message.get('type') == 'snapshot':
        lastDepthData = message
        print('lastDepthData: ', lastDepthData)
    elif message.get('type') == 'delta':
        if message.get('data').get('u') != lastDepthData.get('data').get('u') + 1:
            ws_client.unsub_depth_topic_stream(depth_data,topic)
            ws_client.depth_topic_stream(depth_data,topic)
        else:
            lastDepthData['u'] = message.get('u')
            if lastDepthData.get('data') is not None and message.get('data') is not None and message.get('data').get('b') is not None:
                for entry in message.get('data').get('b'):
                    index = _find_index(lastDepthData['data']['b'], entry[0])
                    if index == -1:
                        lastDepthData['data']['b'].append(entry)
                    else:
                        lastDepthData['data']['b'][index] = entry
                    if entry[1] == '0':
                        lastDepthData['data']['b'].pop(index)


                items=lastDepthData['data']['b']
                #items.sort()
                sorted(items,key=lambda x:x[0],reverse=False)
            if lastDepthData.get('data') is not None and message.get('data')  is not None and message.get('data').get('a') is not None:
                for entry in message.get('data').get('a'):
                    index = _find_index(lastDepthData['data']['a'], entry[0])
                    if index == -1:
                        lastDepthData['data']['a'].append(entry)
                    else:
                        lastDepthData['data']['a'][index] = entry
                    if entry[1] == '0':
                        lastDepthData['data']['a'].pop(index)


            items=lastDepthData['data']['a']
            #items.sort()
            sorted(items,key=lambda x:x[0],reverse=False)

            print('lastDepthData: ', lastDepthData)
    else:
        ws_client.depth_topic_stream(depth_data,topic)


ws_client.depth_stream(depth_data,'BTCUSDC',25)


while True:
    # Run your main trading logic here.
    sleep(1)

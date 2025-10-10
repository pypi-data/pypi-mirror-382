import logging
from .notification_target import NotificationTarget
from .notification_data import NotificationData
from .notification_center import NotificationCenter


logger = logging.getLogger(__name__)

def _ns_register_client(notification_name, target, userdata=None):
    """
    target should be function with following signature:
    def target_func(notification_name, invoker_data, user_data)
    """

    with NotificationCenter.lock:
        if notification_name not in NotificationCenter.notifications:
            data = NotificationData([])
            NotificationCenter.notifications[notification_name] = data
        else:
            data = NotificationCenter.notifications[notification_name]

        client_id = NotificationCenter.id
        NotificationCenter.id += 1
        data.clients.append(NotificationTarget(
            target=target,
            userdata=userdata,
            id=client_id))
        return client_id

def _ns_send_notification(notification_name, data):
    targets = None
    sent = 0
    with NotificationCenter.lock:
        if notification_name not in NotificationCenter.notifications:
            return 0
        targets = list(NotificationCenter.notifications[notification_name].clients)

    for t in targets:
        try:
            t.target(notification_name, data, t.userdata)
            sent += 1
        except Exception:
            logger.exception(f"Couldn't send notification {notification_name} to one of the clients")
    return sent

def _ns_unregister_client(notification_name, client_id):
    with NotificationCenter.lock:
        if notification_name not in NotificationCenter.notifications:
            return False
        oldlen = len(NotificationCenter.notifications[notification_name].clients)
        newlist = [c for c in NotificationCenter.notifications[notification_name].clients if c.id != client_id]
        NotificationCenter.notifications[notification_name].clients = newlist
        return oldlen != len(NotificationCenter.notifications[notification_name].clients)

def send(notification_name:str, data:any=None):
    """ Send a notification to all registered clients. 
    
    Params:
        notification_name: Name of the notification to send.
        data: Any data to send to the clients. The data are send to target callable 
              that is responsible for processing them.
    """
    return _ns_send_notification(notification_name, data)

def register(notification_name:str, target:callable, userdata=None):
    """ Register a client for a notification.
    
    Params:
        notification_name: Name of the notification to register for.
        target: Callable that will be called when the notification is sent.
            Signature of the function must be:
                def target_func(notification_name, invoker_data, user_data)

            notificsation_name is string
            invoker_data is data sent by the sender of the notification
            user_data is data provided during registration
        userdata: Any data to send to the target callable when the notification is sent.
    """
    return _ns_register_client(notification_name, target, userdata)

def unregister(notification_name:str=None, client_id:int=None):
    """
    Unregister a client from a notification.

    scenario                         |    notification_name  |   client_id
    -------------------------------------------------------------------------
    unregister all                   |        None           |    None
    unregister notification          |   notification_name   |    None
    unregister client in all notifs  |        None           |   client_id  
    unregister client in notification|   notification_name   |   client_id

    """
    if client_id is None:
        if notification_name is None:
            return
        else:
            NotificationCenter.notifications.pop(notification_name, None)
    elif notification_name is None:
        with NotificationCenter.lock:
            for n in NotificationCenter.notifications.keys():
                _ns_unregister_client(notification_name, client_id)
    else:
        _ns_unregister_client(notification_name, client_id)


if __name__=='__main__':
    def t1(notif,src,user):
        print(notif, src, user)

    cid = _ns_register_client('Notif1', t1, {'a': 0})
    print(NotificationCenter.notifications)
    s = _ns_send_notification('Notif1', "Invoker's data")
    print('Sent', s, 'notifications')
    _ns_unregister_client('Notif1', cid)
    s = _ns_send_notification('Notif1', "Invoker's data")
    print('Sent', s, 'notifications')

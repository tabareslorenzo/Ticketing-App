import os
from models.Ticket import Tickets
from models.Order import Orders
from exceptions import (
    OrderDoesNotExistsException,
    TicketDoesNotExistsException,
    TicketAlreadyReservedException
)

ORDER_CANCELLED = "ordercancelled"
ORDER_CREATED = "ordercreated"

def reformat_order(order):
    return {
        "status": order['status'], 
        "expiresAt":order['expiresAt'],
        "userId":order['userId'],
         "ticket": order['ticket'],
         "version": order['version'],
        }
def insert_into_db(userId, status, expiresAt, ticket, version):
    Orders(
        userId=userId, 
        status=status, 
        expiresAt=expiresAt,
        ticket=ticket,
        version=version
        ).save()
    order = get_order_from_db(userId=userId, expiresAt=expiresAt)
    send_created_event(order)
    return reformat_order(order=order)

def get_ticket_from_db(title):
    print(title)
    ticket = Tickets.objects(title=title).first()
    print(ticket)
    if ticket is None:
        raise TicketDoesNotExistsException()
    return ticket

def get_order_from_db(userId,expiresAt):
    order = Orders.objects(userId=userId, expiresAt=expiresAt).first()
    if order is None:
        raise OrderDoesNotExistsException()
    return order

def is_ticket_reserved(ticket):
    orders = Orders.objects(ticket=ticket)
    reserved_order = filter(lambda order: (order.status != 'cancel') , orders)
    if reserved_order:
        raise TicketAlreadyReservedException()
    return False
    
def delete_order(id):
    order = get_order_with_id(id)
    send_cancelled_event(order)
    reformated = reformat_order(order)
    order.delete()
    return reformated

def get_order_with_id(id):
    order = res = Orders.objects(id=id).first()
    print(order)
    if order is None:
        raise OrderDoesNotExistsException()
    return order

def get_ticket_with_id(id):
    ticket = res = Tickets.objects(id=id).first()
    print(ticket)
    if ticket is None:
        raise TicketDoesNotExistsException()
    return ticket

def send_cancelled_event(order):
    myobjc = {
    "type": ORDER_CANCELLED,
    "data": order
    }
    requests.post(
        'http://localhost:6005/api/eventbus/events',
        data= myobjc
    )

def send_created_event(order):
    myobjc = {
    "type": ORDER_CREATED,
    "data": order
    }
    requests.post(
        'http://localhost:6005/api/eventbus/events',
        data= myobjc
    )
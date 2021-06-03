import json
import dateutil.parser
import os
from app import app
import requests
# from validator import validate_password, validate_email
from helpers import (
    insert_into_db,
    handle_event
)
from exceptions import (
    TicketDoesNotExistsException
)
from flask import (
    Flask, 
    abort, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify, 
    session
)



@app.route('/api/tickets/events', methods=['POST'])
def events():
    data = request.get_json()
    print(data)
    try:
        
        print(type(data['data']))
        if type(data['data']) == type("str"):
            event_data = json.loads(data['data'])
            id = event_data["id"]["$oid"]
            del event_data["id"]
            event_data["id"] = id
            if "ticket" in event_data:
                print("event_data")
                id = event_data["ticket" ]["id"]["$oid"]
                del event_data["ticket" ]["id"]
                event_data["ticket" ]["id"] = id
                event_data['expiresAt']['date'] = event_data['expiresAt']['$date']
                del event_data['expiresAt']['$date']
        else:
            event_data = data['data']
        event_type = data["type"]
        print(event_type)
        res = handle_event({
            "type":event_type,
            'data': event_data
            })
        if res is not None:
            return res
        return {"status": "ok"}
    except TicketDoesNotExistsException:
        abort(422, TicketDoesNotExistsException.get_message())

@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
    "Success" : False,
    "error": 500,
    "message": f"Internal server error: {error.description}"
    }), 500

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
    "Success" : False,
    "error": 422,
    "message": f"unprocessable: {error.description}"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
    "Success": False,
    "error" : 404,
    "message" : "resource not found"
    }), 404
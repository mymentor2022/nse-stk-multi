from twilio.rest import Client
import creds as l
import json

def send_notif(stk, signal, indvalue, closeprice, sendto):
    print('sending notification')
    print(f"stock: {stk} + signal: {signal} +  value: {indvalue} + closeprice: {closeprice} + whom: {sendto}")
    from_ph = l.from_ph
    # List of WhatsApp phone numbers to send the message to
    to_whatsapp_both = [f'whatsapp:{number}' for number in l.to_both]
    to_whatsapp_only = l.to_only
    messaging_service_sid=l.messaging_service_sid
    content_template_sid=l.content_template_sid
    client = Client(l.account_sid, l.auth_token)
    try:
        if sendto > 0:
           # Loop through each number in the list and send the message
            for to_whatsapp in to_whatsapp_both:
                message = client.messages.create(
                from_='whatsapp:' + from_ph,
                #body= "Alert Generated for {{1}}. There is a {{2}} cross.Please check.",  # Use the dynamic message here
                messaging_service_sid = messaging_service_sid,
                content_sid=content_template_sid,
                content_variables =json.dumps({"1":stk,"2":signal,"3":str(indvalue),"4":str(closeprice)}),
                to=to_whatsapp
             )
        else:
            # Loop through each number in the list and send the message
            message = client.messages.create(
            from_='whatsapp:' + from_ph,
            #body= "Alert Generated for {{1}}. There is a {{2}} cross.Please check.",  # Use the dynamic message here
            messaging_service_sid = messaging_service_sid,
            content_sid=content_template_sid,
            content_variables =json.dumps({"1":stk,"2":signal,"3":str(indvalue),"4":str(closeprice)}),
            to='whatsapp:' + to_whatsapp_only
            )
        print(f'Message sent, with SID: {message.sid}')
    except Exception as e:
        print(f'Error sending message: {e}')

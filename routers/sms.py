from fastapi import APIRouter, HTTPException
from database import db 


sms_router = APIRouter()

async def get_whats_app_credentials(school_id):
    school = await db.schools.find_one({"school_id" : school_id})
    if not school:
        raise HTTPException(status_code = 400, detail="WhatsApp API not configured for this school")
    return school["access_token"], school["phone_number_id"]

@sms_router.post("/whatsapp/register")
async def register_whatsapp(school_id: str, access_token:str, phone_number_id:str):
    await db.schools.update_one(
        {"school_id" : school_id},
        {"$set": {"access_token": access_token, "phone_number_id":phone_number_id}},
        upsert=True
    )
    return {"message":"whatsApp API registered successfully"}


async def send_whatsapp_message(school_id, phone_number, message):
    access_token, phone_number_id = await get_whats_app_credentials(school_id)

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return {"status": "success", "message": "Message sent successfully!"}
    else:
        raise HTTPException(status_code=400, detail=f"WhatsApp API Error: {response.json()}")

# API to send a payment confirmation message
@sms_router.post("/whatsapp/send-payment-confirmation")
async def send_payment_confirmation(school_id: str, student_phone: str, amount_paid: float, balance: float):
    message = f"Payment received: ₹{amount_paid}. Balance: ₹{balance}. Thank you!"
    return await send_whatsapp_message(school_id, student_phone, message)
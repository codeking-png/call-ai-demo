from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI()

@app.get("/call")
@app.head("/call")
async def verify_call():
    return Response(content="OK", media_type="text/plain")

@app.post("/call")
async def handle_call(
    request: Request,
    SpeechResult: str = Form(default=""),
    From: str = Form(default=""),
    CallSid: str = Form(default="")
):
    response = VoiceResponse()

    if SpeechResult:
        print(f"🔔 مكالمة جديدة من: {From} | Call SID: {CallSid}")
        print(f"🎙️ SpeechResult = {SpeechResult}")
        try:
            gpt_reply = ask_gpt(SpeechResult)
            print(f"🤖 رد GPT: {gpt_reply}")
            response.say(gpt_reply, language="ar-SA")
        except Exception as e:
            print(f"❌ GPT Error: {e}")
            response.say("عذرًا، حدث خطأ أثناء المعالجة. حاول لاحقًا.", language="ar-SA")
    else:
        gather = Gather(input="speech", action="/call", method="POST", language="ar-SA", timeout=5)
        gather.say("مرحباً بك، أخبرني كيف يمكنني مساعدتك؟", language="ar-SA")
        response.append(gather)
        response.say("لم أسمع أي شيء، يرجى المحاولة لاحقاً.", language="ar-SA")

    return Response(content=str(response), media_type="application/xml")

def ask_gpt(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "أنت مساعد صوتي ذكي. تحدث دائمًا باللغة العربية الفصحى."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"].strip()


#    chat_completion = client.chat.completions.create(
#        "model": "mistralai/mistral-7b-instruct",
#        messages=[
#            {"role": "system", "content": "أنت مساعد صوتي ذكي لخدمة العملاء."},
#            {"role": "user", "content": prompt}
#        ]
#    )
#    return chat_completion.choices[0].message.content.strip()

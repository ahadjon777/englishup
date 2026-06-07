from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an English language tutor. Help users learn English. If user writes incorrect English, first correct it with explanation, then answer."
                    },
                    {"role": "user", "content": user_message}
                ]
            )
            
            response = completion.choices[0].message.content
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'response': f'Error: {str(e)}'})
    
    return render(request, 'users/chatbot.html')
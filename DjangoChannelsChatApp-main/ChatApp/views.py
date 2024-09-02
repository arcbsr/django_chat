import json
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def CreateRoom(request):

    if request.method == 'POST':
        username = request.POST['username']
        room = request.POST['room']

        try:
            get_room = Room.objects.get(room_name=room)
            return redirect('room', room_name=room, username=username)

        except Room.DoesNotExist:
            new_room = Room(room_name = room)
            new_room.save()
            return redirect('room', room_name=room, username=username)

    return render(request, 'index.html')

def MessageView2(request, room_name, username):

    get_room = Room.objects.get(room_name=room_name)

    if request.method == 'POST':
        message = request.POST['message']

        print(message)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()
    get_messages= Message.objects.filter(room=get_room)
    print(get_messages)
    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
    }
    return render(request, 'msg.html', context)


@csrf_exempt
def MessageView(request, room_name, username):
    try:
        get_room = Room.objects.get(room_name=room_name)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist'}, status=404)

    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

        if not message:
            return JsonResponse({'error': 'Message content is required'}, status=400)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()

        return JsonResponse({
            'message': 'Message sent successfully',
            'message_id': new_message.id,
            'sender': username,
            'room_name': room_name,
            'content': message
        }, status=201)

    elif request.method == 'GET':
        get_messages = Message.objects.filter(room=get_room).order_by('timestamp')
        messages_list = [
            {'sender': msg.sender, 'message': msg.message, 'timestamp': msg.timestamp}
            for msg in get_messages
        ]

        return JsonResponse({
            'room_name': room_name,
            'messages': messages_list
        }, status=200)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
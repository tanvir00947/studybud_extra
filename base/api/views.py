from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from base.models import Room,User,Topic,Message
from .serializers import *
from base.api import serializers
from rest_framework import status

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView): #ye wali class latest documentation me nahi hai video se copy kiyahai
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRooms(request):
    user=request.user
    rooms = user.room_set.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, context={'request': request,'include_room_messages': True})
    return Response(serializer.data)




@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getUser(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getTopics(request):
    topics=Topic.objects.all()
    serializer=TopicSerializer(topics,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTopic(request, pk):
    topic = Topic.objects.get(id=pk)
    serializer = TopicSerializer(topic, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def getMessages(request):
    messages=Message.objects.all()
    serializer=MessageSerializer(messages,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRoomMessages(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    #participants = room.participants.all()
    serializer=MessageSerializer(room_messages,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def homeAPI(request):
    rooms=Room.objects.all()
    topics=Topic.objects.all()[0:5]
    room_messages=Message.objects.all().order_by('-created')[0:7]
    
    rooms_data=RoomSerializer(rooms,many=True).data
    topics_data = TopicSerializer(topics, many=True).data
    messages_data = MessageSerializer(room_messages, many=True).data

    response_data = {
        'topics': topics_data,
        'rooms': rooms_data,
        'messages': messages_data,
    }

    # Return the response
    return Response(response_data)

@api_view(['GET'])
def roomAPI(request,pk):
    room=Room.objects.get(id=pk)
    # participants=room.participants.all()
    room_data=RoomSerializer(room, context={'request': request,'include_room_messages': True}).data
    return Response(room_data)




# @api_view(['GET'])
# def get_csrf_token(request):
#     # Assuming you are using Django's built-in CSRF token mechanism
#     csrf_token = request.COOKIES.get('csrftoken', '')
#     return Response({'csrfToken': csrf_token})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createRoomAPI(request):
    data = request.data
    user=request.user
    
    # Validate and process the form data
    if 'topic' not in data or 'name' not in data:
        return Response({'error': 'Topic and Name are required fields'}, status=400)

    topic_name = data['topic']
    topic, created = Topic.objects.get_or_create(name=topic_name)

    is_private = data.get('private', False)

    new_room = Room.objects.create(
        host=user,
        topic=topic,
        name=data.get('name'),
        description=data.get('description', ''),
        private=is_private
    )

    new_room.participants.add(user)

    return Response({'message': 'Room created successfully'})


@api_view(['GET', 'POST'])
def userProfileAPI(request, pk):
    # Get the user instance or return a 404 response if not found
    user = get_object_or_404(User, id=pk)
    
    # Retrieve related data
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    # Handle follow logic for POST requests for authenticated users
    if request.method == 'POST' and request.user.is_authenticated:
        follow, created = Follow.objects.get_or_create(followed=user)
        if request.user not in follow.followers.all():
            follow.followers.add(request.user)
        else:
            follow.followers.remove(request.user)

    # Serialize the data
    user_data = UserSerializer(user, many=False).data
    rooms_data = RoomSerializer(rooms, many=True).data
    topics_data = TopicSerializer(topics, many=True).data
    messages_data = MessageSerializer(room_messages, many=True).data

    # Get or create Follow instance
    follow, created = Follow.objects.get_or_create(followed=user)
    
    # Additional data for follow status
    is_following = request.user.is_authenticated and request.user in follow.followers.all()
    followers_count = follow.followers.count()
    following_count = user.followers.count()

    response_data = {
        'user': user_data,
        'topics': topics_data,
        'rooms': rooms_data,
        'messages': messages_data,
        'follow': {'is_following': is_following, 'followers_count': followers_count, 'following_count': following_count}
    }

    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createMessageAPI(request,pk):
    data=request.data
    user=request.user
    # Check if 'body' is in the request data
    if 'body' not in data:
        return Response({'error': 'Message body is a required field'}, status=400)

    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)
    message = Message.objects.create(
            user=user,
            room=room,
            body=data['body']
        )
    
    room.participants.add(user)

    return Response({'message':'Message saved successfully'})



@api_view(['POST'])
# @permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteRoomAPI(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user is the host of the room
    if request.user != room.host:
        return Response({'error': 'You are not allowed to delete this room'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        room.delete()
        return Response({'success': 'Room deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    # This block is reached if the request method is not DELETE
    return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteMessageAPI(request,pk):
    try:
        message=Message.objects.get(id=pk)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'},status=status.HTTP_404_NOT_FOUND)
    
    if request.user !=message.user:
        return Response({'error': 'You are not allowed to delete this message'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        message.delete()
        return Response({'success: Message deleted successfully '},status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def updateRoomAPI(request, pk):
    try:
        room = get_object_or_404(Room, id=pk)

        if request.user != room.host:
            return Response({'error': 'You are not allowed here!!'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            serializer = RoomSerializer(room)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = RoomSerializer(room, data=request.data, partial=True)
            if serializer.is_valid():
                room.name = serializer.validated_data.get('name', room.name)
                room.description = serializer.validated_data.get('description', room.description)
                room.save()

                return Response({'message': 'Room updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'errorsfd': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfileAPI(request):
    try:
        user = request.user

        if request.method == 'GET':
            # Serialize and return the user profile for GET requests
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            # Ensure that the request data contains the required fields
            if 'name' not in request.data or 'username' not in request.data or 'email' not in request.data:
                return Response({'error': 'Name, username, and email are required fields'}, status=status.HTTP_400_BAD_REQUEST)

            # Update user profile
            user.name = request.data.get('name', user.name)
            user.username = request.data.get('username', user.username)
            user.email = request.data.get('email', user.email)
            user.bio = request.data.get('bio', user.bio)

            # Save the updated user profile
            user.save()

            # Serialize and return the updated user profile
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

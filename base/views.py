from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User,Follow, JoinRequest,DirectMessage
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Lets learn python!'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)).order_by('-created')[0:5]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    joinRequests = room.join_requests.all()

    requested=False

    for joinRequest in joinRequests:
        if request.user == joinRequest.applicant:
            requested=True

    is_participant = request.user in participants

    if room.private == True:
        if is_participant:
            if request.method == 'POST':
                message = Message.objects.create(
                    user=request.user,
                    room=room,
                    body=request.POST.get('body')
                )
                room.participants.add(request.user)
                return redirect('room', pk=room.id)
        elif not is_participant and not requested:
            if request.method=='POST':
                JoinRequest.objects.create(
                    room=room,
                    applicant=request.user,
                )
                requested=True
                return redirect('room', pk=room.id)

        elif not is_participant and requested:
            if request.method=='POST':
                # JoinRequest.objects.create(
                #     room=room,
                #     applicant=request.user,
                # )
                for joinRequest in joinRequests:
                    if request.user == joinRequest.applicant and room==joinRequest.room:
                        joinRequest.delete()

                requested=False
                return redirect('room', pk=room.id)

    else:
        if request.method == 'POST':
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get('body')
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants,
               'is_participant':is_participant,'joinRequests':joinRequests,'requested':requested}  #my context
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    #my code
    try:
        follow = Follow.objects.get(followed=user)
    except Follow.DoesNotExist:
        # If Follow object does not exist, create a new one
        follow = Follow.objects.create(followed=user)

    is_following= request.user in follow.followers.all()

    followers_count=follow.followers.count()

    following_count = user.followers.count()

    if request.method=='POST':
        if request.user.is_authenticated:
            if request.user not in follow.followers.all():
                follow.followers.add(request.user)
            else:
                follow.followers.remove(request.user)
            return redirect('user-profile',pk=pk)
        else:
            return redirect('login')

    #ends
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics,'follow':follow,'is_following':is_following,'followers_count':followers_count,'following_count':following_count}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        is_private = request.POST.get('private') == 'on'

        new_room=Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            private=is_private
        )

        new_room.participants.add(request.user)
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required(login_url='login')
def acceptRequest(request, pk):
    joinRequest=JoinRequest.objects.get(id=pk)
    room = Room.objects.get(id=joinRequest.room.id)

    if request.user != joinRequest.room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        joinRequest.approveStatus=True
        room.participants.add(joinRequest.applicant)
        joinRequest.save()
        return redirect('home')
    return render(request, 'base/approve_request.html', {'joinRequest': joinRequest})



def followers(request,pk):
    user = User.objects.get(id=pk)
    follow = Follow.objects.get(followed=user)
    followers=follow.followers.all()
    context={'followers':followers}
    return render(request,'base/followers.html',context)

def following(request,pk):
    user = User.objects.get(id=pk)
    #rooms = user.room_set.all()
    followings = user.followers.all()
    #followings=user.follow_set.all()
    print(followings)
    context={'followings':followings}
    return render(request,'base/following.html',context)


@login_required(login_url='login')
def dm(request,pk):
    user= User.objects.get(id=request.user.id)
    receiver= User.objects.get(id=pk)  #jisse user chat karraha hai use receiver naam kiya hai
    
    #followings = user.followers.all()

    # Get distinct users with whom the current user has sent or received messages
    users_with_messages = User.objects.filter(
        Q(sent_messages__sender=user) | Q(received_messages__receiver=user)
    ).union(
        User.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        )
    )


    print(users_with_messages)
    received_messages = DirectMessage.objects.filter(sender=user, receiver=receiver) | \
                     DirectMessage.objects.filter(sender=receiver, receiver=user)



    if request.method == 'POST':
        directmessage = DirectMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            body=request.POST.get('body')
        )
        #room.participants.add(request.user)
        return redirect('dm', pk=pk)
    
    context={'received_messages':received_messages,'receiver':receiver,'users_with_messages':users_with_messages}
    return render(request,'base/dm.html',context)


@login_required(login_url='login')
def deleteDmMessage(request, pk):
    message = DirectMessage.objects.get(id=pk)

    if request.user != message.sender:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


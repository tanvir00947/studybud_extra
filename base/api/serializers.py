from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from base.models import Room,User,Topic,Message,Follow


class MessageSerializer(ModelSerializer):
    room_name = serializers.SerializerMethodField()
    user_username=serializers.SerializerMethodField()
    user_avatar=serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_room_name(self, obj):
        return obj.room.name if obj.room else None
    def get_user_username(self, obj):
        return obj.user.username if obj.user else None
    def get_user_avatar(self, obj):
        if obj.user and obj.user.avatar:
            return obj.user.avatar.url
        return None


class RoomSerializer(ModelSerializer):
    topic_name = serializers.SerializerMethodField()
    host_username=serializers.SerializerMethodField()
    host_avatar=serializers.SerializerMethodField()
    room_messages= serializers.SerializerMethodField()
    room_participants=serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_topic_name(self, obj):
        return obj.topic.name if obj.topic else None
    def get_host_username(self, obj):
        return obj.host.username if obj.host else None
    def get_host_avatar(self, obj):
        if obj.host and obj.host.avatar:
            return obj.host.avatar.url
        return None
    def get_room_messages(self,obj):
        include_room_messages = self.context.get('include_room_messages', False)
        if include_room_messages:
            messages=MessageSerializer(obj.message_set.all(),many=True).data
            return messages
        return None
    def get_room_participants(self,obj):
        include_room_messages = self.context.get('include_room_messages', False)
        if include_room_messages:
            participants=UserSerializer(obj.participants.all(),many=True).data
            return participants
        return None


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class TopicSerializer(ModelSerializer):
    num_rooms = serializers.SerializerMethodField()
    class Meta:
        model = Topic
        fields = '__all__'

    def get_num_rooms(self, obj):
        return obj.room_set.count()


class FollowSerializer(ModelSerializer):
    class Meta:
        model= Follow
        fields = '__all__'
from rest_framework import serializers
from .models import Avatar, AvatarStage, UserAvatarProgress, Stage


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'name', 'description', 'required_spending']


class AvatarStageSerializer(serializers.ModelSerializer):
    stage = StageSerializer()

    class Meta:
        model = AvatarStage
        fields = ['id', 'stage', 'default_img']


class AvatarStartStageSerializer(serializers.ModelSerializer):
    stage = StageSerializer()

    class Meta:
        model = AvatarStage
        fields = ['id', 'stage', 'default_img']


class AvatarSerializer(serializers.ModelSerializer):
    start_stage = AvatarStartStageSerializer(many=True)

    class Meta:
        model = Avatar
        fields = ['id', 'name', 'description', 'start_stage']


class AvatarDetailSerializer(serializers.ModelSerializer):
    avatar_stages = AvatarStageSerializer(many=True)

    class Meta:
        model = Avatar
        fields = ['id', 'name', 'description', 'avatar_stages']


class UserAvatarProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatarProgress
        fields = ['id', 'avatar', 'current_stage', 'total_spending']


class UserAvatarDetailSerializer(serializers.ModelSerializer):
    avatar = AvatarDetailSerializer()
    current_stage = StageSerializer()
    current_image = serializers.SerializerMethodField()
    next_required_spending = serializers.SerializerMethodField()

    class Meta:
        model = UserAvatarProgress
        fields = ['id', 'avatar', 'current_stage', 'total_spending', 'current_image', 'next_required_spending']

    def get_current_image(self, obj):
        return obj.get_current_image()

    def get_next_required_spending(self, obj):
        next_stage = (
            Stage.objects
            .filter(required_spending__gt=obj.current_stage.required_spending)
            .order_by('required_spending')
            .first()
        )
        if next_stage:
            return next_stage.required_spending - obj.total_spending
        return None
from django.contrib import admin
from django.utils.html import format_html
from .models import Avatar, Stage, AvatarStage, Animation, UserAvatarProgress, AvatarOutfit, OutfitPurchase

@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview')
    search_fields = ('name', 'description')
    list_per_page = 20
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
    )

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Описание'

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_spending', 'description_preview')
    search_fields = ('name', 'description')
    list_filter = ('required_spending',)
    list_per_page = 20
    ordering = ('required_spending',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'required_spending')
        }),
    )

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Описание'

@admin.register(AvatarStage)
class AvatarStageAdmin(admin.ModelAdmin):
    list_display = ('avatar', 'stage', 'image_preview')
    list_filter = ('avatar', 'stage')
    search_fields = ('avatar__name', 'stage__name')
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('avatar', 'stage', 'default_img')
        }),
        ('Превью', {
            'fields': ('image_preview',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.default_img:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.default_img.url)
        return "Нет изображения"
    image_preview.short_description = "Превью изображения"

class AnimationInline(admin.TabularInline):
    model = Animation
    extra = 1
    readonly_fields = ('gif_preview',)

    def gif_preview(self, obj):
        if obj.gif:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.gif.url)
        return "Нет GIF"
    gif_preview.short_description = "Превью GIF"

class AvatarOutfitInline(admin.TabularInline):
    model = AvatarOutfit
    extra = 1
    readonly_fields = ('outfit_preview', 'custom_img_preview')

    def outfit_preview(self, obj):
        if obj.outfit:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.outfit.url)
        return "Нет изображения"
    outfit_preview.short_description = "Превью одежды"

    def custom_img_preview(self, obj):
        if obj.custom_img:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.custom_img.url)
        return "Нет изображения"
    custom_img_preview.short_description = "Превью аватара в одежде"

@admin.register(Animation)
class AnimationAdmin(admin.ModelAdmin):
    list_display = ('avatar_stage', 'gif_preview')
    list_filter = ('avatar_stage__avatar', 'avatar_stage__stage')
    search_fields = ('avatar_stage__avatar__name', 'avatar_stage__stage__name')
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('avatar_stage', 'gif')
        }),
        ('Превью', {
            'fields': ('gif_preview',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('gif_preview',)

    def gif_preview(self, obj):
        if obj.gif:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.gif.url)
        return "Нет GIF"
    gif_preview.short_description = "Превью GIF"

@admin.register(UserAvatarProgress)
class UserAvatarProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'current_stage', 'total_spending', 'current_outfit_display')
    list_filter = ('avatar', 'current_stage')
    search_fields = ('user__username', 'avatar__name', 'current_stage__name')
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'current_stage', 'total_spending', 'current_outfit')
        }),
        ('Превью', {
            'fields': ('current_image_preview',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('current_image_preview',)

    def current_outfit_display(self, obj):
        return obj.current_outfit if obj.current_outfit else "Без одежды"
    current_outfit_display.short_description = "Текущая одежда"

    def current_image_preview(self, obj):
        image_url = obj.get_current_image()
        if image_url:
            return format_html('<img src="{}" style="max-height: 200px;"/>', image_url)
        return "Нет изображения"
    current_image_preview.short_description = "Текущее изображение"

@admin.register(AvatarOutfit)
class AvatarOutfitAdmin(admin.ModelAdmin):
    list_display = ('avatar_stage', 'price', 'outfit_preview', 'custom_img_preview')
    list_filter = ('avatar_stage__avatar', 'avatar_stage__stage')
    search_fields = ('avatar_stage__avatar__name', 'avatar_stage__stage__name')
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('avatar_stage', 'outfit', 'price', 'custom_img', 'custom_animations')
        }),
        ('Превью', {
            'fields': ('outfit_preview', 'custom_img_preview'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('outfit_preview', 'custom_img_preview')

    def outfit_preview(self, obj):
        if obj.outfit:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.outfit.url)
        return "Нет изображения"
    outfit_preview.short_description = "Превью одежды"

    def custom_img_preview(self, obj):
        if obj.custom_img:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.custom_img.url)
        return "Нет изображения"
    custom_img_preview.short_description = "Превью аватара в одежде"

@admin.register(OutfitPurchase)
class OutfitPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_name', 'stage_name', 'outfit', 'purchased_at')
    list_filter = ('purchased_at', 'outfit__avatar_stage__avatar', 'outfit__avatar_stage__stage')
    search_fields = (
        'user__username',
        'outfit__avatar_stage__avatar__name',
        'outfit__avatar_stage__stage__name',
    )
    ordering = ('-purchased_at',)
    date_hierarchy = 'purchased_at'

    def avatar_name(self, obj):
        return obj.outfit.avatar_stage.avatar.name
    avatar_name.short_description = "Аватар"

    def stage_name(self, obj):
        return obj.outfit.avatar_stage.stage.name
    stage_name.short_description = "Стадия"
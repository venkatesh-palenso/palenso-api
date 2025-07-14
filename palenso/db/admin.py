from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from palenso.db.models import User, Token, Profile, Education, WorkExperience, Skill, Interest, Project, Resume


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile_number', 'first_name', 'last_name', 
                   'is_email_verified', 'is_mobile_verified', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_email_verified', 'is_mobile_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'mobile_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    readonly_fields = ('date_joined', 'last_login', 'last_active', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'mobile_number')}),
        ('Verification', {'fields': ('is_email_verified', 'is_mobile_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_active')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'mobile_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'is_used', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')
    ordering = ('-created_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'country', 'city', 'gender')
    list_filter = ('gender', 'country')
    search_fields = ('user__username', 'user__email', 'bio')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {'fields': ('bio', 'date_of_birth', 'gender', 'profile_picture')}),
        ('Contact Information', {'fields': ('website', 'linkedin', 'github', 'twitter')}),
        ('Location', {'fields': ('country', 'state', 'city')}),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'end_date')
    search_fields = ('institution', 'degree', 'field_of_study', 'profile__user__username')
    ordering = ('-end_date', '-start_date')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company', 'position', 'location', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'end_date')
    search_fields = ('company', 'position', 'location', 'profile__user__username')
    ordering = ('-end_date', '-start_date')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'proficiency_level')
    list_filter = ('proficiency_level',)
    search_fields = ('name', 'profile__user__username')
    ordering = ('name',)


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'description')
    search_fields = ('name', 'description', 'profile__user__username')
    ordering = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'technologies_used', 'profile__user__username')
    ordering = ('-end_date', '-start_date')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('title', 'description', 'profile__user__username')
    ordering = ('-created_at',)

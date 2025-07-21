from django.contrib import admin

from django.contrib.auth.admin import UserAdmin


from palenso.db.models import (
    User,
    Token,
    Profile,
    Company,
    Education,
    WorkExperience,
    Project,
    Skill,
    Interest,
    Resume,
    Job,
    JobApplication,
    SavedJob,
    Event,
    EventRegistration,
    MediaAssets,
)


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "mobile_number",
        "first_name",
        "last_name",
        "is_email_verified",
        "is_mobile_verified",
        "is_active",
        "date_joined",
        "role",
    )
    list_filter = (
        "is_active",
        "is_email_verified",
        "is_mobile_verified",
        "is_staff",
        "is_superuser",
        "role",
    )
    search_fields = ("username", "email", "mobile_number", "first_name", "last_name")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    readonly_fields = (
        "date_joined",
        "last_login",
        "last_active",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "mobile_number", "role")},
        ),
        ("Verification", {"fields": ("is_email_verified", "is_mobile_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined", "last_active")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "mobile_number",
                    "first_name",
                    "last_name",
                    "role",
                ),
            },
        ),
    )


admin.site.register(Token)
admin.site.register(MediaAssets)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("student", "job", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("student__username", "student__email", "job__title")
    readonly_fields = ("saved_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "country", "city", "gender")
    list_filter = ("gender", "country")
    search_fields = ("user__username", "user__email", "bio")
    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Personal Information",
            {"fields": ("bio", "date_of_birth", "gender", "profile_picture_url")},
        ),
        (
            "Contact Information",
            {"fields": ("website", "linkedin", "github", "twitter")},
        ),
        ("Location", {"fields": ("country", "state", "city")}),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "institution",
        "degree",
        "field_of_study",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = (
        "institution",
        "degree",
        "field_of_study",
        "profile__user__username",
    )
    ordering = ("-end_date", "-start_date")


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "company",
        "position",
        "location",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = ("company", "position", "profile__user__username")
    ordering = ("-end_date", "-start_date")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("profile", "name", "proficiency_level")
    list_filter = ("proficiency_level",)
    search_fields = ("name", "profile__user__username")


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("profile", "name", "description")
    search_fields = ("name", "description", "profile__user__username")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("profile", "title", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = (
        "title",
        "description",
        "technologies_used",
        "profile__user__username",
    )
    ordering = ("-end_date", "-start_date")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("profile", "title", "is_primary", "created_at")
    list_filter = ("is_primary", "created_at")
    search_fields = ("title", "description", "profile__user__username")
    ordering = ("-created_at",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "employer",
        "industry",
        "company_size",
        "country",
        "city",
        "is_verified",
        "is_active",
    )
    list_filter = ("industry", "company_size", "is_verified", "is_active", "country")
    search_fields = ("name", "description", "employer__username", "employer__email")
    fieldsets = (
        (
            "Company Information",
            {
                "fields": (
                    "employer",
                    "name",
                    "description",
                    "industry",
                    "company_size",
                    "founded_year",
                )
            },
        ),
        ("Contact Information", {"fields": ("website", "email", "phone")}),
        ("Location", {"fields": ("country", "state", "city", "address")}),
        ("Media", {"fields": ("logo", "banner_image")}),
        ("Social Media", {"fields": ("linkedin", "twitter", "facebook")}),
        ("Status", {"fields": ("is_verified", "is_active")}),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "job_type",
        "experience_level",
        "location",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = (
        "job_type",
        "experience_level",
        "is_active",
        "is_featured",
        "is_remote",
        "created_at",
    )
    search_fields = ("title", "description", "company__name")
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Job Information",
            {
                "fields": (
                    "company",
                    "title",
                    "description",
                    "requirements",
                    "responsibilities",
                )
            },
        ),
        (
            "Job Details",
            {"fields": ("job_type", "experience_level", "location", "is_remote")},
        ),
        ("Salary", {"fields": ("salary_min", "salary_max", "salary_currency")}),
        (
            "Skills & Categories",
            {"fields": ("required_skills", "preferred_skills", "category")},
        ),
        (
            "Application Details",
            {"fields": ("application_deadline", "max_applications")},
        ),
        ("Status", {"fields": ("is_active", "is_featured")}),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "job", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "applicant__username",
        "applicant__email",
        "job__title",
        "job__company__name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("applicant", "job", "created_at")
    fieldsets = (
        ("Application", {"fields": ("applicant", "job", "cover_letter", "resume")}),
        ("Status", {"fields": ("status",)}),
        (
            "Additional Information",
            {"fields": ("expected_salary", "available_from", "notes")},
        ),
        ("Employer Notes", {"fields": ("employer_notes",)}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organizer",
        "event_type",
        "start_date",
        "end_date",
        "location",
        "is_active",
        "is_featured",
    )
    list_filter = (
        "event_type",
        "is_active",
        "is_featured",
        "is_virtual",
        "start_date",
        "end_date",
    )
    search_fields = ("title", "description", "organizer__username", "organizer__email")
    ordering = ("-start_date",)
    fieldsets = (
        (
            "Event Information",
            {"fields": ("organizer", "company", "title", "description", "event_type")},
        ),
        (
            "Date & Time",
            {"fields": ("start_date", "end_date", "registration_deadline")},
        ),
        ("Location", {"fields": ("location", "is_virtual", "virtual_meeting_url")}),
        (
            "Registration",
            {
                "fields": (
                    "max_participants",
                    "is_registration_required",
                    "registration_fee",
                )
            },
        ),
        ("Media", {"fields": ("banner_image",)}),
        ("Additional Information", {"fields": ("tags", "requirements")}),
        ("Status", {"fields": ("is_active", "is_featured")}),
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "event",
        "status",
        "registration_date",
        "payment_status",
    )
    list_filter = ("status", "payment_status", "registration_date")
    search_fields = ("participant__username", "participant__email", "event__title")
    ordering = ("-registration_date",)
    readonly_fields = ("participant", "event", "registration_date")
    fieldsets = (
        ("Registration", {"fields": ("participant", "event", "registration_date")}),
        ("Status", {"fields": ("status",)}),
        (
            "Additional Information",
            {"fields": ("dietary_restrictions", "special_requirements", "notes")},
        ),
        ("Payment", {"fields": ("payment_status", "payment_amount")}),
    )

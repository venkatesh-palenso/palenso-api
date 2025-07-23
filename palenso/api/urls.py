from django.urls import path

# Create your urls here.

from palenso.api.views.authentication import (
    SignInEndpoint,
    SignUpEndpoint,
    SignOutEndpoint,
    ForgotPasswordEndpoint,
    ResetPasswordEndpoint,
    ChangePasswordEndpoint,
    CheckMediumAvailabilityEndpoint,
    RequestMediumVerificationEndpoint,
    VerifyMediumEndpoint,
)
from palenso.api.views.people import PeopleView, UserView
from palenso.api.views.profile import (
    EducationView,
    InterestView,
    ProfileDetailView,
    ProjectView,
    ResumeView,
    SkillView,
    WorkExperienceView,
)
from palenso.api.views.company import (
    CompanyProfileListCreateEndpoint,
    CompanyProfileDetailEndpoint,
)

from palenso.api.views.job import JobListCreateEndpoint, JobDetailEndpoint

from palenso.api.views.event import EventListCreateEndpoint, EventDetailEndpoint

from palenso.api.views.media import UploadMediaEndpoint

urlpatterns = [
    # media
    path("upload", UploadMediaEndpoint.as_view()),
    # auth
    path("auth/signin", SignInEndpoint.as_view()),
    path("auth/signup", SignUpEndpoint.as_view()),
    path("auth/signout", SignOutEndpoint.as_view()),
    # manage password
    path("auth/forgot-password", ForgotPasswordEndpoint.as_view()),
    path("auth/reset-password", ResetPasswordEndpoint.as_view()),
    path("auth/change-password", ChangePasswordEndpoint.as_view()),
    # handle medium
    path("auth/check-medium-availability", CheckMediumAvailabilityEndpoint.as_view()),
    path(
        "auth/request-medium-verification", RequestMediumVerificationEndpoint.as_view()
    ),
    path("auth/verify-medium", VerifyMediumEndpoint.as_view()),
    # users
    path("users", PeopleView.as_view()),
    path("users/me", UserView.as_view()),
    # profile
    path("users/<uuid:user_id>/profile", ProfileDetailView.as_view()),
    path("educations", EducationView.as_view()),
    path(
        "educations/<uuid:education_id>",
        EducationView.as_view(),
    ),
    path("work-experiences", WorkExperienceView.as_view()),
    path(
        "work-experiences/<uuid:experience_id>",
        WorkExperienceView.as_view(),
    ),
    path("skills", SkillView.as_view()),
    path("skills/<uuid:skill_id>", SkillView.as_view()),
    path("interests", InterestView.as_view()),
    path("interests/<uuid:interest_id>", InterestView.as_view()),
    path("projects", ProjectView.as_view()),
    path("projects/<uuid:project_id>", ProjectView.as_view()),
    path("resumes", ResumeView.as_view()),
    path("resumes/<uuid:resume_id>", ResumeView.as_view()),
    # company
    path("companies", CompanyProfileListCreateEndpoint.as_view()),
    path("companies/<uuid:company_id>", CompanyProfileDetailEndpoint.as_view()),
    # event
    path("events", EventListCreateEndpoint.as_view()),
    path("events/<uuid:event_id>", EventDetailEndpoint.as_view()),
    # job
    path("jobs", JobListCreateEndpoint.as_view()),
    path("jobs/<uuid:job_id>", JobDetailEndpoint.as_view()),
]

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

from palenso.api.views.job import (
    JobListCreateEndpoint, 
    JobDetailEndpoint,
    JobApplicationListCreateEndpoint,
    JobApplicationDetailEndpoint,
    SavedJobListCreateEndpoint,
    SavedJobDetailEndpoint,
    InterviewListCreateEndpoint,
    InterviewDetailEndpoint,
    OfferListCreateEndpoint,
    OfferDetailEndpoint,
)

from palenso.api.views.event import (
    EventListCreateEndpoint, 
    EventDetailEndpoint,
    EventRegistrationListCreateEndpoint,
    EventRegistrationDetailEndpoint,
)

from palenso.api.views.media import UploadMediaEndpoint

from palenso.api.views.dashboard import DashboardAnalyticsEndpoint, DashboardInfoEndpoint

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
    path("users/<uuid:user_id>", UserView.as_view()),
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
    # job
    path("jobs", JobListCreateEndpoint.as_view()),
    path("jobs/<uuid:job_id>", JobDetailEndpoint.as_view()),
    # job applications
    path("job-applications", JobApplicationListCreateEndpoint.as_view()),
    path("job-applications/<uuid:application_id>", JobApplicationDetailEndpoint.as_view()),
    # saved jobs
    path("saved-jobs", SavedJobListCreateEndpoint.as_view()),
    path("saved-jobs/<uuid:saved_job_id>", SavedJobDetailEndpoint.as_view()),
    # interviews
    path("interviews", InterviewListCreateEndpoint.as_view()),
    path("interviews/<uuid:interview_id>", InterviewDetailEndpoint.as_view()),
    # offers
    path("offers", OfferListCreateEndpoint.as_view()),
    path("offers/<uuid:offer_id>", OfferDetailEndpoint.as_view()),
    # event
    path("events", EventListCreateEndpoint.as_view()),
    path("events/<uuid:event_id>", EventDetailEndpoint.as_view()),
    # event registrations
    path("event-registrations", EventRegistrationListCreateEndpoint.as_view()),
    path("event-registrations/<uuid:registration_id>", EventRegistrationDetailEndpoint.as_view()),
    # analytics
    path("dashboard-analytics", DashboardAnalyticsEndpoint.as_view()),
    # dashboard
    path("dashboard-info", DashboardInfoEndpoint.as_view()),
]

from django.urls import path

# Create your urls here.

from palenso.api.views.authentication import (
    SignInEndpoint,
    CheckAvailabilityEndpoint,
    UserSignupEndpoint,
    SendVerificationCodeEndpoint,
    SignOutEndpoint,
    VerifyEmailEndpoint,
    VerifyMobileEndpoint,
    ForgotPasswordEndpoint,
    ResetPasswordEndpoint,
)
from palenso.api.views.people import (
    PeopleView
)
from palenso.api.views.profile import (
    UserProfileView,
    EducationView,
    WorkExperienceView,
    SkillView,
    InterestView,
    ProjectView,
    ResumeView,
)

urlpatterns = [
    # Authentication endpoints - SSO-compatible signup flow
    path("auth/check-availability", CheckAvailabilityEndpoint.as_view()),
    path("auth/send-verification", SendVerificationCodeEndpoint.as_view()),

    path("auth/signup", UserSignupEndpoint.as_view()),
    
    # Authentication endpoints - Other
    path("auth/sign-in", SignInEndpoint.as_view()),
    path("auth/sign-out", SignOutEndpoint.as_view()),
    path("auth/verify-email", VerifyEmailEndpoint.as_view()),
    path("auth/verify-mobile", VerifyMobileEndpoint.as_view()),
    path("auth/forgot-password", ForgotPasswordEndpoint.as_view()),
    path("auth/reset-password", ResetPasswordEndpoint.as_view()),
    
    # Profile management endpoints
    path("profile", UserProfileView.as_view()),
    path("profile/education", EducationView.as_view()),
    path("profile/education/<int:education_id>", EducationView.as_view()),
    path("profile/work-experience", WorkExperienceView.as_view()),
    path("profile/work-experience/<int:experience_id>", WorkExperienceView.as_view()),
    path("profile/skills", SkillView.as_view()),
    path("profile/skills/<int:skill_id>", SkillView.as_view()),
    path("profile/interests", InterestView.as_view()),
    path("profile/interests/<int:interest_id>", InterestView.as_view()),
    path("profile/projects", ProjectView.as_view()),
    path("profile/projects/<int:project_id>", ProjectView.as_view()),
    path("profile/resumes", ResumeView.as_view()),
    path("profile/resumes/<int:resume_id>", ResumeView.as_view()),
    
    # Legacy endpoints (keeping for backward compatibility)
    path("sign-in", SignInEndpoint.as_view()),
    path("sign-out", SignOutEndpoint.as_view()),
    path("users", PeopleView.as_view()),
]

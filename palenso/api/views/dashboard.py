from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from sentry_sdk import capture_exception

from palenso.db.models.job import Job, JobApplication, SavedJob, Interview, Offer
from palenso.db.models.event import Event, EventRegistration
from palenso.db.models.company import Company
from palenso.db.models.user import User



class DashboardAnalyticsEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            now = timezone.now()
            week_start = now - timedelta(days=now.weekday())
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if user_role == "student":
                return self._get_student_analytics(request, now, week_start, month_start)
            elif user_role == "employer":
                return self._get_employer_analytics(request, now, week_start, month_start)
            elif user_role == "admin":
                return self._get_admin_analytics(request, now, week_start, month_start)
            else:
                return Response(
                    {"error": "Invalid user role."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_student_analytics(self, request, now, week_start, month_start):
        """Get analytics data for students"""
        # Submitted Applications
        submitted_applications = JobApplication.objects.filter(applicant=request.user).count()
        applications_this_week = JobApplication.objects.filter(
            applicant=request.user,
            created_at__gte=week_start
        ).count()

        # Interviews Scheduled
        interviews_scheduled = Interview.objects.filter(
            application__applicant=request.user
        ).count()
        interviews_this_week = Interview.objects.filter(
            application__applicant=request.user,
            created_at__gte=week_start
        ).count()

        # Offers Received
        offers_received = Offer.objects.filter(application__applicant=request.user).count()
        offers_this_month = Offer.objects.filter(
            application__applicant=request.user,
            created_at__gte=month_start
        ).count()

        # Saved Jobs
        saved_jobs = SavedJob.objects.filter(student=request.user).count()
        saved_jobs_this_week = SavedJob.objects.filter(
            student=request.user,
            created_at__gte=week_start
        ).count()

        analytics_data = {
            "submitted_applications": {
                "total": submitted_applications,
                "this_week": applications_this_week
            },
            "interviews_scheduled": {
                "total": interviews_scheduled,
                "this_week": interviews_this_week
            },
            "offers_received": {
                "total": offers_received,
                "this_month": offers_this_month
            },
            "saved_jobs": {
                "total": saved_jobs,
                "this_week": saved_jobs_this_week
            }
        }

        return Response(analytics_data, status=status.HTTP_200_OK)

    def _get_employer_analytics(self, request, now, week_start, month_start):
        """Get analytics data for employers"""
        # Get company
        company = request.user.company
        if not company:
            return Response(
                {"error": "No company found for this employer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Active Jobs
        active_jobs = Job.objects.filter(company=company, is_active=True).count()
        active_jobs_this_week = Job.objects.filter(
            company=company, 
            is_active=True, 
            created_at__gte=week_start
        ).count()

        # Applications Count
        applications_count = JobApplication.objects.filter(job__company=company).count()
        applications_this_week = JobApplication.objects.filter(
            job__company=company, 
            created_at__gte=week_start
        ).count()

        # Interviews Scheduled
        interviews_scheduled = Interview.objects.filter(
            application__job__company=company
        ).count()
        interviews_this_week = Interview.objects.filter(
            application__job__company=company,
            created_at__gte=week_start
        ).count()

        # Hires Count (applications with status 'hired')
        hires_count = JobApplication.objects.filter(
            job__company=company, 
            status='hired'
        ).count()
        hires_this_month = JobApplication.objects.filter(
            job__company=company,
            status='hired',
            updated_at__gte=month_start
        ).count()

        analytics_data = {
            "active_jobs": {
                "total": active_jobs,
                "this_week": active_jobs_this_week
            },
            "applications": {
                "total": applications_count,
                "this_week": applications_this_week
            },
            "interviews_scheduled": {
                "total": interviews_scheduled,
                "this_week": interviews_this_week
            },
            "hires": {
                "total": hires_count,
                "this_month": hires_this_month
            }
        }

        return Response(analytics_data, status=status.HTTP_200_OK)

    def _get_admin_analytics(self, request, now, week_start, month_start):
        """Get analytics data for admins"""
        # Total Users
        total_users = User.objects.count()
        users_this_week = User.objects.filter(
            date_joined__gte=week_start
        ).count()

        # Companies
        total_companies = Company.objects.count()
        companies_this_week = Company.objects.filter(
            created_at__gte=week_start
        ).count()

        # Active Jobs
        active_jobs = Job.objects.filter(is_active=True).count()
        active_jobs_this_week = Job.objects.filter(
            is_active=True,
            created_at__gte=week_start
        ).count()

        # Events
        total_events = Event.objects.count()
        events_this_week = Event.objects.filter(
            created_at__gte=week_start
        ).count()

        analytics_data = {
            "total_users": {
                "total": total_users,
                "this_week": users_this_week
            },
            "companies": {
                "total": total_companies,
                "this_week": companies_this_week
            },
            "active_jobs": {
                "total": active_jobs,
                "this_week": active_jobs_this_week
            },
            "events": {
                "total": total_events,
                "this_week": events_this_week
            }
        }

        return Response(analytics_data, status=status.HTTP_200_OK) 


class DashboardInfoEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            now = timezone.now()
            week_ago = now - timedelta(days=7)

            if user_role == "student":
                return self._get_student_dashboard(request, now, week_ago)
            elif user_role == "employer":
                return self._get_employer_dashboard(request, now, week_ago)
            elif user_role == "admin":
                return self._get_admin_dashboard(request, now, week_ago)
            else:
                return Response(
                    {"error": "Invalid user role."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_student_dashboard(self, request, now, week_ago):
        """Get dashboard data for students"""
        # Recent Job Opportunities (active jobs from last 7 days)
        recent_jobs = Job.objects.filter(
            is_active=True,
            created_at__gte=week_ago
        ).select_related('company').order_by('-created_at')[:10]

        # Upcoming Events (events starting in the future)
        upcoming_events = Event.objects.filter(
            is_active=True,
            start_date__gt=now
        ).select_related('company', 'organizer').order_by('start_date')[:10]

        # Upcoming Interviews (scheduled interviews for the student)
        upcoming_interviews = Interview.objects.filter(
            application__applicant=request.user,
            scheduled_at__gt=now,
            status='scheduled'
        ).select_related(
            'application__job__company',
            'interviewer'
        ).order_by('scheduled_at')[:10]

        dashboard_data = {
            "recent_job_opportunities": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company_name": job.company.name,
                    "location": job.location,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "is_remote": job.is_remote,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_currency": job.salary_currency,
                    "created_at": job.created_at,
                    "application_deadline": job.application_deadline,
                }
                for job in recent_jobs
            ],
            "upcoming_events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "event_type": event.event_type,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "location": event.location,
                    "is_virtual": event.is_virtual,
                    "virtual_meeting_url": event.virtual_meeting_url,
                    "organizer_name": event.organizer.get_full_name(),
                    "company_name": event.company.name if event.company else None,
                    "registration_fee": event.registration_fee,
                    "is_registration_required": event.is_registration_required,
                }
                for event in upcoming_events
            ],
            "upcoming_interviews": [
                {
                    "id": interview.id,
                    "job_title": interview.application.job.title,
                    "company_name": interview.application.job.company.name,
                    "interview_type": interview.interview_type,
                    "scheduled_at": interview.scheduled_at,
                    "duration_minutes": interview.duration_minutes,
                    "location": interview.location,
                    "meeting_url": interview.meeting_url,
                    "interviewer_name": interview.interviewer.get_full_name(),
                    "status": interview.status,
                }
                for interview in upcoming_interviews
            ]
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)

    def _get_employer_dashboard(self, request, now, week_ago):
        """Get dashboard data for employers"""
        # Get company
        company = request.user.company
        if not company:
            return Response(
                {"error": "No company found for this employer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Recent Applications (applications from last 7 days)
        recent_applications = JobApplication.objects.filter(
            job__company=company,
            created_at__gte=week_ago
        ).select_related(
            'job', 'applicant'
        ).order_by('-created_at')[:10]

        # Active Jobs
        active_jobs = Job.objects.filter(
            company=company,
            is_active=True
        ).order_by('-created_at')[:10]

        # Upcoming Events (events organized by the employer)
        upcoming_events = Event.objects.filter(
            organizer=request.user,
            start_date__gt=now
        ).select_related('company').order_by('start_date')[:10]

        # Upcoming Interviews (interviews for the employer's company)
        upcoming_interviews = Interview.objects.filter(
            application__job__company=company,
            scheduled_at__gt=now,
            status='scheduled'
        ).select_related(
            'application__job',
            'application__applicant',
            'interviewer'
        ).order_by('scheduled_at')[:10]

        dashboard_data = {
            "recent_applications": [
                {
                    "id": app.id,
                    "job_title": app.job.title,
                    "applicant_name": app.applicant.get_full_name(),
                    "applicant_email": app.applicant.email,
                    "status": app.status,
                    "cover_letter": app.cover_letter[:200] + "..." if len(app.cover_letter) > 200 else app.cover_letter,
                    "expected_salary": app.expected_salary,
                    "available_from": app.available_from,
                    "created_at": app.created_at,
                }
                for app in recent_applications
            ],
            "active_jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "location": job.location,
                    "is_remote": job.is_remote,
                    "application_count": job.application_count,
                    "is_featured": job.is_featured,
                    "created_at": job.created_at,
                    "application_deadline": job.application_deadline,
                }
                for job in active_jobs
            ],
            "upcoming_events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "event_type": event.event_type,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "location": event.location,
                    "is_virtual": event.is_virtual,
                    "registration_count": event.registration_count,
                    "max_participants": event.max_participants,
                    "is_featured": event.is_featured,
                }
                for event in upcoming_events
            ],
            "upcoming_interviews": [
                {
                    "id": interview.id,
                    "job_title": interview.application.job.title,
                    "candidate_name": interview.application.applicant.get_full_name(),
                    "candidate_email": interview.application.applicant.email,
                    "interview_type": interview.interview_type,
                    "scheduled_at": interview.scheduled_at,
                    "duration_minutes": interview.duration_minutes,
                    "location": interview.location,
                    "meeting_url": interview.meeting_url,
                    "interviewer_name": interview.interviewer.get_full_name(),
                }
                for interview in upcoming_interviews
            ]
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)

    def _get_admin_dashboard(self, request, now, week_ago):
        """Get dashboard data for admins"""
        # Recent Users (users who joined in last 7 days)
        recent_users = User.objects.filter(
            date_joined__gte=week_ago
        ).order_by('-date_joined')[:10]

        # System Alerts (various system conditions that need attention)
        system_alerts = []

        # Check for pending job applications (more than 3 days old)
        old_pending_applications = JobApplication.objects.filter(
            status='pending',
            created_at__lt=now - timedelta(days=3)
        ).count()
        if old_pending_applications > 0:
            system_alerts.append({
                "type": "pending_applications",
                "message": f"{old_pending_applications} job applications pending for more than 3 days",
                "severity": "medium",
                "count": old_pending_applications
            })

        # Check for expired jobs
        expired_jobs = Job.objects.filter(
            is_active=True,
            application_deadline__lt=now.date()
        ).count()
        if expired_jobs > 0:
            system_alerts.append({
                "type": "expired_jobs",
                "message": f"{expired_jobs} active jobs have expired",
                "severity": "high",
                "count": expired_jobs
            })

        # Check for upcoming events with low registration
        upcoming_events_low_registration = Event.objects.filter(
            is_active=True,
            start_date__gt=now,
            start_date__lte=now + timedelta(days=7),
            max_participants__isnull=False
        )
        for event in upcoming_events_low_registration:
            registration_rate = event.registration_count / event.max_participants if event.max_participants > 0 else 0
            if registration_rate < 0.3:  # Less than 30% registered
                system_alerts.append({
                    "type": "low_event_registration",
                    "message": f"Event '{event.title}' has low registration ({event.registration_count}/{event.max_participants})",
                    "severity": "low",
                    "event_id": event.id,
                    "registration_rate": registration_rate
                })

        # Check for inactive users (no login for 30+ days)
        inactive_users = User.objects.filter(
            last_active__lt=now - timedelta(days=30),
            is_active=True
        ).count()
        if inactive_users > 0:
            system_alerts.append({
                "type": "inactive_users",
                "message": f"{inactive_users} users have been inactive for 30+ days",
                "severity": "low",
                "count": inactive_users
            })

        # Check for companies without active jobs
        companies_without_jobs = Company.objects.filter(
            jobs__isnull=True
        ).count()
        if companies_without_jobs > 0:
            system_alerts.append({
                "type": "companies_without_jobs",
                "message": f"{companies_without_jobs} companies have no active jobs",
                "severity": "medium",
                "count": companies_without_jobs
            })

        dashboard_data = {
            "recent_users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "date_joined": user.date_joined,
                    "is_active": user.is_active,
                    "is_email_verified": user.is_email_verified,
                }
                for user in recent_users
            ],
            "system_alerts": system_alerts
        }

        return Response(dashboard_data, status=status.HTTP_200_OK) 
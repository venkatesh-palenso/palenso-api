from rest_framework import serializers
from palenso.db.models.job import Job, JobApplication, SavedJob, Interview, Offer
from palenso.api.serializers.company import CompanySerializer


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    company = CompanySerializer(read_only=True)
    application_count = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "application_count", "is_expired"]


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for JobApplication model"""
    applicant_name = serializers.CharField(source="applicant.get_full_name", read_only=True)

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ["id", "applicant", "created_at", "updated_at"]


class SavedJobSerializer(serializers.ModelSerializer):
    """Serializer for SavedJob model"""
    job = JobSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)

    class Meta:
        model = SavedJob
        fields = [
            "id", "student", "student_name", "job", "job_id", "saved_at", "notes"
        ]
        read_only_fields = ["id", "student", "saved_at"]


class InterviewSerializer(serializers.ModelSerializer):
    """Serializer for Interview model"""
    application = JobApplicationSerializer(read_only=True)
    application_id = serializers.IntegerField(write_only=True)
    interviewer_name = serializers.CharField(source="interviewer.get_full_name", read_only=True)
    candidate_name = serializers.CharField(source="application.applicant.get_full_name", read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id", "application", "application_id", "interviewer", "interviewer_name",
            "candidate_name", "interview_type", "scheduled_at", "duration_minutes",
            "location", "meeting_url", "status", "interviewer_notes", "candidate_notes",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer model"""
    application = JobApplicationSerializer(read_only=True)
    application_id = serializers.IntegerField(write_only=True)
    offered_by_name = serializers.CharField(source="offered_by.get_full_name", read_only=True)
    candidate_name = serializers.CharField(source="application.applicant.get_full_name", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "application", "application_id", "offered_by", "offered_by_name",
            "candidate_name", "position_title", "salary_amount", "salary_currency",
            "job_type", "start_date", "offer_deadline", "benefits", "terms_conditions",
            "status", "response_date", "response_notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

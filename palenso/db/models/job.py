from django.db import models

from palenso.db.models.base import BaseModel
from palenso.db.models.company import Company
from palenso.db.models.profile import Resume


class Job(BaseModel):
    """Job Posting Model"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    # Job Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()

    # Job Type and Level
    job_type = models.CharField(
        max_length=20,
        choices=[
            ("full_time", "Full Time"),
            ("part_time", "Part Time"),
            ("contract", "Contract"),
            ("internship", "Internship"),
            ("freelance", "Freelance"),
        ],
    )
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ("entry", "Entry Level"),
            ("mid", "Mid Level"),
            ("senior", "Senior Level"),
            ("executive", "Executive"),
        ],
    )

    # Location and Salary
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    salary_currency = models.CharField(max_length=3, default="USD")

    # Skills and Categories
    required_skills = models.TextField(blank=True)  # Comma-separated skills
    preferred_skills = models.TextField(blank=True)  # Comma-separated skills
    category = models.CharField(max_length=100, blank=True)

    # Application Details
    application_deadline = models.DateField(null=True, blank=True)
    max_applications = models.IntegerField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = "jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    @property
    def application_count(self):
        return self.applications.count()

    @property
    def is_expired(self):
        if self.application_deadline:
            from django.utils import timezone

            return timezone.now().date() > self.application_deadline
        return False


class JobApplication(BaseModel):
    """Job Application Model"""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="job_applications"
    )

    # Application Details
    cover_letter = models.TextField()
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("reviewed", "Reviewed"),
            ("shortlisted", "Shortlisted"),
            ("interviewed", "Interviewed"),
            ("offered", "Offered"),
            ("hired", "Hired"),
            ("rejected", "Rejected"),
            ("withdrawn", "Withdrawn"),
        ],
        default="pending",
    )

    # Additional Information
    expected_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    available_from = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Employer Notes (private)
    employer_notes = models.TextField(blank=True)

    class Meta:
        db_table = "job_applications"
        ordering = ["-created_at"]
        unique_together = ["job", "applicant"]

    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.job.title}"


class SavedJob(BaseModel):
    """Saved Jobs for Students"""

    student = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="saved_jobs"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "saved_jobs"
        ordering = ["-saved_at"]
        unique_together = ["student", "job"]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.job.title}"

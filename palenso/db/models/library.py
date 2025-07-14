from django.db import models
from django.core.validators import FileExtensionValidator
from .base import BaseModel


class Profile(BaseModel):
    """User Profile model to store additional user information"""
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    bio = models.TextField(blank=True, max_length=500)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, 
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    # Contact Information
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Location
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Education(BaseModel):
    """User Education History"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_education'
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"


class WorkExperience(BaseModel):
    """User Work Experience"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_work_experience'
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"


class Skill(BaseModel):
    """User Skills"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate'
    )
    
    class Meta:
        db_table = 'user_skills'
        unique_together = ['profile', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.proficiency_level})"


class Interest(BaseModel):
    """User Interests/Hobbies"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_interests'
        unique_together = ['profile', 'name']
    
    def __str__(self):
        return self.name


class Project(BaseModel):
    """User Projects"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies_used = models.TextField(blank=True)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='project_images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    class Meta:
        db_table = 'user_projects'
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return self.title


class Resume(BaseModel):
    """User Resume"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    is_primary = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_resumes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.profile.user.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary resume per profile
        if self.is_primary:
            Resume.objects.filter(profile=self.profile, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

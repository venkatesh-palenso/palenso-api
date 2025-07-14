from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from palenso.db.models import User, Profile, Education, WorkExperience, Skill, Interest, Project, Resume
from palenso.api.serializers.auth import (
    UserProfileSerializer, ProfileSerializer, EducationSerializer, WorkExperienceSerializer,
    SkillSerializer, InterestSerializer, ProjectSerializer, ResumeSerializer
)


class UserProfileView(APIView):
    """Get and update user profile"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        """Get user profile with all related data"""
        try:
            user = request.user
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request):
        """Update user profile"""
        try:
            user = request.user
            profile = user.profile
            
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class EducationView(APIView):
    """CRUD operations for education"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, education_id=None):
        """Get education records"""
        try:
            user = request.user
            if education_id:
                education = get_object_or_404(Education, id=education_id, profile=user.profile)
                serializer = EducationSerializer(education)
            else:
                education_list = Education.objects.filter(profile=user.profile)
                serializer = EducationSerializer(education_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new education record"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = EducationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, education_id):
        """Update education record"""
        try:
            user = request.user
            education = get_object_or_404(Education, id=education_id, profile=user.profile)
            
            serializer = EducationSerializer(education, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, education_id):
        """Delete education record"""
        try:
            user = request.user
            education = get_object_or_404(Education, id=education_id, profile=user.profile)
            education.delete()
            return Response({"message": "Education record deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WorkExperienceView(APIView):
    """CRUD operations for work experience"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, experience_id=None):
        """Get work experience records"""
        try:
            user = request.user
            if experience_id:
                experience = get_object_or_404(WorkExperience, id=experience_id, profile=user.profile)
                serializer = WorkExperienceSerializer(experience)
            else:
                experience_list = WorkExperience.objects.filter(profile=user.profile)
                serializer = WorkExperienceSerializer(experience_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new work experience record"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = WorkExperienceSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, experience_id):
        """Update work experience record"""
        try:
            user = request.user
            experience = get_object_or_404(WorkExperience, id=experience_id, profile=user.profile)
            
            serializer = WorkExperienceSerializer(experience, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, experience_id):
        """Delete work experience record"""
        try:
            user = request.user
            experience = get_object_or_404(WorkExperience, id=experience_id, profile=user.profile)
            experience.delete()
            return Response({"message": "Work experience deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SkillView(APIView):
    """CRUD operations for skills"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, skill_id=None):
        """Get skills"""
        try:
            user = request.user
            if skill_id:
                skill = get_object_or_404(Skill, id=skill_id, profile=user.profile)
                serializer = SkillSerializer(skill)
            else:
                skills = Skill.objects.filter(profile=user.profile)
                serializer = SkillSerializer(skills, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new skill"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = SkillSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, skill_id):
        """Update skill"""
        try:
            user = request.user
            skill = get_object_or_404(Skill, id=skill_id, profile=user.profile)
            
            serializer = SkillSerializer(skill, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, skill_id):
        """Delete skill"""
        try:
            user = request.user
            skill = get_object_or_404(Skill, id=skill_id, profile=user.profile)
            skill.delete()
            return Response({"message": "Skill deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class InterestView(APIView):
    """CRUD operations for interests"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, interest_id=None):
        """Get interests"""
        try:
            user = request.user
            if interest_id:
                interest = get_object_or_404(Interest, id=interest_id, profile=user.profile)
                serializer = InterestSerializer(interest)
            else:
                interests = Interest.objects.filter(profile=user.profile)
                serializer = InterestSerializer(interests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new interest"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = InterestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, interest_id):
        """Update interest"""
        try:
            user = request.user
            interest = get_object_or_404(Interest, id=interest_id, profile=user.profile)
            
            serializer = InterestSerializer(interest, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, interest_id):
        """Delete interest"""
        try:
            user = request.user
            interest = get_object_or_404(Interest, id=interest_id, profile=user.profile)
            interest.delete()
            return Response({"message": "Interest deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProjectView(APIView):
    """CRUD operations for projects"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, project_id=None):
        """Get projects"""
        try:
            user = request.user
            if project_id:
                project = get_object_or_404(Project, id=project_id, profile=user.profile)
                serializer = ProjectSerializer(project)
            else:
                projects = Project.objects.filter(profile=user.profile)
                serializer = ProjectSerializer(projects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new project"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = ProjectSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, project_id):
        """Update project"""
        try:
            user = request.user
            project = get_object_or_404(Project, id=project_id, profile=user.profile)
            
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, project_id):
        """Delete project"""
        try:
            user = request.user
            project = get_object_or_404(Project, id=project_id, profile=user.profile)
            project.delete()
            return Response({"message": "Project deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResumeView(APIView):
    """CRUD operations for resumes"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, resume_id=None):
        """Get resumes"""
        try:
            user = request.user
            if resume_id:
                resume = get_object_or_404(Resume, id=resume_id, profile=user.profile)
                serializer = ResumeSerializer(resume)
            else:
                resumes = Resume.objects.filter(profile=user.profile)
                serializer = ResumeSerializer(resumes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def post(self, request):
        """Create new resume"""
        try:
            user = request.user
            data = request.data.copy()
            data['profile'] = user.profile.id
            
            serializer = ResumeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def put(self, request, resume_id):
        """Update resume"""
        try:
            user = request.user
            resume = get_object_or_404(Resume, id=resume_id, profile=user.profile)
            
            serializer = ResumeSerializer(resume, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, resume_id):
        """Delete resume"""
        try:
            user = request.user
            resume = get_object_or_404(Resume, id=resume_id, profile=user.profile)
            resume.delete()
            return Response({"message": "Resume deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong. Please try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            ) 
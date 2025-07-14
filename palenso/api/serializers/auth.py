from rest_framework import serializers
from palenso.db.models import User, Token, Profile, Education, WorkExperience, Skill, Interest, Project, Resume


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name',
            'is_email_verified', 'is_mobile_verified', 'is_active', 'date_joined',
            'last_active'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_active']


class CheckAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking email/mobile availability"""
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(max_length=15, required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        
        if not email and not mobile_number:
            raise serializers.ValidationError("Either email or mobile number is required.")
        
        if email and mobile_number:
            raise serializers.ValidationError("Please provide either email or mobile number, not both.")
        
        return attrs


class CreateUserSerializer(serializers.Serializer):
    """Serializer for creating user with contact information"""
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255, required=False, default="")
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(max_length=15, required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        
        if not email and not mobile_number:
            raise serializers.ValidationError("Either email or mobile number is required.")
        
        # Check if user already exists
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        
        if mobile_number:
            mobile_number = mobile_number.strip()
            if User.objects.filter(mobile_number=mobile_number).exists():
                raise serializers.ValidationError("A user with this mobile number already exists.")
        
        return attrs


class SendVerificationCodeSerializer(serializers.Serializer):
    """Serializer for sending verification codes"""
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(max_length=15, required=False)
    user_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        user_id = attrs.get('user_id')

        print(user_id)
        
        if not email and not mobile_number:
            raise serializers.ValidationError("Either email or mobile number is required.")
        
        if email and mobile_number:
            raise serializers.ValidationError("Please provide either email or mobile number, not both.")
        
        return attrs


class CompleteSignupSerializer(serializers.Serializer):
    """Serializer for completing signup with password"""
    user_id = serializers.UUIDField()
    password = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        user_id = attrs.get('user_id')
        try:
            user = User.objects.get(id=user_id, is_active=False)
            if user.password:  # User already has password set
                raise serializers.ValidationError("User signup already completed.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user ID or user not found.")
        
        return attrs


class SignInSerializer(serializers.Serializer):
    """Serializer for user signin"""
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(max_length=15, required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        
        if not email and not mobile_number:
            raise serializers.ValidationError("Either email or mobile number is required.")
        
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class VerifyMobileSerializer(serializers.Serializer):
    """Serializer for mobile verification"""
    mobile_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password"""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password"""
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education"""
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['profile']


class WorkExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience"""
    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ['profile']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills"""
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ['profile']


class InterestSerializer(serializers.ModelSerializer):
    """Serializer for interests"""
    class Meta:
        model = Interest
        fields = '__all__'
        read_only_fields = ['profile']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects"""
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['profile']


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for resumes"""
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ['profile']


class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer with all related data"""
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name',
            'is_email_verified', 'is_mobile_verified', 'is_active', 'date_joined',
            'last_active', 'profile'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_active']
    
    def to_representation(self, instance):
        """Custom representation to include related data"""
        data = super().to_representation(instance)
        if hasattr(instance, 'profile') and instance.profile:
            data['education'] = EducationSerializer(instance.profile.education.all(), many=True).data
            data['work_experience'] = WorkExperienceSerializer(instance.profile.work_experience.all(), many=True).data
            data['skills'] = SkillSerializer(instance.profile.skills.all(), many=True).data
            data['interests'] = InterestSerializer(instance.profile.interests.all(), many=True).data
            data['projects'] = ProjectSerializer(instance.profile.projects.all(), many=True).data
            data['resumes'] = ResumeSerializer(instance.profile.resumes.all(), many=True).data
        return data 
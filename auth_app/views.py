from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from apis.models import (
    Profile,
)  # Make sure to replace 'your_app' with the actual name of your Django app
import uuid
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from .models import Emails


from django.db import transaction

@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    try:
        with transaction.atomic():
            # Retrieve data from the request
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")
            referral_code = request.data.get("refferal_code")
            phone_number = request.data.get("phone_number")
            print(referral_code )
            
            # Check if referral code is valid
            referring_user = None
           
            if referral_code:
                try:
                    referring_user = Profile.objects.get(gameId=referral_code)
                    print(referring_user)
                except User.DoesNotExist:
                    print()
                    raise ValidationError("Invalid referral code.")
            else:
                referral_code = User.objects.filter(is_superuser=True).first().profile.gameId
                
            # Generate a unique gameId using UUID
            gameId = str(uuid.uuid4())

            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            try:
                # Create a profile for the new user with the unique gameId
                profile = Profile.objects.create(
                    user=user, email=email, gameId=gameId, phone_no=phone_number
                )

                # If there is a referral, associate the new user with the referring user
                if referring_user:
                    profile.level_1 = referring_user.user
                    if referring_user.level_1 is not None :
                        profile.level_2 = referring_user.level_1
                    if  referring_user.level_2 is not None:
                        profile.level_3 = referring_user.level_2
                    profile.save()
                return Response(
                    {"message": "User registered successfully."},
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as ve:
                user.delete()
                raise ve

    except ValidationError as e:
        if user:
            user.delete()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        
        print(request.data)
        return Response(
            {"error": f"An unexpected error occurred. {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def send_email(link, email):
    subject = "Veto Gaming Confirmation Email"
    from_email = "no-reply@vetogaming.com"
    to_email = email

    # Get the HTML template
    html_template = get_template("confirm.html")

    # Render the HTML content with context data
    context_data = {"link": link}  # Add any context data needed in the template
    html_content = html_template.render(context_data)

    # Create a plain text version of the email
    text_content = strip_tags(html_content)

    # Create the EmailMultiAlternatives object
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])

    # Attach the HTML content to the email
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()

    # You can redirect to a success page or return a response as needed


@api_view(["POST"])
@permission_classes([AllowAny])
def send_forget_password_email(request):
    # Get data from the request
    host = request.data.get("origin")
    email = request.data.get("email")

    try:
        # Check if the user with the given email exists
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # If the user does not exist, return an error response
        return Response(
            {"error": "User with this email does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        # Send forget password email
        code = str(uuid.uuid4())
        send_email(f"{host}/auth/reset?uuid-temp-code={code}", email)
        create_email = Emails.objects.create(code=code, email=email, used=False)
        create_email.save()
        return Response(
            {"message": f"Email sent successfully."}, status=status.HTTP_200_OK
        )
    except Exception as e:
        # Handle any other exceptions that might occur during email sending
        return Response(
            {"error": f"Failed to send email. Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


User = get_user_model()


from django.utils import timezone
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    unique_code = request.data.get("unique_code")

    email_obj = get_object_or_404(Emails, code=unique_code, used=False)

    # Check if the code is older than 10 minutes
    expiration_time = email_obj.created_at + timedelta(minutes=10)
    if timezone.now() > expiration_time:
        return Response({"message": "Code has expired."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email_obj.email)
    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)


    new_password = request.data.get("new_password")

    # Validate the new password
    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return Response({"message": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's password
    user.set_password(new_password)
    user.save()

    # Mark the code as used
    email_obj.used = True
    email_obj.save()

    # Update the session to prevent the user from being logged out
    update_session_auth_hash(request, user)

    return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)



@api_view(["GET"])
def Team(request):
    try:
        user = Profile.objects.get()
        return Response(
            {
                "username": user.username,
                "email": user.email,
                "phone_number": user.profile.phone_no,
                "referral_code": user.profile.gameId,
            },
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    # Get the user making the request
    user = request.user

    # Get old_password and new_password from the request data
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    # Check if the old_password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
    


@api_view(['POST'])
def upload_image(request):
    user = request.user
    image = request.FILES.get('image')

    if image:
        # Update the user's profile with the uploaded image
        profile, created = Profile.objects.get_or_create(user=user)
        profile.image = image  # This assumes that your model's image field is an ImageField
        profile.save()

        return Response({"message": "Image uploaded successfully"})
    else:
        return Response({"error": "No image provided in the request"}, status=400)
   
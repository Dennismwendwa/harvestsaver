from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import auth

from .models import (User, FarmerProfile, BuyerProfile, EquipmentOwnerProfile,
                     Profile)
from .models import Contact
from .forms import ContactForm, FarmerProfileForm, BuyerProfileForm, EquipmentOwnerProfileForm

from .utils.functions import create_group_and_permission


def register(request):
    """This is register view
       args: first name, last name, username, email, password1,
             password2, role, phone_number, gender, country
    """
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        role = request.POST["role"]
        phone_number = request.POST.get("phone_number", "")
        gender = request.POST["gender"]
        country = request.POST["country"]

        if password1 == password2 and len(password1) >= 8:
            
            if User.objects.filter(username=username).exists():
                messages.warning(request, f"username taken")
                return redirect("accounts:register")
            elif User.objects.filter(email=email).exists():
                messages.warning(request, f"email already in use")
                return redirect("accounts:register")
            else:
                user = User.objects.create_user(first_name=first_name,
                                                last_name=last_name,
                                                email=email,
                                                username=username,
                                                password=password1,
                                                phone_number=phone_number,
                                                gender=gender,
                                                country=country,
                                                role=role,
                                                )

                if role == User.Role.STAFF:
                    user.is_staff = True
                    user.save(update_fields=["is_staff"])
                
                if role == "farmer" or role == "equipment_owner":
                    create_group_and_permission(role, user)
                status = login_helper(username, password1, request)
                if status == "farmer":
                    return redirect("farm:farmer_dashboard")
                elif status == "equipment":
                    return redirect("farm:equipment_dashboard")
                elif status == "success":
                    return redirect("farm:home")

        elif len(password1) < 8:
            messages.warning(request, f"Passward must have 8 or more characters")
            return redirect("accounts:register")
        else:
            messages.warning(request, f"Password not matching")
            return redirect("accounts:register")

    return render(request, "accounts/register.html")

def login_helper(username, password, request):
    """This function is for login users"""
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        if user.is_farmer:
            return "farmer"
        elif user.is_equipment_owner:
            return "equipment"
        else:
            return "success"
    else:
        messages.warning(request, f"Wrong password or username")
        return redirect("accounts:login")    

def login(request):
    """This is login view
    Args: username required
          password required
    """
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if not password and username:
            messages.warning(request, f"Please enter both username and password")
            return redirect("accounts:login")

        next_param = request.GET.get('next', '')
        status = login_helper(username, password, request)

        if next_param:
            return redirect(next_param)
        elif status == "farmer":
            return redirect("farm:farmer_dashboard")
        elif status == "equipment":
            return redirect("farm:equipment_dashboard")
        elif status == "success":
            return redirect("farm:home")

    return render(request, "accounts/login.html")

def logout(request):
    """This is logout view"""

    auth.logout(request)
    return redirect("farm:home")

def contact(request):
    
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

            email_message = f"Name: {name}\nEmail: {email}\nSubject\n\n{message}"

            send_mail(
                subject = "New cantact form submission",
                message = email_message,
                from_email = email,
                recipient_list = ["dennissoftware3@gmail.com",],
                fail_silently = False,
            )

            messages.success(request, f"Your message has been sent. Thank you")
            return redirect("accounts:contact")
        else:
            return render(request, "accounts/conatact.html", {"form": form})
    else:
        form = ContactForm()

    context = {"form": form,}
    return render(request, "accounts/conatact.html", context)

def aboutus(request):
    return render(request, "accounts/aboutus.html")

def get_profile_and_form(user):
    if hasattr(user, "farmerprofile"):
        return user.farmerprofile, FarmerProfileForm
    elif hasattr(user, "buyerprofile"):
        return user.buyerprofile, BuyerProfileForm
    elif hasattr(user, "equipmentownerprofile"):
        return user.equipmentownerprofile, EquipmentOwnerProfileForm
    else:
        raise Exception("User has no profile")

def profile(request):
    """
    Docstring for profile
    
    This view is for updating and rendering user profile
    """
    user = request.user
    profile, form_class = get_profile_and_form(user)

    if request.method == "POST":
        form = form_class(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("accounts:profile")
    else:
        form = form_class(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "accounts/profile.html", context)



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth, Group
from django.core.mail import send_mail

from .models import User, FarmerProfile, BuyerProfile, EquipmentOwnerProfile
from .models import Contact
from .forms import ContactForm


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
                                                phone_number=phone_number,
                                                gender=gender,
                                                country=country,
                                                username=username,
                                                password=password1
                                                )
                if role == "farmer":
                    user.is_farmer = True
                    FarmerProfile.objects.create(user=user)
                elif role == "equipment owner":
                    user.is_equipment_owner = True
                    EquipmentOwnerProfile.objects.create(user=user)
                elif role == "customer":
                    user.is_customer = True
                    BuyerProfile.objects.create(user=user)
                elif role == "staff":
                    user.is_staff = True
                user.save()

                role = role.capitalize()
                try:
                    group = Group.objects.get(name=role)
                except Group.DoesNotExist:
                    group = Group.objects.create(name=role)
                
                group.user_set.add(user)
                user = auth.authenticate(username=username, password=password1)
                
                if user is not None:
                    auth.login(request, user)
                    return redirect("farm:home")

        elif len(password1) < 8:
            messages.warning(request, f"Passward must have 8 or more characters")
            return redirect("accounts:register")
        else:
            messages.warning(request, f"Password not matching")
            return redirect("accounts:register")

    return render(request, "accounts/register.html")


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

        user = auth.authenticate(username=username, password=password)
        next_param = request.GET.get('next', '')
        if user is not None:
            auth.login(request, user)
            return redirect(next_param if next_param else "farm:home")
        else:
            messages.warning(request, f"Wrong password or username")
            return redirect("accounts:login")

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
        form = ContactForm()

    context = {"form": form,}
    return render(request, "accounts/conatact.html", context)


def aboutus(request):
    return render(request, "accounts/aboutus.html")

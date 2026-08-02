from django.shortcuts import render, redirect
from datetime import datetime, date
from .models import Project, Notification, Event, User
import json
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.functions import TruncMonth
from django.db.models import Count
import re
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta







# home  Page
def LSpage(request):
    return render(request, 'LSPage.html')


# Login Page

def loginpage(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        # ✅ empty check
        if not email or not password:
            return render(request, 'Loginpage.html', {
                'error': 'All fields are required'
            })

        try:
            user = User.objects.get(email=email)

            # ✅ check password
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect('DSBord')
            else:
                return render(request, 'Loginpage.html', {
                    'error': 'Wrong password'
                })

        except User.DoesNotExist:
            return render(request, 'Loginpage.html', {
                'error': 'Email not found'
            })

    return render(request, 'Loginpage.html')
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get('email')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            return redirect('loginpage')

        except User.DoesNotExist:
            return render(request, 'forgotpassword.html', {
                'error': 'Email not found'
            })

    return render(request, 'forgotpassword.html')
def DSBord(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')
    
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)


    active = Project.objects.filter(user_id=user_id, status='active').count()
    in_progress = Project.objects.filter(user_id=user_id, status='in_progress').count()
    completed = Project.objects.filter(user_id=user_id, status='completed').count()
    overdue = Project.objects.filter(user_id=user_id, status='overdue').count()

    total_projects = active + in_progress + completed + overdue

    # Monthly chart
    monthly_data = (
        Project.objects
        .filter(user_id=user_id)
        .annotate(month=TruncMonth('start_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = []
    counts = []

    for item in monthly_data:
        if item['month']:
            months.append(item['month'].strftime('%b'))
            counts.append(item['count'])

    if not months:
        months = ["No Data"]
        counts = [0]

    # AI insights
    insights = get_insights(user)

    return render(request, 'DSBoard.html', {
        'user':user,
        'insights': insights,
        'in_progress': in_progress,
        'completed': completed,
        'overdue': overdue,
        'active': active,
        'total_projects': total_projects,
        'months': json.dumps(months),
    'counts': json.dumps(counts),
    })
# Create New Page
def CreateNewPage(request):
    return render(request,'CreateNew.html')



def calender(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user_id = request.session['user_id']

    # ✅ RUN LOGIC
    check_event_notifications(user_id)
    delete_old_events(user_id)

    events = Event.objects.filter(user_id=user_id)

    event_list = []

    for e in events:

        color = "blue"

        if "deadline" in e.title.lower():
            color = "red"
        elif "meeting" in e.title.lower():
            color = "purple"
        elif "launch" in e.title.lower():
            color = "yellow"
        elif "task" in e.title.lower():
            color = "green"

        event_list.append({
            "id": e.id,
            "title": e.title,
            "start": str(e.date),
            "className": color   
        })

    return render(request, 'calendar.html', {
        'events': json.dumps(event_list),
        'user': User.objects.get(id=user_id)
    })
def create_project(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    if request.method == "POST":
        name = request.POST.get('project_name')
        description = request.POST.get('project_description')
        file = request.FILES.get('project_file')
        start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d").date()

        user = User.objects.get(id=request.session['user_id'])

        # ✅ SAVE PROJECT FIRST
        project = Project.objects.create(
            user=user,
            project_name=name,
            project_description=description,
            project_file=file,
            start_date=start_date,
            end_date=end_date
        )

        # ✅ LINK PROJECT TO NOTIFICATION
        Notification.objects.create(
            user=user,
            title="New Project Created",
            message=f"{name} project created successfully",
            type="project",
            project=project
        )

        return redirect('project')

    return render(request, 'CreateNew.html')


# Signup page

def signup(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        # ✅ empty fields check
        if not username or not email or not password or not confirm:
            messages.error(request, 'All fields are required')
            return redirect('signup')

        # ✅ password match
        if password != confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        # ✅ email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        # ✅ password length
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return redirect('signup')

        # ✅ at least 2 letters
        if len(re.findall(r'[A-Za-z]', password)) < 2:
            messages.error(request, 'Password must contain at least 2 letters')
            return redirect('signup')

        # ✅ at least 2 numbers
        if len(re.findall(r'[0-9]', password)) < 2:
            messages.error(request, 'Password must contain at least 2 numbers')
            return redirect('signup')

        # ✅ at least 1 special character
        if not re.search(r'[@$!%*?&]', password):
            messages.error(request, 'Password must contain at least 1 special character')
            return redirect('signup')

        # ✅ create user (hashed password)
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        # ✅ success message
        messages.success(request, 'Account created successfully! Please login.')

        return redirect('loginpage')

    return render(request, 'signup.html')

# profile page
def profile(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user = User.objects.get(id=request.session['user_id'])

    if request.method == "POST":
        user.role = request.POST.get('role')

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']

        user.save()
        return redirect('profile')

    return render(request, 'profile.html', {'user': user})
# noti page
def notification(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)

    filter_type = request.GET.get('type')
    
    if request.GET.get('deleted'):
        messages.error(request, "This project is no longer available.")

    notifications = Notification.objects.filter(user_id=user_id)

    # counts
    counts = notifications.values('type').annotate(count=Count('id'))

    count_dict = {
        'project': 0,
        'deadline': 0,
        'update': 0,
        'delete': 0
    }

    for item in counts:
        count_dict[item['type']] = item['count']

    if filter_type:
        notifications = notifications.filter(type=filter_type)
    

    notifications = notifications.order_by('-created_at')

    return render(request, 'notification.html', {
        'notifications': notifications,
        'filter_type': filter_type,
        'counts': count_dict,
        'user': user
    })
    
def mark_read(request, id):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    try:
        notification = Notification.objects.get(id=id)
        notification.is_read = True
        notification.save()
    except Notification.DoesNotExist:
        return redirect('notification')

    next_url = request.GET.get('next')

    if next_url:
        return redirect(next_url)

    return redirect('notification')

def check_deadline_notifications(user_id):

    today = date.today()
    user = User.objects.get(id=user_id)

    projects = Project.objects.filter(
        user=user,
        end_date__isnull=False,
        end_date__lte=today
    )

    print("Checking deadlines...")
    print(projects)

    for project in projects:

        message = f"{project.id} - {project.project_name} deadline missed!"

        exists = Notification.objects.filter(
            user=user,
            message=message
        ).exists()

        if not exists:
            print("Creating notification for:", project.project_name)

            Notification.objects.create(
                user=user,
                title="Deadline Alert",
                message=message,  
                type="deadline"
            )
# project page
def project(request):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user_id = request.session['user_id']

    
    check_overdue_projects(user_id)

    
    status_filter = request.GET.get('status')

    
    projects = Project.objects.filter(user_id=user_id)

    if status_filter:
        projects = projects.filter(status=status_filter)
        
    user = User.objects.get(id=user_id)   


    return render(request, 'projects.html', {
        'projects': projects,
        'status': status_filter,
        'user': user
    })

def update_status(request, project_id, status):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    project = Project.objects.get(id=project_id, user_id=request.session['user_id'])

    project.status = status
    project.save()

    return redirect('project')

def delete_project(request, id):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user = User.objects.get(id=request.session['user_id'])
    project = Project.objects.get(id=id, user=user)

    project_name = project.project_name  # ✅ store name

    project.delete()  # delete project

    # ✅ CREATE DELETE NOTIFICATION
    Notification.objects.create(
        user=user,
        title="Project Deleted",
        message=f'"{project_name}" has been deleted successfully',
        type="delete"
    )
    return redirect('project')



def check_overdue_projects(user_id):
    projects = Project.objects.filter(user_id=user_id)

    today = date.today()

    for project in projects:
        if project.end_date and project.end_date < today and project.status not in ['completed', 'archived']:
            project.status = 'overdue'
            project.save()
            
            


def project_detail(request, id):

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('loginpage')
    
    user = User.objects.get(id=user_id)

    try:
        project = Project.objects.get(id=id, user_id=user_id)
    except Project.DoesNotExist:
        messages.error(request, "This project is no longer available.")
        return redirect('notification')

    if request.method == "POST":
        new_file = request.FILES.get('new_file')

        if new_file:
            project.project_file = new_file
            project.save()
            messages.success(request, "File uploaded successfully!")
            return redirect('project_detail', id=id)

    return render(request, 'project_detail.html', {
        'user': user,
        'project': project
    })
    
def delete_file(request, id):
    if not request.session.get('user_id'):
        return redirect('loginpage')

    project = get_object_or_404(Project, id=id, user_id=request.session['user_id'])

    if project.project_file:
        project.project_file.delete(save=False)
        project.project_file = None
        project.save()
        messages.success(request, "File deleted successfully.")

    return redirect('project_detail', id=id)

def edit_project(request, id):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    user = User.objects.get(id=request.session['user_id'])  # ✅ FIXED

    project = Project.objects.get(id=id)

    if request.method == "POST":
        project.project_description = request.POST.get('description')
        project.save()
        return redirect('project_detail', id=id)

    return render(request, 'edit_project.html', {
        'user': user,   # ✅ FIXED
        'project': project
    })

def update_status_dropdown(request, id):

    if not request.session.get('user_id'):
        return redirect('loginpage')

    project = Project.objects.get(id=id, user_id=request.session['user_id'])

    if request.method == "POST":
        new_status = request.POST.get('status')
        project.status = new_status
        project.save()

    return redirect('project_detail', id=id)

def improve_description(request):
    if request.method == "POST":
        
        data = json.loads(request.body)

        text = data.get("text", "").lower()

        completed = []
        progress = []
        next_steps = []

        # SMART KEYWORDS
        if "fix" in text or "bug" in text:
            completed.append("Fixed bugs")

        if "create" in text or "build" in text:
            completed.append("Developed new feature")

        if "login" in text:
            completed.append("Implemented login system")

        if "api" in text:
            progress.append("Working on API integration")
            next_steps.append("Complete API development")

        if "design" in text:
            completed.append("Improved UI/UX design")

        # DEFAULT FALLBACK
        if not completed:
            completed.append("Worked on project tasks")

        if not progress:
            progress.append("Development in progress")

        if not next_steps:
            next_steps.append("Continue development")
            next_steps.append("Complete pending tasks")

        # FORMAT OUTPUT
        result = "📅 Daily Progress Report\n\n"

        result += "✅ Completed Tasks:\n"
        for c in completed:
            result += f"- {c}\n"

        result += "\n🚧 In Progress:\n"
        for p in progress:
            result += f"- {p}\n"

        result += "\n📌 Summary:\n"
        result += "Development is progressing smoothly with continuous improvements.\n"

        result += "\n🚀 Next Plan:\n"
        for n in next_steps:
            result += f"- {n}\n"

        
        return JsonResponse({"result": result})


@csrf_exempt
def add_event(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(id=request.session['user_id'])

        event = Event.objects.create(
            user=user,
            title=data['title'],
            date=data['date']
        )

        # ✅ CREATE NOTIFICATION WHEN EVENT ADDED
        Notification.objects.create(
            user=user,
            title="New Event",
            message=f"{event.title} scheduled on {event.date}",
            type="event"
        )

        return JsonResponse({
            "status": "success",
            "id": event.id})
    


def check_event_notifications(user_id):
    today = date.today()
    user = User.objects.get(id=user_id)

    events = Event.objects.filter(user=user)

    for e in events:
        days_left = (e.date - today).days

        # 🔵 2 DAYS BEFORE
        if days_left == 2:
            message = f"{e.title} is in 2 days"

        # 🟡 1 DAY BEFORE
        elif days_left == 1:
            message = f"{e.title} is tomorrow"

        # 🔴 TODAY
        elif days_left == 0:
            message = f"{e.title} is today"

        else:
            continue

        # ✅ PREVENT DUPLICATE
        exists = Notification.objects.filter(
            user=user,
            message=message
        ).exists()

        if not exists:
            Notification.objects.create(
                user=user,
                title="Event Reminder",
                message=message,
                type="event"
            )
        
def delete_old_events(user_id):
    today = date.today()
    Event.objects.filter(user_id=user_id, date__lt=today).delete()

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@csrf_exempt
def delete_event(request):
    if request.method == "POST":
        data = json.loads(request.body)

        event_id = data.get('id')
        user = User.objects.get(id=request.session['user_id'])

        try:
            event = Event.objects.get(id=event_id, user=user)

            event_title = event.title
            event_date = event.date

            # 🔥 DELETE EVENT
            event.delete()

            # 🔔 CREATE NOTIFICATION
            Notification.objects.create(
                user=user,
                title="Event Deleted",
                message=f"{event_title} on {event_date} has been deleted",
                type="delete"
            )

            return JsonResponse({"status": "deleted"})

        except Event.DoesNotExist:
            return JsonResponse({"status": "error"})
@csrf_exempt
@csrf_exempt
def update_event(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(id=request.session['user_id'])

        try:
            event = Event.objects.get(
                id=data['id'],
                user=user
            )

            old_date = event.date  # 🧠 store old date

            # 🔥 UPDATE EVENT
            event.title = data['title']
            event.date = data['date']
            event.save()

            # 🔔 CREATE NOTIFICATION
            Notification.objects.create(
                user=user,
                title="Event Updated",
                message=f"{event.title} moved from {old_date} to {event.date}",
                type="update"
            )

            return JsonResponse({"status": "updated"})

        except Event.DoesNotExist:
            return JsonResponse({"status": "error"})







def get_insights(user):

    today = date.today()
    insights = []

    # 🔴 OVERDUE (TOP PRIORITY)
    overdue = Project.objects.filter(
        user=user,
        end_date__lt=today,
        status='overdue'
    ).count()

    if overdue > 0:
        insights.append(("danger", f"{overdue} overdue projects — fix immediately"))

    # 📅 EVENTS (SMART COMBINE)
    next_week = today + timedelta(days=7)

    upcoming = Event.objects.filter(
        user=user,
        date__range=(today, next_week)
    ).count()

    if upcoming >= 5:
        insights.append(("warning", f"{upcoming} events this week — schedule wisely"))
    elif upcoming > 0:
        insights.append(("info", f"{upcoming} events upcoming"))

    # 🔄 IN PROGRESS
    in_progress = Project.objects.filter(
        user=user,
        status='in_progress'
    ).count()

    if in_progress >= 5:
        insights.append(("warning", f"{in_progress} projects running — focus on priorities"))
    elif in_progress > 0:
        insights.append(("progress", f"Working on {in_progress} projects"))

    # ✅ COMPLETED
    completed = Project.objects.filter(
        user=user,
        status='completed'
    ).count()

    if completed > 0:
        insights.append(("success", f"{completed} projects completed — keep momentum"))

    # 💤 NO ACTIVITY
    today_activity = Notification.objects.filter(
        user=user,
        created_at__date=today
    ).count()

    if today_activity == 0:
        insights.append(("info", "No activity today — start a task"))

    # 📊 WEEKLY SUMMARY
    total_projects = Project.objects.filter(user=user).count()

    if total_projects >= 10:
        insights.append(("info", f"You are managing {total_projects} projects — stay organized"))

    # 🔥 PRIORITY SORT
    priority = {
        "danger": 1,
        "warning": 2,
        "progress": 3,
        "success": 4,
        "info": 5
    }

    insights.sort(key=lambda x: priority[x[0]])

    # ✅ LIMIT (MAX 5)
    insights = insights[:5]

    # 🟢 DEFAULT
    if not insights:
        insights.append(("info", "Everything looks good — keep going!"))

    return insights

from django.http import JsonResponse

def get_insights_api(request):

    if not request.session.get('user_id'):
        return JsonResponse({'error': 'not logged in'})

    user = User.objects.get(id=request.session['user_id'])

    insights = get_insights(user)

    return JsonResponse({'insights': insights})
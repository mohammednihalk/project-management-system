from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    project_name = models.CharField(max_length=200)
    project_description = models.TextField(blank=True,null=True)
    project_file = models.FileField(upload_to='projects/', null=True, blank=True)
    title = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('overdue', 'Overdue'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    message = models.TextField()

    type = models.CharField(max_length=50)  # project, deadline, update

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.title
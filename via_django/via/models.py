from django.db import models
from django.utils import timezone
import datetime
from django.db.models import JSONField
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=300)
    settings = JSONField(null=True, blank=True, editable=False)
    attributes = JSONField(null=True, blank=True, editable=False)
    data_format_version = models.CharField(max_length=64, default="2.0.10")

    @property
    def image_count(self):
        return self.image_set.count()

    def __str__(self):
        return f"{self.name}. " \
               f"images imported: {self.image_set.count()}"


class Image(models.Model):
    filename = models.ImageField(upload_to="images")
    size = models.IntegerField(editable=False)
    file_attributes = JSONField(null=True, blank=True)
    regions = JSONField(null=True, blank=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    edit_date = models.DateTimeField('date edited', auto_now=True, null=True, editable=False)

    def __str__(self):
        return f"{self.filename} edited {self.edit_date}"

    @property
    def modified_by(self):
        try:
            user = User.objects.get(id=self.edited_by)
            name = user.get_full_name() or user.get_username()
            date = self.edit_date.strftime("%c")
            return f"Edited by {name} on {date}"
        except User.DoesNotExist:
            return ""

    def save(self, *args, **kwargs):
        self.size = self.filename.size
        super(Image, self).save(*args, **kwargs)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


from django.contrib import admin
from .models import Ticket, Review, UserFollows

# Enregistrement simple
admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(UserFollows)

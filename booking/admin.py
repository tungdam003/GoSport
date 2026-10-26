
from django.contrib import admin
from .models import Sport, Court, TimeSlot, Booking, Contact

admin.site.register(Sport)
admin.site.register(Court)
admin.site.register(TimeSlot)
admin.site.register(Booking)
admin.site.register(Contact)

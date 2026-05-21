from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = 'Create default groups and users'

    def handle(self, *args, **kwargs):
        radmin_group, created = Group.objects.get_or_create(name='RADMIN')
        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('admin123')
            admin.is_staff = True
            admin.save()
            admin.groups.add(radmin_group)
            self.stdout.write(self.style.SUCCESS('Created admin user and assigned to RADMIN group.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))

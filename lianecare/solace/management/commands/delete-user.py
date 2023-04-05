from django.core.management.base import BaseCommand, CommandError
from lianecare.users.models import User

class Command(BaseCommand):
    help = 'Deletes an user and everything associated with it'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        email = options['email']

        self.stdout.write("Processing " + email)

        for user in User.objects.filter(email=email):
            user.delete()
            self.stdout.write("User " + email + " with ID " + str(user.id) + " deleted")


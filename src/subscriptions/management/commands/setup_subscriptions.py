from django.core.management.base import BaseCommand
from subscriptions.models import Subscription, SubscriptionPrice


class Command(BaseCommand):
    help = 'Set up initial subscription plans and pricing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up subscription plans...')
        
        # Create Basic subscription
        basic_sub, created = Subscription.objects.get_or_create(
            name='Basic',
            defaults={
                'subtitle': 'Perfect for small businesses getting started with local SEO',
                'active': True,
                'featured': True,
                'order': 1,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Basic subscription'))
        else:
            self.stdout.write(f'Basic subscription already exists')
        
        # Create Pro subscription
        pro_sub, created = Subscription.objects.get_or_create(
            name='Pro',
            defaults={
                'subtitle': 'Advanced features for growing businesses serious about local SEO',
                'active': True,
                'featured': True,
                'order': 2,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Pro subscription'))
        else:
            self.stdout.write(f'Pro subscription already exists')
        
        # Create Basic Monthly price
        basic_monthly, created = SubscriptionPrice.objects.get_or_create(
            subscription=basic_sub,
            interval=SubscriptionPrice.IntervalChoices.MONTHLY,
            defaults={
                'price': 0.00,
                'featured': True,
                'order': 1,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Basic Monthly price: ${basic_monthly.price}'))
        else:
            self.stdout.write(f'Basic Monthly price already exists')
        
        # Create Basic Yearly price
        basic_yearly, created = SubscriptionPrice.objects.get_or_create(
            subscription=basic_sub,
            interval=SubscriptionPrice.IntervalChoices.YEARLY,
            defaults={
                'price': 0.00,  # ~17% discount for yearly
                'featured': True,
                'order': 2,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Basic Yearly price: ${basic_yearly.price}'))
        else:
            self.stdout.write(f'Basic Yearly price already exists')
        
        # Create Pro Monthly price
        pro_monthly, created = SubscriptionPrice.objects.get_or_create(
            subscription=pro_sub,
            interval=SubscriptionPrice.IntervalChoices.MONTHLY,
            defaults={
                'price': 19.99,
                'featured': True,
                'order': 3,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Pro Monthly price: ${pro_monthly.price}'))
        else:
            self.stdout.write(f'Pro Monthly price already exists')
        
        # Create Pro Yearly price
        pro_yearly, created = SubscriptionPrice.objects.get_or_create(
            subscription=pro_sub,
            interval=SubscriptionPrice.IntervalChoices.YEARLY,
            defaults={
                'price': 199.99,  # ~17% discount for yearly
                'featured': True,
                'order': 4,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Pro Yearly price: ${pro_yearly.price}'))
        else:
            self.stdout.write(f'Pro Yearly price already exists')
        
        self.stdout.write(self.style.SUCCESS('Subscription setup completed successfully!'))
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPrice

class Command(BaseCommand):
    help = 'Update Stripe price IDs with real production price IDs'

    def handle(self, *args, **options):
        self.stdout.write('Updating Stripe price IDs...')
        
        # Replace these with your actual Stripe price IDs from Stripe dashboard
        updates = [
            ('Basic', 'month', 'price_1S0RaiFS3VUz19uos95pPaO1'),
            ('Basic', 'year', 'price_1S0RaiFS3VUz19uoJJoCkvGO'),
            ('Pro', 'month', 'price_1S0RaiFS3VUz19uopn0R0YFG'),
            ('Pro', 'year', 'price_1S0RaiFS3VUz19uoYk60xwFs'),
        ]
        
        for sub_name, interval, stripe_id in updates:
            price = SubscriptionPrice.objects.filter(
                subscription__name=sub_name,
                interval=interval
            ).first()
            
            if price:
                old_id = price.stripe_id
                price.stripe_id = stripe_id
                price.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {sub_name} {interval}: {old_id} -> {stripe_id}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Price not found for {sub_name} {interval}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('All Stripe price IDs updated successfully!'))
        
        # Display current prices for verification
        self.stdout.write('\nCurrent Price IDs:')
        self.stdout.write('=' * 50)
        for price in SubscriptionPrice.objects.all().order_by('subscription__name', 'interval'):
            self.stdout.write(
                f'{price.subscription.name} {price.interval}: {price.stripe_id}'
            )
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import BusinessProfile, SEOAudit, AuditItem, Checklist, ChecklistItem, RankingTracker
from .forms import BusinessProfileForm, ChecklistForm, RankingTrackerForm
import random

@login_required
def dashboard_view(request):
    """Main dashboard showing user's businesses and recent activity"""
    user_businesses = BusinessProfile.objects.filter(user=request.user)
    recent_audits = SEOAudit.objects.filter(business_profile__user=request.user)[:5]
    active_checklists = Checklist.objects.filter(user=request.user, is_completed=False)[:3]
    
    context = {
        'businesses': user_businesses,
        'recent_audits': recent_audits,
        'active_checklists': active_checklists,
    }
    return render(request, 'features/dashboard.html', context)

@login_required
def business_profile_list(request):
    """List all business profiles for the user"""
    businesses = BusinessProfile.objects.filter(user=request.user)
    return render(request, 'features/business_list.html', {'businesses': businesses})

@login_required
def business_profile_create(request):
    """Create a new business profile"""
    if request.method == 'POST':
        form = BusinessProfileForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.user = request.user
            business.save()
            messages.success(request, f'Business profile "{business.business_name}" created successfully!')
            return redirect('business_profile_detail', pk=business.pk)
    else:
        form = BusinessProfileForm()
    
    return render(request, 'features/business_form.html', {'form': form, 'action': 'Create'})

@login_required
def business_profile_detail(request, pk):
    """View business profile details and recent audits"""
    business = get_object_or_404(BusinessProfile, pk=pk, user=request.user)
    recent_audits = business.audits.all()[:5]
    active_rankings = business.rankings.filter(is_tracking=True)[:10]
    
    context = {
        'business': business,
        'recent_audits': recent_audits,
        'active_rankings': active_rankings,
    }
    return render(request, 'features/business_detail.html', context)

@login_required
def business_profile_edit(request, pk):
    """Edit business profile"""
    business = get_object_or_404(BusinessProfile, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BusinessProfileForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, f'Business profile "{business.business_name}" updated successfully!')
            return redirect('business_profile_detail', pk=business.pk)
    else:
        form = BusinessProfileForm(instance=business)
    
    return render(request, 'features/business_form.html', {'form': form, 'action': 'Edit', 'business': business})

@login_required
def run_seo_audit(request, business_pk):
    """Run an SEO audit for a business"""
    business = get_object_or_404(BusinessProfile, pk=business_pk, user=request.user)
    
    # Create a new audit
    audit = SEOAudit.objects.create(business_profile=business)
    
    # Generate audit items based on business category
    audit_items = generate_audit_items(audit, business.category)
    
    # Calculate scores
    audit.overall_score = calculate_overall_score(audit_items)
    audit.google_my_business_score = calculate_category_score(audit_items, 'gmb')
    audit.citation_score = calculate_category_score(audit_items, 'citation')
    audit.review_score = calculate_category_score(audit_items, 'review')
    audit.website_score = calculate_category_score(audit_items, 'website')
    audit.save()
    
    messages.success(request, f'SEO audit completed for {business.business_name}!')
    return redirect('audit_detail', audit_pk=audit.pk)

@login_required
def audit_detail(request, audit_pk):
    """View detailed audit results"""
    audit = get_object_or_404(SEOAudit, pk=audit_pk, business_profile__user=request.user)
    
    # Group items by category
    gmb_items = audit.items.filter(category='gmb')
    citation_items = audit.items.filter(category='citation')
    review_items = audit.items.filter(category='review')
    website_items = audit.items.filter(category='website')
    
    context = {
        'audit': audit,
        'gmb_items': gmb_items,
        'citation_items': citation_items,
        'review_items': review_items,
        'website_items': website_items,
    }
    return render(request, 'features/audit_detail.html', context)

@login_required
def checklist_list(request):
    """List all checklists for the user"""
    checklists = Checklist.objects.filter(user=request.user)
    return render(request, 'features/checklist_list.html', {'checklists': checklists})

@login_required
def checklist_create(request):
    """Create a new checklist"""
    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.user = request.user
            checklist.save()
            
            # Generate default checklist items
            generate_default_checklist_items(checklist)
            
            messages.success(request, f'Checklist "{checklist.title}" created successfully!')
            return redirect('checklist_detail', pk=checklist.pk)
    else:
        form = ChecklistForm()
    
    return render(request, 'features/checklist_form.html', {'form': form, 'action': 'Create'})

@login_required
def checklist_detail(request, pk):
    """View checklist details and items"""
    checklist = get_object_or_404(Checklist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Handle item completion toggles
        for item in checklist.items.all():
            item_id = f'item_{item.id}'
            if item_id in request.POST:
                item.is_completed = not item.is_completed
                if item.is_completed:
                    item.completed_at = timezone.now()
                else:
                    item.completed_at = None
                item.save()
        
        # Check if all items are completed
        all_completed = all(item.is_completed for item in checklist.items.all())
        if all_completed and not checklist.is_completed:
            checklist.is_completed = True
            checklist.completed_at = timezone.now()
            checklist.save()
            messages.success(request, 'Congratulations! Checklist completed!')
        elif not all_completed and checklist.is_completed:
            checklist.is_completed = False
            checklist.completed_at = None
            checklist.save()
        
        return redirect('checklist_detail', pk=checklist.pk)
    
    return render(request, 'features/checklist_detail.html', {'checklist': checklist})

@login_required
def ranking_tracker_list(request):
    """List all ranking trackers"""
    rankings = RankingTracker.objects.filter(business_profile__user=request.user)
    return render(request, 'features/ranking_list.html', {'rankings': rankings})

@login_required
def ranking_tracker_create(request):
    """Create a new ranking tracker"""
    if request.method == 'POST':
        form = RankingTrackerForm(request.POST)
        if form.is_valid():
            ranking = form.save(commit=False)
            ranking.business_profile = form.cleaned_data['business_profile']
            
            # Check if this keyword is already being tracked for this business
            existing = RankingTracker.objects.filter(
                business_profile=ranking.business_profile,
                keyword=ranking.keyword
            ).first()
            
            if existing:
                messages.error(request, f'Keyword "{ranking.keyword}" is already being tracked for this business.')
            else:
                ranking.save()
                messages.success(request, f'Now tracking "{ranking.keyword}" for {ranking.business_profile.business_name}!')
                return redirect('ranking_tracker_list')
    else:
        form = RankingTrackerForm()
        # Filter business profiles to only show user's businesses
        form.fields['business_profile'].queryset = BusinessProfile.objects.filter(user=request.user)
    
    return render(request, 'features/ranking_form.html', {'form': form})

# Helper functions
def generate_audit_items(audit, category):
    """Generate audit items based on business category"""
    items_data = {
        'gmb': [
            ('Business Name Consistency', 'Ensure business name is consistent across all platforms', 'high'),
            ('Complete Business Information', 'Fill out all business details including hours, services, etc.', 'critical'),
            ('Business Category Selection', 'Choose the most relevant business category', 'high'),
            ('Profile Photos', 'Add high-quality photos of your business', 'medium'),
            ('Business Description', 'Write a compelling business description', 'medium'),
        ],
        'citation': [
            ('NAP Consistency', 'Ensure Name, Address, Phone are consistent everywhere', 'critical'),
            ('Major Directory Listings', 'Claim and optimize listings on major directories', 'high'),
            ('Industry-Specific Directories', 'List on directories specific to your industry', 'medium'),
            ('Local Chamber of Commerce', 'Join and list with local business organizations', 'low'),
            ('Social Media Profiles', 'Ensure consistent business information on social media', 'medium'),
        ],
        'review': [
            ('Review Response Rate', 'Respond to all customer reviews promptly', 'high'),
            ('Review Generation Strategy', 'Implement a system to generate more reviews', 'critical'),
            ('Review Monitoring', 'Set up alerts for new reviews', 'medium'),
            ('Review Sentiment Analysis', 'Monitor overall sentiment of reviews', 'medium'),
            ('Review Platform Diversity', 'Encourage reviews on multiple platforms', 'low'),
        ],
        'website': [
            ('Local SEO Keywords', 'Optimize website for local search terms', 'critical'),
            ('Contact Information Visibility', 'Make contact information easily accessible', 'high'),
            ('Local Landing Pages', 'Create location-specific landing pages', 'medium'),
            ('Mobile Optimization', 'Ensure website works well on mobile devices', 'high'),
            ('Local Schema Markup', 'Implement local business schema markup', 'medium'),
        ]
    }
    
    items = []
    for cat, cat_items in items_data.items():
        for item_name, description, priority in cat_items:
            # Randomize status for demo purposes
            status_choices = ['pending', 'completed', 'failed']
            status = random.choice(status_choices)
            
            item = AuditItem.objects.create(
                audit=audit,
                category=cat,
                item_name=item_name,
                description=description,
                status=status,
                priority=priority,
                recommendation=f"Focus on improving {item_name.lower()} to boost your local SEO performance."
            )
            items.append(item)
    
    return items

def calculate_overall_score(items):
    """Calculate overall audit score"""
    if not items:
        return 0
    
    total_score = 0
    for item in items:
        if item.status == 'completed':
            total_score += 100
        elif item.status == 'failed':
            total_score += 0
        else:
            total_score += 50  # Partial credit for pending items
    
    return total_score // len(items)

def calculate_category_score(items, category):
    """Calculate score for a specific category"""
    category_items = [item for item in items if item.category == category]
    return calculate_overall_score(category_items)

def generate_default_checklist_items(checklist):
    """Generate default checklist items based on checklist title"""
    default_items = [
        ('Optimize Google My Business Profile', 'Complete all sections of your GMB profile', 'critical'),
        ('Claim Local Directory Listings', 'Claim and verify listings on major directories', 'high'),
        ('Encourage Customer Reviews', 'Ask satisfied customers to leave reviews', 'high'),
        ('Optimize Website for Local SEO', 'Add local keywords and location information', 'critical'),
        ('Create Local Content', 'Write blog posts about local topics and events', 'medium'),
        ('Monitor and Respond to Reviews', 'Set up alerts and respond to all reviews', 'medium'),
        ('Build Local Citations', 'Get listed on industry-specific directories', 'medium'),
        ('Optimize for Mobile', 'Ensure your website is mobile-friendly', 'high'),
        ('Track Local Rankings', 'Monitor your position for local keywords', 'medium'),
        ('Engage with Local Community', 'Participate in local events and organizations', 'low'),
    ]
    
    for title, description, priority in default_items:
        ChecklistItem.objects.create(
            checklist=checklist,
            title=title,
            description=description,
            priority=priority
        )

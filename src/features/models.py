from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BusinessProfile(models.Model):
    """Model for storing business information for SEO audits"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_profiles')
    business_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} - {self.user.username}"

class SEOAudit(models.Model):
    """Model for storing SEO audit results"""
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='audits')
    audit_date = models.DateTimeField(auto_now_add=True)
    overall_score = models.IntegerField(default=0)
    google_my_business_score = models.IntegerField(default=0)
    citation_score = models.IntegerField(default=0)
    review_score = models.IntegerField(default=0)
    website_score = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-audit_date']
    
    def __str__(self):
        return f"Audit for {self.business_profile.business_name} - {self.audit_date.strftime('%Y-%m-%d')}"

class AuditItem(models.Model):
    """Individual audit items with status and recommendations"""
    audit = models.ForeignKey(SEOAudit, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=50)  # gmb, citation, review, website
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('not_applicable', 'Not Applicable')
    ], default='pending')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    recommendation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['priority', 'item_name']
    
    def __str__(self):
        return f"{self.item_name} - {self.status}"

class Checklist(models.Model):
    """SEO improvement checklists for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class ChecklistItem(models.Model):
    """Individual checklist items"""
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    
    class Meta:
        ordering = ['priority', 'title']
    
    def __str__(self):
        return f"{self.title} - {'Completed' if self.is_completed else 'Pending'}"

class RankingTracker(models.Model):
    """Track keyword rankings for businesses"""
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='rankings')
    keyword = models.CharField(max_length=200)
    current_ranking = models.IntegerField(blank=True, null=True)
    previous_ranking = models.IntegerField(blank=True, null=True)
    tracking_date = models.DateTimeField(auto_now_add=True)
    is_tracking = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-tracking_date']
        unique_together = ['business_profile', 'keyword']
    
    def __str__(self):
        return f"{self.keyword} - {self.business_profile.business_name}"

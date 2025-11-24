from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def with_deleted(self):
        """Include soft-deleted records"""
        return super().get_queryset()
    
    def only_deleted(self):
        """Only soft-deleted records"""
        return super().get_queryset().filter(deleted_at__isnull=False)

class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality"""
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access to all records including deleted
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the record"""
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the record"""
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self):
        """Check if record is soft-deleted"""
        return self.deleted_at is not None
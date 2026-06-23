import os
from django.db import models

class FileCleanupMixin(models.Model):
    """
    Mixin tự động xóa file vật lý khi:
    - Xóa instance
    - Cập nhật field với file mới
    
    Cách dùng: khai báo file_fields = ['image', 'avatar', ...]
    """
    file_fields: list[str]=[]
    
    class Meta:
        abstract = True
        
    def _delete_file(self, path: str) -> None:
        if path and os.path.isfile(path):
            os.remove(path)
            
    def _get_file_path(self, file_name: str) -> str|None:
        field = getattr(self, file_name, None)
        
        if field and hasattr(field, 'path'):
            try:
                return field.path
            except ValueError:
                return None
        return None
    
    def delete(self, *args, **kwargs):
        # Thu thap path truoc khi xoa record
        paths = [self._get_file_path(f) for f in self.file_fields]
        super().delete(*args, **kwargs)
        for path in paths:
            self._delete_file(path)        
        
    def save(self, *args, **kwargs):
        if not self.pk:
            return super().save(*args, **kwargs)
        
        # So sánh file cũ vs mới trước khi save
        try:
            old = self.__class__.objects.get(pk=self.pk)
        except self.__class__.DoesNotExist:
            return super().save(*args, **kwargs)
        
        old_paths={
            f:old._get_file_path(f) for f in self.file_fields
        }
        
        super().save(*args, **kwargs)
        
        for file_name, old_path in old_paths.items():
            new_path = self._get_file_path(file_name)
            if old_path and old_path != new_path:
                self._delete_file(old_path)
class JafrDowError(Exception):
    """الاستثناء الأساسي للمكتبة"""
    pass

class APIError(JafrDowError):
    """خطأ في استدعاء API"""
    pass

class DownloadError(JafrDowError):
    """خطأ في تنزيل الفيديو"""
    pass

class NoVideoLinksError(JafrDowError):
    """لا توجد روابط فيديو متاحة"""
    pass
import requests
import os
import re
import time
from typing import Dict, List, Optional
from .exceptions import APIError, DownloadError, NoVideoLinksError

class JafrDow:
    """
    المكتبة الرئيسية لتنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي
    """
    
    def __init__(self, api_url: str = "https://sii3.top/api/do.php", timeout: int = 30):
        self.api_url = api_url
        self.timeout = timeout
        self.download_folder = "jafrdow_downloads"
        self.session = requests.Session()
        
        # إعداد headers للطلب
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
        })
        
        # إنشاء مجلد التنزيلات
        self._create_download_folder()
    
    def get_video_info(self, social_url: str) -> Dict:
        """
        الحصول على معلومات الفيديو من API
        """
        if not self._validate_url(social_url):
            raise ValueError("❌ الرابط غير صالح أو غير مدعوم")
        
        try:
            response = self.session.get(
                self.api_url, 
                params={"url": social_url}, 
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # التحقق من وجود بيانات الفيديو
            if not data or "links" not in data:
                raise NoVideoLinksError("❌ لا توجد بيانات فيديو متاحة من API")
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"❌ خطأ في استدعاء API: {e}")
    
    def get_video_links(self, social_url: str) -> List[Dict]:
        """
        الحصول على روابط الفيديو المتاحة
        """
        data = self.get_video_info(social_url)
        
        if "links" not in data or not data["links"]:
            raise NoVideoLinksError("❌ لا توجد روابط فيديو متاحة")
        
        return data["links"]
    
    def get_video_title(self, social_url: str) -> str:
        """
        الحصول على عنوان الفيديو
        """
        data = self.get_video_info(social_url)
        return data.get("title", "video")
    
    def get_best_video_link(self, social_url: str, prefer_mp4: bool = True, quality: str = "highest") -> Optional[str]:
        """
        الحصول على أفضل رابط فيديو متاح
        """
        links = self.get_video_links(social_url)
        
        # تصفية الروابط حسب النوع والصيغة
        video_links = [link for link in links if link.get("type") == "video"]
        
        if not video_links:
            return None
        
        # تفضيل صيغة MP4
        if prefer_mp4:
            mp4_links = [link for link in video_links if link.get("ext") == "mp4"]
            if mp4_links:
                video_links = mp4_links
        
        # فرز الروابط حسب الجودة
        sorted_links = self._sort_links_by_quality(video_links, quality)
        
        return sorted_links[0]["url"] if sorted_links else None
    
    def _sort_links_by_quality(self, links: List[Dict], quality: str) -> List[Dict]:
        """
        فرز الروابط حسب الجودة
        """
        def extract_quality(link):
            quality_str = str(link.get("quality", "0"))
            numbers = re.findall(r'\d+', quality_str)
            return int(numbers[0]) if numbers else 0
        
        # نسخة من القائمة الأصلية
        sorted_links = links.copy()
        sorted_links.sort(key=extract_quality, reverse=True)
        
        if quality == "highest":
            return sorted_links
        elif quality == "lowest":
            return sorted_links[::-1]  # عكس القائمة
        else:
            # معالجة الجودة المحددة (مثل "720p")
            try:
                target_quality = int(''.join(filter(str.isdigit, quality)))
                # البحث عن الجودة المطلوبة
                for link in sorted_links:
                    if extract_quality(link) == target_quality:
                        return [link]
                # إذا لم توجد الجودة المطلوبة، نعود لأعلى جودة
                return [sorted_links[0]] if sorted_links else []
            except (ValueError, TypeError):
                return sorted_links
    
    def get_available_qualities(self, social_url: str) -> List[str]:
        """
        الحصول على الجودات المتاحة للفيديو
        """
        links = self.get_video_links(social_url)
        video_links = [link for link in links if link.get("type") == "video"]
        
        qualities = []
        for link in video_links:
            quality = link.get("quality", "")
            if quality and quality not in qualities:
                qualities.append(quality)
        
        # فرز الجودات
        def quality_key(q):
            numbers = re.findall(r'\d+', q)
            return int(numbers[0]) if numbers else 0
        
        return sorted(qualities, key=quality_key, reverse=True)
    
    def download_video(self, social_url: str, output_file: str = None, quality: str = "highest") -> str:
        """
        تنزيل الفيديو من الرابط
        """
        # إنشاء اسم الملف مع ترقيم تلقائي
        if not output_file:
            title = self.get_video_title(social_url)
            output_file = self._generate_unique_filename(title)
        
        # التأكد من أن الملف ينتهي بـ .mp4
        if not output_file.endswith('.mp4'):
            output_file += '.mp4'
        
        # المسار الكامل للملف
        file_path = os.path.join(self.download_folder, output_file)
        
        # الحصول على رابط الفيديو
        video_link = self.get_best_video_link(social_url, quality=quality)
        if not video_link:
            raise NoVideoLinksError("❌ لا توجد روابط فيديو مناسبة")
        
        print(f"📥 جاري تحميل الفيديو...")
        print(f"🔗 المصدر: {self._shorten_url(social_url)}")
        print(f"💾 سيتم الحفظ في: {file_path}")
        
        try:
            # تنزيل الفيديو
            start_time = time.time()
            with self.session.get(video_link, stream=True, timeout=60) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            
                            # تحديث شريط التقدم
                            if total_size > 0:
                                self._update_progress(downloaded, total_size, start_time)
                
                # إظهار رسالة الإكمال
                download_time = time.time() - start_time
                print(f"\n✅ تم التنزيل بنجاح!")
                print(f"📁 الموقع: {file_path}")
                print(f"💿 الحجم: {self._format_size(downloaded)}")
                print(f"⏱️  الوقت: {self._format_time(download_time)}")
                if download_time > 0:
                    print(f"🚀 السرعة: {self._format_size(downloaded / download_time)}/s")
                
                return file_path
                
        except requests.exceptions.RequestException as e:
            # حذف الملف إذا فشل التنزيل
            if os.path.exists(file_path):
                os.remove(file_path)
            raise DownloadError(f"❌ خطأ في تنزيل الفيديو: {e}")
    
    def _update_progress(self, downloaded: int, total: int, start_time: float):
        """تحديث شريط التقدم بشكل صحيح"""
        percent = (downloaded / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * downloaded // total) if total > 0 else 0
        bar = '█' * filled_length + '▒' * (bar_length - filled_length)
        
        # حساب السرعة والوقت المتبقي
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = downloaded / elapsed_time
            if downloaded < total and speed > 0:
                remaining_time = (total - downloaded) / speed
                time_str = f"⏳ {self._format_time(remaining_time)}"
            else:
                time_str = "⏳ مكتمل"
        else:
            speed = 0
            time_str = "⏳ حساب..."
        
        progress_str = f"\r📊 |{bar}| {percent:.1f}% - {self._format_size(downloaded)}/{self._format_size(total)} - 🚀 {self._format_size(speed)}/s - {time_str}"
        print(progress_str, end='', flush=True)
    
    def _format_time(self, seconds: float) -> str:
        """تنسيق الوقت"""
        if seconds < 60:
            return f"{int(seconds)} ثانية"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} دقيقة {secs} ثانية"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} ساعة {minutes} دقيقة"
    
    def _format_size(self, size_bytes: float) -> str:
        """تنسيق حجم الملف"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _shorten_url(self, url: str) -> str:
        """تقصير الرابط لعرضه بشكل أنيق"""
        if len(url) > 50:
            return url[:47] + "..."
        return url
    
    def _validate_url(self, url: str) -> bool:
        """التحقق من صحة الرابط"""
        patterns = [
            r'https?://(www\.)?(youtube|youtu)\.(com|be)',
            r'https?://(www\.)?tiktok\.com',
            r'https?://(www\.)?instagram\.com',
            r'https?://(www\.)?twitter\.com',
            r'https?://(www\.)?facebook\.com',
            r'https?://(www\.)?x\.com',
            r'https?://vm\.tiktok\.com',
            r'https?://vt\.tiktok\.com'
        ]
        
        return any(re.match(pattern, url) for pattern in patterns)
    
    def _create_download_folder(self):
        """إنشاء مجلد التنزيلات"""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def _generate_unique_filename(self, title: str) -> str:
        """إنشاء اسم فريد للملف مع ترقيم تلقائي"""
        # تنظيف العنوان من الأحرف غير المسموحة
        safe_title = re.sub(r'[<>:"/\\|?*#]', '', title)
        safe_title = re.sub(r'[^\w\s\-_\.]', '', safe_title)  # إزالة الإيموجي والرموز
        safe_title = safe_title.strip()
        
        if not safe_title or safe_title == "video":
            safe_title = "فيديو"
        
        # إذا كان العنوان طويلاً جداً، نقصره
        if len(safe_title) > 40:
            safe_title = safe_title[:40]
        
        base_name = safe_title
        counter = 1
        filename = f"{base_name}.mp4"
        file_path = os.path.join(self.download_folder, filename)
        
        # البحث عن اسم فريد
        while os.path.exists(file_path):
            filename = f"{base_name}_{counter}.mp4"
            file_path = os.path.join(self.download_folder, filename)
            counter += 1
        
        return filename
    
    def quick_download(self, social_url: str, custom_name: str = None, quality: str = "highest") -> bool:
        """
        تنزيل سريع بدون إعدادات معقدة
        """
        try:
            self.download_video(social_url, custom_name, quality=quality)
            return True
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def show_available_qualities(self, social_url: str):
        """
        عرض الجودات المتاحة للفيديو
        """
        try:
            qualities = self.get_available_qualities(social_url)
            title = self.get_video_title(social_url)
            
            print(f"🎬 الفيديو: {title}")
            print("📈 الجودات المتاحة:")
            for i, quality in enumerate(qualities, 1):
                print(f"   {i}. {quality}")
            
            return qualities
        except Exception as e:
            print(f"❌ خطأ في الحصول على الجودات: {e}")
            return []
    
    def get_download_folder(self) -> str:
        """
        الحصول على مسار مجلد التنزيلات
        """
        return os.path.abspath(self.download_folder)
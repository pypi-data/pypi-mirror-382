#!/usr/bin/env python3
"""
واجهة سطر الأوامر لمكتبة jafrdow
"""

import argparse
import sys
import os

# إصلاح مشكلة الاستيراد عند التشغيل المباشر
try:
    from .core import JafrDow
except ImportError:
    # إذا فشل الاستيراد النسبي، نجرب الاستيراد المطلق
    try:
        from jafrdow.core import JafrDow
    except ImportError:
        # كحل أخير، نضيف المسار إلى sys.path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from jafrdow.core import JafrDow

def main():
    parser = argparse.ArgumentParser(
        description='jafrdow - أداة تنزيل مقاطع الفيديو من وسائل التواصل الاجتماعي',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  jafrdow "https://tiktok.com/..."                    # تنزيل بأعلى جودة
  jafrdow "https://youtube.com/..." -q 720p          # تنزيل بجودة 720p
  jafrdow "https://instagram.com/..." -o فيديو_خاص.mp4 # تنزيل باسم مخصص
  jafrdow "https://twitter.com/..." --qualities      # عرض الجودات المتاحة
        """
    )
    
    parser.add_argument('url', nargs='?', help='رابط الفيديو من السوشيال ميديا')
    parser.add_argument('-o', '--output', help='اسم ملف الإخراج', default=None)
    parser.add_argument('-q', '--quality', help='جودة الفيديو (highest, lowest, 1080p, 720p, etc.)', default='highest')
    parser.add_argument('--qualities', '--show-qualities', help='عرض الجودات المتاحة فقط', action='store_true')
    parser.add_argument('--folder', help='عرض موقع مجلد التنزيلات', action='store_true')
    
    args = parser.parse_args()
    
    downloader = JafrDow()
    
    try:
        if args.folder:
            # عرض موقع المجلد
            folder_path = downloader.get_download_folder()
            print(f"📁 مجلد التنزيلات: {folder_path}")
            return
        
        if not args.url:
            parser.print_help()
            return
        
        if args.qualities:
            downloader.show_available_qualities(args.url)
            return
        
        # تنزيل الفيديو
        file_path = downloader.download_video(
            args.url, 
            args.output, 
            quality=args.quality
        )
        
        print(f"✅ تم التنزيل بنجاح: {file_path}")
        
    except Exception as e:
        print(f"❌ فشل التنزيل: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
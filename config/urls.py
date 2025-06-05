# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dairy Farm Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #27ae60; text-align: center; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { display: block; padding: 10px 15px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; transition: background-color 0.3s; }
            a:hover { background-color: #2980b9; }
            p { text-align: center; color: #7f8c8d; margin-top: 30px; }
            .status { background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐄 Dairy Farm Management System 🥛</h1>
            <div class="status">✅ API is running successfully!</div>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/admin/">📊 Admin Panel</a></li>
                <li><a href="/api/farms/">🏘️ Farms API</a></li>
                <li><a href="/api/livestock/">🐄 Livestock API</a></li>
                <li><a href="/api/production/">🥛 Production API</a></li>
                <li><a href="/api/feeds/">🌾 Feeds API</a></li>
                <li><a href="/api/health/">🏥 Health API</a></li>
                <li><a href="/api/breeding/">💕 Breeding API</a></li>
                <li><a href="/api/financial/">💰 Financial API</a></li>
                <li><a href="/api/analytics/">📈 Analytics API</a></li>
                <li><a href="/api/notifications/">🔔 Notifications API</a></li>
            </ul>
            
            <p><strong>Your Django backend is ready for the React frontend!</strong></p>
            <p>Next steps: Create superuser → Test admin panel → Add sample data</p>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('', home_view, name='home'),  # Landing page
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/farms/', include('apps.farms.urls')),
    path('api/livestock/', include('apps.livestock.urls')),
    path('api/production/', include('apps.production.urls')),
    path('api/feeds/', include('apps.feeds.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/breeding/', include('apps.breeding.urls')),
    path('api/financial/', include('apps.financial.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Dairy Farm Management System"
admin.site.site_title = "Dairy Farm Admin"
admin.site.index_title = "Welcome to Dairy Farm Management"
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('upload-folder/', views.upload_folder, name='upload_folder'),
    path('create-folder/', views.create_folder, name='create_folder'),

    path('folder/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),

    path('file/<int:file_id>/open/', views.open_file, name='open_file'),

    path('rename-file/<int:file_id>/', views.rename_file, name='rename_file'),
    path('rename-folder/<int:folder_id>/', views.rename_folder, name='rename_folder'),
    
    path('my-drive/', views.my_drive, name='my_drive'),

    path('recent/', views.recent_files_and_folders, name='recent_files_and_folders'),

    path('trash/', views.trash, name='trash'),
    path('folder/<int:id>/move_to_trash/', views.move_folder_to_trash, name='move_to_trash_folder'),
    path('file/<int:id>/move_to_trash/', views.move_file_to_trash, name='move_to_trash_file'),
    path('folder/<int:id>/restore/', views.restore_folder, name='restore_folder'),
    path('file/<int:id>/restore/', views.restore_file, name='restore_file'),
    path('folder/<int:id>/delete/', views.permanently_delete_folder, name='delete_folder'),
    path('file/<int:id>/delete/', views.permanently_delete_file, name='delete_file'),

    path('file/download/<int:file_id>/', views.download_file, name='download_file'),
    
    path('share/file/<int:file_id>/', views.share_file, name='share_file'),
    path('share/folder/<int:folder_id>/', views.share_folder, name='share_folder'),

    path('search/', views.search_results, name='search_results'),
]


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import File, Folder, Trash
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.db.models import Q
from django.conf import settings

# Signup
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth import authenticate, login as auth_login



@login_required
def home(request):
    # Handle POST requests for file upload or folder creation
    if request.method == 'POST':
        if 'file' in request.FILES:
            # Handle file upload
            file = request.FILES['file']
            new_file = File(name=file.name, file=file, owner=request.user, is_trashed=False)
            new_file.save()
        elif 'folder_name' in request.POST:
            # Handle folder creation
            folder_name = request.POST['folder_name']
            new_folder = Folder(name=folder_name, owner=request.user, is_trashed=False)
            new_folder.save()
        return redirect('home')

    # Fetch the user's Google avatar URL if authenticated
    avatar_url = None
    if request.user.is_authenticated:
        social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if social_account:
            avatar_url = social_account.get_avatar_url()

    # Prepare context for rendering the home page
    context = {
        'files': File.objects.filter(owner=request.user, is_trashed=False),
        'folders': Folder.objects.filter(owner=request.user, is_trashed=False),
        'avatar_url': avatar_url,
    }
    
    return render(request, 'drive/home.html', context)


@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        new_file = File(name=file.name, file=file, owner=request.user)
        new_file.save()
        return redirect('home')
    
def upload_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        files = request.FILES.getlist('files')
        folder = Folder.objects.create(name=folder_name, owner=request.user)
        for file in files:
            File.objects.create(name=file.name, owner=request.user, folder=folder, file=file)
        return redirect('home')  # Redirect to the home page or folder detail page
    return render(request, 'upload_folder.html')

@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST['folder_name']
        new_folder = Folder(name=folder_name, owner=request.user)
        new_folder.save()
        return redirect('home')

@login_required
def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    files = folder.files.all()
    return render(request, 'drive/folder_detail.html', {'folder': folder, 'files': files})

@login_required
def file_detail(request, file_id):
    file = get_object_or_404(File, id=file_id)
    context = {
        'file': file
    }
    return render(request, 'drive/file_detail.html', context)

@login_required
def open_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.file:
        # Redirect to the file URL if it exists
        return redirect(file.file.url)
    else:
        # Handle the case where the file doesn't exist
        return HttpResponseNotFound("File not found.")


@login_required
def rename_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if request.method == 'POST':
        new_name = request.POST.get('file_name')
        file.name = new_name
        file.save()
        messages.success(request, 'File renamed successfully')
        return redirect('home')
    return render(request, 'drive/rename_file.html', {'file': file})

@login_required
def rename_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        new_name = request.POST.get('folder_name')
        folder.name = new_name
        folder.save()
        messages.success(request, 'Folder renamed successfully')
        return redirect('home')
    return render(request, 'drive/rename_folder.html', {'folder': folder})

@login_required
def my_drive(request):
    # Retrieve files and folders for My Drive page
    context = {
        'files': File.objects.filter(owner=request.user).all(),
        'folders': Folder.objects.filter(owner=request.user).all(),
    }
    return render(request, 'drive/my_drive.html', context)

@login_required
def recent_files_and_folders(request):
    files = File.objects.order_by('-uploaded_at')[:5]  # Get the 10 most recent files
    folders = Folder.objects.order_by('-created_at')[:5]  # Get the 10 most recent folders
    return render(request, 'drive/recent.html', {'files': files, 'folders': folders})

@login_required
def trash(request):
    trash_items = Trash.objects.filter(user=request.user)
    return render(request, 'drive/trash.html', {'trash_items': trash_items})

@login_required
def move_folder_to_trash(request, id):
    folder = get_object_or_404(Folder, id=id)
    Trash.objects.create(
        user=request.user,  # Assign the current user
        object_id=folder.id,
        object_type='folder',
        name=folder.name
    )
    folder.delete()  # Or set a 'deleted' status if not actually deleting
    return redirect('home')

@login_required
def move_file_to_trash(request, id):
    file = get_object_or_404(File, id=id)
    Trash.objects.create(
        user=request.user,  # Assign the current user
        object_id=file.id,
        object_type='file',
        name=file.name
    )
    file.delete()  # Or set a 'deleted' status if not actually deleting
    return redirect('home')

@login_required
def restore_folder(request, id):
    trash_item = get_object_or_404(Trash, id=id, user=request.user)
    if trash_item.object_type == 'folder':
        Folder.objects.create(
            id=trash_item.object_id,
            name=trash_item.name,
            owner=request.user  # Set the owner to the current user
        )
    trash_item.delete()
    return redirect('home')

@login_required
def restore_file(request, id):
    trash_item = get_object_or_404(Trash, id=id,  user=request.user)
    if trash_item.object_type == 'file':
        File.objects.create(
            id=trash_item.object_id,
            name=trash_item.name,
            owner=request.user 
        )
    trash_item.delete()
    return redirect('home')

@login_required
def permanently_delete_folder(request, id):
    folder = get_object_or_404(Trash, id=id)
    folder.delete()  # Permanently delete from trash
    return redirect('trash')

@login_required
def permanently_delete_file(request, id):
    file = get_object_or_404(Trash, id=id)
    file.delete()  # Permanently delete from trash

def download_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    # Logic for file download (e.g., using FileResponse or HttpResponse)
    pass

@login_required
def share_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if request.method == "POST":
        recipient_email = request.POST.get('email')
        subject = f"Shared File: {file.name}"
        message = f"A file has been shared with you.\n\nFile Name: {file.name}\n"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
        return redirect('home')
    return render(request, 'drive/share_file.html', {'file': file})

@login_required
def share_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == "POST":
        recipient_email = request.POST.get('email')
        subject = f"Shared Folder: {folder.name}"
        message = f"A folder has been shared with you.\n\nFolder Name: {folder.name}\n"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
        return redirect('home')
    return render(request, 'drive/share_folder.html', {'folder': folder})

def search_results(request):
    query = request.GET.get('q')
    user = request.user

    if query:
        search_results = File.objects.filter(
            Q(name__icontains=query) & Q(owner=user)
        ).distinct()
    else:
        search_results = File.objects.none()

    return render(request, 'drive/search_results.html', {'search_results': search_results})







def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)  # Ensure this call is correct
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Username and password are required.")

        return redirect('login')
    else:
        return render(request, 'account/login.html')

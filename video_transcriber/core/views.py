from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import UploadForm
from .models import Upload, Output
from .tasks import process_media_from_url, extract_audio_from_file, extract_audio_from_url


@login_required
def upload_view(request):
    form = UploadForm()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()

            output_types = form.cleaned_data.get('output_types', [])
            for output_type in output_types:
                Output.objects.create(
                    upload=upload,
                    output_type=output_type
                )
            
            if upload.file_url:
                chain = (
                    process_media_from_url.si(upload.id) |
                    extract_audio_from_url.si(upload.id)
                ).apply_async()
                # process_media_from_url.apply_async(args=(upload.id,))
                # extract_audio_from_url.apply_async(args=(upload.id,))
            if upload.file:
                extract_audio_from_file.apply_async(args=(upload.id,))
                
            return redirect(to='upload')
    return render(request, template_name='core/upload.html', context={'form': form})


@login_required
def dashboard_view(request):
    uploads = Upload.objects.filter(user=request.user).order_by('-created_at')
    return render(request, template_name='core/dashboard.html', context={'uploads': uploads})
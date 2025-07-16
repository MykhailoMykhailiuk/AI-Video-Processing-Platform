from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .forms import SignupForm


class SignupView(View):
    template_name = 'accounts/signup.html'
    form_class = SignupForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, f"Account created for {username}")
            return redirect(to='accounts:login')
        return render(request, self.template_name, {'form': form})




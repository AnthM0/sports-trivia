from urllib import request

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib import messages
from myapp.models import TriviaCategory

def home(request):
    return render(request, 'myapp/home.html')

def pinpoint_challenge(request):
    sport = request.GET.get('sport', '')
    categories = TriviaCategory.objects.filter(sport=sport) if sport else TriviaCategory.objects.none()
    return render(request, 'myapp/pinpoint_challenge.html', {
        'categories': categories,
        'selected_sport': sport,
        'sport_choices': TriviaCategory.SPORT_CHOICES,
    })

def add_trivia_category(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        sport = request.POST.get('sport', '').strip()
        stat_code = request.POST.get('stat_code', '').strip()
        verified = request.POST.get('verified') == 'true'
        recommended_pinpoint = request.POST.get('recommended_pinpoint') or 100
        total_players = request.POST.get('total_players') or 200

        if not title or not sport or not stat_code:
            return JsonResponse({'success': False, 'error': 'Name, sport, and stat code are required.'})

        if TriviaCategory.objects.filter(stat_code=stat_code).exists():
            return JsonResponse({'success': False, 'error': 'A trivia set with that stat code already exists.'})

        TriviaCategory.objects.create(
            title=title,
            description=description,
            sport=sport,
            stat_code=stat_code,
            verified=verified,
            recommended_pinpoint=recommended_pinpoint,
            total_players=total_players,
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
        else:
            username = email  # use email as username
            user = User.objects.create_user(username=username, email=email, password=password)
            name_parts = name.strip().split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
            login(request, user)
            return redirect('home')
    return redirect('home')

def logout_view(request):
    logout(request)
    return redirect('home')
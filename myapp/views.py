from urllib import request
import csv
import io
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from myapp.models import Player, TriviaCategory


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

def categories_and_players(request):
    categories = TriviaCategory.objects.all().order_by('sport', 'title')
    selected_category_id = request.GET.get('category', '')

    if selected_category_id == 'all':
        players = Player.objects.all().order_by('name')
        selected_category = None
    elif selected_category_id:
        try:
            selected_category = TriviaCategory.objects.get(id=selected_category_id)
            players = selected_category.players.all()
            # Sort by the stat value for this category
            players = sorted(players, key=lambda p: p.stats.get(selected_category.stat_code, 0), reverse=True)
        except TriviaCategory.DoesNotExist:
            selected_category = None
            players = []
    else:
        selected_category = None
        players = []

    return render(request, 'myapp/categories_and_players.html', {
        'categories': categories,
        'players': players,
        'selected_category': selected_category,
        'selected_category_id': selected_category_id,
    })

def add_trivia_category(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    sport = request.POST.get('sport', '').strip()
    stat_code = request.POST.get('stat_code', '').strip()
    verified = request.POST.get('verified') == 'true'
    merge = request.POST.get('merge') == 'true'
    recommended_pinpoint = request.POST.get('recommended_pinpoint') or None
    total_players = request.POST.get('total_players') or None
    csv_file = request.FILES.get('csv_file')

    if not title or not sport or not stat_code:
        return JsonResponse({'success': False, 'error': 'Name, sport, and stat code are required.'})

    if TriviaCategory.objects.filter(stat_code=stat_code).exists():
        return JsonResponse({'success': False, 'error': 'A trivia set with that stat code already exists.'})

    category = TriviaCategory.objects.create(
        title=title,
        description=description,
        sport=sport,
        stat_code=stat_code,
        verified=verified,
        recommended_pinpoint=int(recommended_pinpoint) if recommended_pinpoint else None,
        total_players=int(total_players) if total_players else None,
    )

    if csv_file:
        try:
            decoded = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))

            raw_rows = list(reader)
            if not raw_rows:
                return JsonResponse({'success': True, 'warning': 'CSV file was empty.'})

            # Normalise headers — strip whitespace and lowercase
            rows = []
            for row in raw_rows:
                normalised = {k.strip().lower(): v.strip() for k, v in row.items()}
                rows.append(normalised)

            # Detect columns
            first_row_keys = list(rows[0].keys())
            name_col = None
            stat_col = None

            for key in first_row_keys:
                if key in ('name', 'player name', 'player'):
                    name_col = key
                elif key == 'stat' or key == stat_code.lower():
                    stat_col = key

            if not name_col or not stat_col:
                return JsonResponse({
                    'success': True,
                    'warning': f'CSV columns not recognised. Found: {first_row_keys}. Expected a name column and a stat column.'
                })

            linked_players = []
            errors = []

            for row in rows:
                name = row.get(name_col, '').strip()
                stat_value = row.get(stat_col, '').strip()

                if not name or not stat_value:
                    errors.append(f"Skipped row — missing name or stat: {row}")
                    continue

                try:
                    stat_value = int(stat_value)
                except ValueError:
                    try:
                        stat_value = float(stat_value)
                    except ValueError:
                        pass

                if merge:
                    player = Player.objects.filter(
                        name__iexact=name,
                        sport=sport
                    ).first()
                    if player:
                        player.stats[stat_code] = stat_value
                        player.save()
                    else:
                        player = Player.objects.create(
                            name=name,
                            sport=sport,
                            stats={stat_code: stat_value}
                        )
                else:
                    player = Player.objects.create(
                        name=name,
                        sport=sport,
                        stats={stat_code: stat_value}
                    )

                linked_players.append(player)

            category.players.set(linked_players)

            response_data = {
                'success': True,
                'players_processed': len(linked_players),
            }
            if errors:
                response_data['warnings'] = errors

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'success': True,
                'warning': f'Category saved but CSV processing failed: {str(e)}'
            })

    return JsonResponse({'success': True})

def edit_trivia_category(request, category_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    try:
        category = TriviaCategory.objects.get(id=category_id)
    except TriviaCategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})

    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    sport = request.POST.get('sport', '').strip()
    stat_code = request.POST.get('stat_code', '').strip()
    verified = request.POST.get('verified') == 'true'
    recommended_pinpoint = request.POST.get('recommended_pinpoint') or None
    total_players = request.POST.get('total_players') or None

    if not title or not sport or not stat_code:
        return JsonResponse({'success': False, 'error': 'Name, sport, and stat code are required.'})

    # If stat_code changed, migrate stats on linked players
    if stat_code != category.stat_code:
        for player in category.players.all():
            if category.stat_code in player.stats:
                player.stats[stat_code] = player.stats.pop(category.stat_code)
                player.save()

    category.title = title
    category.description = description
    category.sport = sport
    category.stat_code = stat_code
    category.verified = verified
    category.recommended_pinpoint = int(recommended_pinpoint) if recommended_pinpoint else None
    category.total_players = int(total_players) if total_players else None
    category.save()

    return JsonResponse({'success': True})


def delete_trivia_category(request, category_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    try:
        category = TriviaCategory.objects.get(id=category_id)
    except TriviaCategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})

    stat_code = category.stat_code

    for player in category.players.all():
        if stat_code in player.stats:
            del player.stats[stat_code]
            if not player.stats:
                player.delete()
            else:
                player.save()

    category.delete()
    return JsonResponse({'success': True})

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
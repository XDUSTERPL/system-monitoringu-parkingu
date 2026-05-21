from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import ParkingOccupation, ParkingSpot
from .streaming import gen_frames


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """Prosty endpoint do testowania autentykacji."""
    if not request.user.groups.filter(name='RADMIN').exists():
        return Response("Brak dostępu.", status=status.HTTP_403_FORBIDDEN)
    return Response({"message": "OK"}, status=status.HTTP_200_OK)

#  ENDPOINT STREAMUJĄCY WIDEO
def video_feed(request):
    """
    Widok, który zwraca strumień MJPEG.
    Frontend wyświetla to w czasie rzeczywistym.
    """
    return StreamingHttpResponse(
        gen_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_parking_stats(request):
    """
    Endpoint zwracający statystyki zajmowania miejsc parkingowych.
    
    Parametry GET:
    - mode: 'day' (konkretny dzień) | 'best_month' (najlepszy dzień w miesiącu) | 'best_quarter' (najlepszy dzień w kwartale)
    - date: data w formacie YYYY-MM-DD (wymagane dla mode='day')
    - month: miesiąc w formacie YYYY-MM (wymagane dla mode='best_month')
    - quarter: kwartał w formacie YYYY-Q (np. '2025-1' dla Q1 2025, wymagane dla mode='best_quarter')
    
    Zwraca:
    - Listę miejsc z liczbą zajęć w wybranym okresie
    - Sumę wszystkich zajęć
    - Informacje o zakresie dat
    """
    if not request.user.groups.filter(name='RADMIN').exists():
        return Response("Brak dostępu.", status=status.HTTP_403_FORBIDDEN)
    
    mode = request.GET.get('mode', 'day')
    
    try:
        if mode == 'day':
            # Konkretny dzień
            date_str = request.GET.get('date')
            if not date_str:
                return Response("Brak parametru 'date'", status=status.HTTP_400_BAD_REQUEST)
            
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_datetime = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))
            
            stats = get_daily_stats(start_datetime, end_datetime)
            stats['period'] = f"Dzień: {target_date.strftime('%Y-%m-%d')}"
            
        elif mode == 'month':
            # Miesiąc
            month_str = request.GET.get('month')
            if not month_str:
                return Response("Brak parametru 'month'", status=status.HTTP_400_BAD_REQUEST)
            
            year, month = map(int, month_str.split('-'))
            stats = get_month_stats(year, month)
            stats['period'] = f"Miesiąc: {year}-{month:02d}"
            
        elif mode == 'quarter':
            # Kwartał
            quarter_str = request.GET.get('quarter')
            if not quarter_str:
                return Response("Brak parametru 'quarter'", status=status.HTTP_400_BAD_REQUEST)
            
            year, quarter = map(int, quarter_str.split('-'))
            stats = get_quarter_stats(year, quarter)
            stats['period'] = f"Kwartał: Q{quarter} {year}"
        
        elif mode == 'year':
            # Rok
            year_str = request.GET.get('year')
            if not year_str:
                return Response("Brak parametru 'year'", status=status.HTTP_400_BAD_REQUEST)
            
            year = int(year_str)
            stats = get_year_stats(year)
            stats['period'] = f"Rok: {year}"
        
        elif mode == 'best_day_month':
            # Najlepszy dzień w miesiącu
            month_str = request.GET.get('month')
            if not month_str:
                return Response("Brak parametru 'month'", status=status.HTTP_400_BAD_REQUEST)
            
            year, month = map(int, month_str.split('-'))
            stats = get_best_day_in_month(year, month)
            
        elif mode == 'best_day_quarter':
            # Najlepszy dzień w kwartale
            quarter_str = request.GET.get('quarter')
            if not quarter_str:
                return Response("Brak parametru 'quarter'", status=status.HTTP_400_BAD_REQUEST)
            
            year, quarter = map(int, quarter_str.split('-'))
            stats = get_best_day_in_quarter(year, quarter)
            
        elif mode == 'best_day_year':
            # Najlepszy dzień w roku
            year_str = request.GET.get('year')
            if not year_str:
                return Response("Brak parametru 'year'", status=status.HTTP_400_BAD_REQUEST)
            
            year = int(year_str)
            stats = get_best_day_in_year(year)
            
        elif mode == 'best_month_year':
            # Najlepszy miesiąc w roku
            year_str = request.GET.get('year')
            if not year_str:
                return Response("Brak parametru 'year'", status=status.HTTP_400_BAD_REQUEST)
            
            year = int(year_str)
            stats = get_best_month_in_year(year)
            
        elif mode == 'best_quarter_year':
            # Najlepszy kwartał w roku
            year_str = request.GET.get('year')
            if not year_str:
                return Response("Brak parametru 'year'", status=status.HTTP_400_BAD_REQUEST)
            
            year = int(year_str)
            stats = get_best_quarter_in_year(year)
            
        elif mode == 'best_day':
            # Najlepszy dzień (wszystkie dane)
            stats = get_best_day_overall()
            
        elif mode == 'best_month':
            # Najlepszy miesiąc (wszystkie dane)
            stats = get_best_month_overall()
            
        elif mode == 'best_quarter':
            # Najlepszy kwartał (wszystkie dane)
            stats = get_best_quarter_overall()
            
        elif mode == 'best_year':
            # Najlepszy rok (wszystkie dane)
            stats = get_best_year_overall()
        
        else:
            return Response("Nieprawidłowy parametr 'mode'", status=status.HTTP_400_BAD_REQUEST)
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(f"Błąd formatowania daty: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(f"Błąd serwera: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_daily_stats(start_datetime, end_datetime):
    """
    Zwraca statystyki zajęć dla podanego zakresu czasowego.
    """
    # Pobieranie wszystkich zajęć w danym dniu
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_datetime,
        occupied_at__lte=end_datetime
    )
    
    # Grupowanie po miejscach parkingowych i zliczanie zajęć
    spot_stats = occupations.values('parking_spot__spot_number').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Przygotowanie wyniku
    spots = []
    total_occupations = 0
    
    for stat in spot_stats:
        spots.append({
            'spot_number': stat['parking_spot__spot_number'],
            'occupations': stat['count']
        })
        total_occupations += stat['count']
    
    return {
        'spots': spots,
        'total_occupations': total_occupations,
        'start_date': start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'end_date': end_datetime.strftime('%Y-%m-%d %H:%M:%S')
    }


def get_best_day_in_month(year, month):
    """
    Znajduje dzień z największą liczbą zajęć w danym miesiącu.
    """
    # Początek i koniec miesiąca
    start_of_month = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    else:
        end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(seconds=1)
    
    
    # Pobieranie wszystkich zajęć w miesiącu
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_of_month,
        occupied_at__lte=end_of_month
    )
    
    
    # Grupowanie po dniach i zliczanie
    daily_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        day = local_time.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    
    if not daily_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': f"Miesiąc {year}-{month:02d} (brak danych)",
            'best_day': None
        }
    
    # Szukanie dnia z największą liczbą zajęć
    best_day = max(daily_counts, key=daily_counts.get)
    
    
    # Pobieranie szczegółowych statystyk dla tego dnia
    start_datetime = timezone.make_aware(datetime.combine(best_day, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(best_day, datetime.max.time()))
    
    
    stats = get_daily_stats(start_datetime, end_datetime)
    stats['period'] = f"Najlepszy dzień w miesiącu {year}-{month:02d}"
    stats['best_day'] = best_day.strftime('%Y-%m-%d')
    
    return stats


def get_best_day_in_quarter(year, quarter):
    """
    Znajduje dzień z największą liczbą zajęć w danym kwartale.
    """
    # Ustalanie początku i końca kwartału
    quarter_start_months = {1: 1, 2: 4, 3: 7, 4: 10}
    start_month = quarter_start_months.get(quarter)
    
    if not start_month:
        raise ValueError("Kwartał musi być w zakresie 1-4")
    
    start_of_quarter = timezone.make_aware(datetime(year, start_month, 1))
    
    if quarter == 4:
        end_of_quarter = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    else:
        end_of_quarter = timezone.make_aware(datetime(year, start_month + 3, 1)) - timedelta(seconds=1)
    
    # Pobieranie wszystkich zajęć w kwartale
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_of_quarter,
        occupied_at__lte=end_of_quarter
    )
    
    # Grupowanie po dniach i zliczanie
    daily_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        day = local_time.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    if not daily_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': f"Kwartał Q{quarter} {year} (brak danych)",
            'best_day': None
        }
    
    # Szukanie dnia z największą liczbą zajęć
    best_day = max(daily_counts, key=daily_counts.get)
    
    # Pobieranie szczegółowych statystyk dla tego dnia
    start_datetime = timezone.make_aware(datetime.combine(best_day, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(best_day, datetime.max.time()))
    
    stats = get_daily_stats(start_datetime, end_datetime)
    stats['period'] = f"Najlepszy dzień w kwartale Q{quarter} {year}"
    stats['best_day'] = best_day.strftime('%Y-%m-%d')
    
    return stats


def get_month_stats(year, month):
    """
    Zwraca statystyki dla całego miesiąca.
    """
    start_of_month = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    else:
        end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(seconds=1)
    
    stats = get_daily_stats(start_of_month, end_of_month)
    stats['period'] = f"Miesiąc {year}-{month:02d}"
    return stats


def get_quarter_stats(year, quarter):
    """
    Zwraca statystyki dla całego kwartału.
    """
    quarter_start_months = {1: 1, 2: 4, 3: 7, 4: 10}
    start_month = quarter_start_months.get(quarter)
    
    if not start_month:
        raise ValueError("Kwartał musi być w zakresie 1-4")
    
    start_of_quarter = timezone.make_aware(datetime(year, start_month, 1))
    
    if quarter == 4:
        end_of_quarter = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    else:
        end_of_quarter = timezone.make_aware(datetime(year, start_month + 3, 1)) - timedelta(seconds=1)
    
    stats = get_daily_stats(start_of_quarter, end_of_quarter)
    stats['period'] = f"Kwartał Q{quarter} {year}"
    return stats


def get_year_stats(year):
    """
    Zwraca statystyki dla całego roku.
    """
    start_of_year = timezone.make_aware(datetime(year, 1, 1))
    end_of_year = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    
    stats = get_daily_stats(start_of_year, end_of_year)
    stats['period'] = f"Rok {year}"
    return stats


def get_best_day_in_year(year):
    """
    Znajduje dzień z największą liczbą zajęć w danym roku.
    """
    start_of_year = timezone.make_aware(datetime(year, 1, 1))
    end_of_year = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_of_year,
        occupied_at__lte=end_of_year
    )
    
    daily_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        day = local_time.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    if not daily_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': f"Rok {year} (brak danych)",
            'best_day': None
        }
    
    best_day = max(daily_counts, key=daily_counts.get)
    
    start_datetime = timezone.make_aware(datetime.combine(best_day, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(best_day, datetime.max.time()))
    
    stats = get_daily_stats(start_datetime, end_datetime)
    stats['period'] = f"Najlepszy dzień w roku {year}"
    stats['best_day'] = best_day.strftime('%Y-%m-%d')
    
    return stats


def get_best_month_in_year(year):
    """
    Znajduje miesiąc z największą liczbą zajęć w danym roku.
    """
    start_of_year = timezone.make_aware(datetime(year, 1, 1))
    end_of_year = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_of_year,
        occupied_at__lte=end_of_year
    )
    
    monthly_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        month = local_time.month
        monthly_counts[month] = monthly_counts.get(month, 0) + 1
    
    if not monthly_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': f"Rok {year} (brak danych)",
            'best_month': None
        }
    
    best_month = max(monthly_counts, key=monthly_counts.get)
    
    stats = get_month_stats(year, best_month)
    stats['period'] = f"Najlepszy miesiąc w roku {year}"
    stats['best_month'] = f"{year}-{best_month:02d}"
    
    return stats


def get_best_quarter_in_year(year):
    """
    Znajduje kwartał z największą liczbą zajęć w danym roku.
    """
    start_of_year = timezone.make_aware(datetime(year, 1, 1))
    end_of_year = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(seconds=1)
    
    occupations = ParkingOccupation.objects.filter(
        occupied_at__gte=start_of_year,
        occupied_at__lte=end_of_year
    )
    
    quarterly_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        month = local_time.month
        quarter = (month - 1) // 3 + 1
        quarterly_counts[quarter] += 1
    
    if sum(quarterly_counts.values()) == 0:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': f"Rok {year} (brak danych)",
            'best_quarter': None
        }
    
    best_quarter = max(quarterly_counts, key=quarterly_counts.get)
    
    stats = get_quarter_stats(year, best_quarter)
    stats['period'] = f"Najlepszy kwartał w roku {year}"
    stats['best_quarter'] = f"{year}-{best_quarter}"
    
    return stats


def get_best_day_overall():
    """
    Znajduje dzień z największą liczbą zajęć we wszystkich danych.
    """
    occupations = ParkingOccupation.objects.all()
    
    daily_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        day = local_time.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    if not daily_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': 'Wszystkie dane (brak danych)',
            'best_day': None
        }
    
    best_day = max(daily_counts, key=daily_counts.get)
    
    start_datetime = timezone.make_aware(datetime.combine(best_day, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(best_day, datetime.max.time()))
    
    stats = get_daily_stats(start_datetime, end_datetime)
    stats['period'] = 'Najlepszy dzień (wszystkie dane)'
    stats['best_day'] = best_day.strftime('%Y-%m-%d')
    
    return stats


def get_best_month_overall():
    """
    Znajduje miesiąc z największą liczbą zajęć we wszystkich danych.
    """
    occupations = ParkingOccupation.objects.all()
    
    monthly_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        year_month = (local_time.year, local_time.month)
        monthly_counts[year_month] = monthly_counts.get(year_month, 0) + 1
    
    if not monthly_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': 'Wszystkie dane (brak danych)',
            'best_month': None
        }
    
    best_year, best_month = max(monthly_counts, key=monthly_counts.get)
    
    stats = get_month_stats(best_year, best_month)
    stats['period'] = 'Najlepszy miesiąc (wszystkie dane)'
    stats['best_month'] = f"{best_year}-{best_month:02d}"
    
    return stats


def get_best_quarter_overall():
    """
    Znajduje kwartał z największą liczbą zajęć we wszystkich danych.
    """
    occupations = ParkingOccupation.objects.all()
    
    quarterly_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        quarter = (local_time.month - 1) // 3 + 1
        year_quarter = (local_time.year, quarter)
        quarterly_counts[year_quarter] = quarterly_counts.get(year_quarter, 0) + 1
    
    if not quarterly_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': 'Wszystkie dane (brak danych)',
            'best_quarter': None
        }
    
    best_year, best_quarter = max(quarterly_counts, key=quarterly_counts.get)
    
    stats = get_quarter_stats(best_year, best_quarter)
    stats['period'] = 'Najlepszy kwartał (wszystkie dane)'
    stats['best_quarter'] = f"{best_year}-{best_quarter}"
    
    return stats


def get_best_year_overall():
    """
    Znajduje rok z największą liczbą zajęć we wszystkich danych.
    """
    occupations = ParkingOccupation.objects.all()
    
    yearly_counts = {}
    for occ in occupations:
        local_time = timezone.localtime(occ.occupied_at)
        year = local_time.year
        yearly_counts[year] = yearly_counts.get(year, 0) + 1
    
    if not yearly_counts:
        return {
            'spots': [],
            'total_occupations': 0,
            'period': 'Wszystkie dane (brak danych)',
            'best_year': None
        }
    
    best_year = max(yearly_counts, key=yearly_counts.get)
    
    stats = get_year_stats(best_year)
    stats['period'] = 'Najlepszy rok (wszystkie dane)'
    stats['best_year'] = str(best_year)
    
    return stats

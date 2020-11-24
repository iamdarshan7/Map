from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium

# Create your views here.
def calculate_distance_view(request):
    distance = None
    destination = None
    obj = get_object_or_404(Measurement, id=40)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent="measurements")
    
    # ip = '192.168.100.3'                      
    # ip = '72.14.207.99'                      
    # ip = '85.214.18.16'
    ip = '27.34.68.25'
    # ip = get_ip_address(request)
    # print(ip)                      
    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)
    print(location)
    
    # location co-ordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)
    
    # initialize folium
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8) 
    # location marker
    folium.Marker([l_lat, l_lon], tooltip="click here for more", popup=city['city'],
                     icon=folium.Icon(color="purple")).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # destination co-ordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        # distance calculation
        distance = round(geodesic(pointA,pointB).km,2)

        # folium map modification
        m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon),zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip="click here for more", popup=city['city'],
                     icon=folium.Icon(color="purple")).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip="click here for more", popup=destination,
                     icon=folium.Icon(color="red", icon="cloud")).add_to(m)


        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA,pointB], weight=2, color="blue")
        m.add_child(line)  

        instance.location = location
        instance.distance =  distance
        instance.save()

    m = m._repr_html_()
    
    context = {
        "distance": distance,
        "destination": destination,
        "form": form,
        'map': m,  
    }

    return render(request, 'measurements/main.html', context)

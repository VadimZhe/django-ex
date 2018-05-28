var map;
var xhr;

function initMap() {
    var uluru = {lat: 60, lng: 30};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: uluru
    });
    xhr = new XMLHttpRequest();
    xhr.open('GET', "/contacts/locations", true);
    xhr.send();
    xhr.addEventListener("readystatechange", drawLocations, true);
}

function drawLocations(e) {
     if (xhr.readyState == 4 && xhr.status == 200) {
        var response = JSON.parse(xhr.responseText);
        //alert(response.locations[0].name);
        bounds  = new google.maps.LatLngBounds()
        response.locations.forEach(function(item, i, arr) {
            //alert( i + ": " + item + " (массив:" + arr + ")" );
            var marker = new google.maps.Marker({
                map: map,
                draggable: false,
                //animation: google.maps.Animation.DROP,
                position: {lat: item.latitude, lng: item.longitude},
                icon: '/static/img/marker_16.png',
                title: 'titletitle'
            });
            loc = new google.maps.LatLng(marker.position.lat(), marker.position.lng());
            bounds.extend(loc);
            var infowindow = new google.maps.InfoWindow({
                content: '<h4>' + item.name + '</h3><br>' + item.address + '<br>' + item.hours
            });
            marker.addListener('click', function() {
                infowindow.open(map, marker);
            });
        });
        map.fitBounds(bounds);       // auto-zoom
        map.panToBounds(bounds);     // auto-center
     }
}
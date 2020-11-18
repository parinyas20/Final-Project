import folium, os
from folium import plugins
from folium.plugins import MarkerCluster, HeatMap


def plot_map(df, lat, long, city=None, zoom_start=10, search_term=None, report_path=None):
    if city:
        df = df[df.filename.str.startswith(city.lower())]
    if search_term:
        df = df[df.Issue.apply(str.lower).str.contains(search_term.lower())]

    m = folium.Map(location=[lat, long],zoom_start=zoom_start)

    for _,row in  df.iterrows():
        lat = row.get('lat')
        long = row.get('long')
        issues = row.get('Issue')
        duration = row.get('Duration')
        timestamp = row.get('TimeStamp')
        tooltip = f'''Issues: {issues},
Duration: {duration},
Timestamp: {timestamp}
    '''
        if report_path:
            try:
                with open(os.path.join(report_path,row.filename)) as f:
                    popup = f.read()
            except:
                popup = row.filename
        else:
            popup = row.filename

#     print(lat, long)
#     print(popup)
        folium.Circle(radius=50,
                    location=[lat, long], # coordinates for the marker 
                    tooltip=tooltip,
                    popup=popup, # pop-up label for the marker
                    color='red',
                    fill=True,
                    fill_color='red',
                    ).add_to(m)
    return m

def plot_heat_map(df, lat, long, city=None, radius=10, zoom_start=10):
    df = df[df.filename.str.startswith(city.lower())]
    coordinates = df[['lat','long']].values
    m = folium.Map(location=[lat, long],zoom_start=zoom_start)

    m.add_child(HeatMap(coordinates, radius=radius))
    return m
    

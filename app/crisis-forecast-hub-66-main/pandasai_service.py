from flask import Flask, request, jsonify
from matplotlib.colors import LinearSegmentedColormap
#%pip install folium
import folium
from folium import IFrame, Map, Marker, Icon, Element
from folium.plugins import MarkerCluster
from jinja2 import Template
#%pip install plotly
import plotly.express as px
import plotly.graph_objects as go
#import pandas as pd
#from pandasai import SmartDataframe
##from pandasai.llm.openai import OpenAI
#from pandasai.llm import OpenAI
#from pandasai.llm import BambooLLM 
##from pandasai.llm_registry import LLMRegistry
##from pandasai.llms import OpenAI
#from pandasai.llm import Transformers
#from pandasai.llm.base import LLM
import pandasai as pai
import pandas as pd
import matplotlib
matplotlib.use('agg')  # must be first!
import matplotlib.pyplot as plt
print(f"Matplotlib backend in use: {matplotlib.get_backend()}")
import uuid
import os
from dotenv import load_dotenv
import shutil
from sqlalchemy import create_engine, text
import json
import ast
import re

# Load env variables
load_dotenv()

# Database connection settings
db_user = os.getenv('PG_DB_USER') #'myuser' 
db_password = os.getenv('PG_DB_PASSWORD') #'mypassword'
db_host = os.getenv('PG_DB_HOST') #'localhost'
db_port = os.getenv('PG_DB_PORT') #'5432'
db_name = os.getenv('PG_DB_NAME') #'mydatabase'
db_schema = os.getenv('PG_DB_SCHEMA') #'ccar'
pai_api_key = os.getenv("PANDAS_AI_API_KEY")

pai.api_key.set(pai_api_key)


engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
#print(os.getcwd())

dataset_path = "../../datasets/ccar/merged"
if os.path.exists(dataset_path):
    shutil.rmtree(dataset_path)

sql_table1 = pai.create(
    path="ccar/merged",
    source={
        "type": "postgres",
        "connection": {
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_password,
            "database": db_name
        },
        "table": "merged"
    }
)

merged = pai.load("ccar/merged")

dataset_path = "../../datasets/ccar/historical"
if os.path.exists(dataset_path):
    shutil.rmtree(dataset_path)

sql_table2 = pai.create(
    path="ccar/historical",
    source={
        "type": "postgres",
        "connection": {
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_password,
            "database": db_name
        },
        "table": "historical"
    }
)

historical = pai.load("ccar/historical")

dataset_path = "../../datasets/ccar/prediction-future"
if os.path.exists(dataset_path):
    shutil.rmtree(dataset_path)

sql_table3 = pai.create(
    path="ccar/prediction-future",
    source={
        "type": "postgres",
        "connection": {
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_password,
            "database": db_name
        },
        "table": "prediction_future"
    }
)

prediction_future = pai.load("ccar/prediction-future")



app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_question():

    data = request.get_json()

    question = data.get("question", "")
    print(question)
    try:

        #pai.api_key.set(pai_api_key)
        #df = pai.read_csv("/home/user/BTS/finalProject/CCAR/data/ccar_merged.csv")
        #response = df.chat(question)
        #print(response)


        response = pai.chat(question, merged, historical, prediction_future)

        #plot_url = None
        # If the response is a DataFrameResponse
        if hasattr(response, "type") and response.type == "dataframe":
            df1 = response.value
            print(df1)
            json_result = df1.to_json(orient="records")  # list of dicts
            #json_result = jsonify(df1.to_dict(orient="records"))
            result = jsonify({"answer": json_result}) 
        elif plt.get_fignums():
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join("exports/charts/", filename)
            plt.savefig(filepath)
            plt.close('all')
            plot_url = f"exports/charts/{filename}"
            result = jsonify({"answer": "plot", "plot_url": plot_url})
        else:
            result = jsonify({"answer": str(response)})
        
        #print(result)

        return result
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/plot', methods=['POST'])
def plot_graph():

    data = request.get_json()
    country = data.get("country", "")
    print(country)
    try:

        if country:
            #df = pd.read_sql('SELECT * FROM your_table_name', con=engine)
            #historical_data_df = pd.read_csv('/home/user/BTS/finalProject/CCAR/data/ccar_historical_data.csv', parse_dates=['ds'])
            #predicted_past_df = pd.read_csv('/home/user/BTS/finalProject/CCAR/data/ccar_predicted_past.csv', parse_dates=['ds'])
            #predicted_future_df = pd.read_csv('/home/user/BTS/finalProject/CCAR/data/ccar_predicted_future.csv', parse_dates=['ds'])
            historical_data_df = pd.read_sql('SELECT * FROM historical', con=engine, parse_dates=['date'])
            predicted_past_df = pd.read_sql('SELECT * FROM prediction_past', con=engine, parse_dates=['date'])
            predicted_future_df = pd.read_sql('SELECT * FROM prediction_future', con=engine, parse_dates=['date'])

            historical_data_df = historical_data_df[historical_data_df['country'] == country]
            predicted_past_df = predicted_past_df[predicted_past_df['country'] == country]
            predicted_future_df = predicted_future_df[predicted_future_df['country'] == country]
            max_date = historical_data_df['date'].max()

            # Plot
            plt.figure(figsize=(14, 6))
            plt.plot(historical_data_df['date'], historical_data_df['most_needs_idx'], label='Actual (last 1 year)', color='black') #historical_data_df['y']
            plt.plot(predicted_past_df['date'], predicted_past_df['most_needs_idx'], label='Predicted (past 6 months)', color='orange') #predicted_past_df['yhat']
            plt.plot(predicted_future_df['date'], predicted_future_df['most_needs_idx'], label='Predicted (next 6 months)', color='dodgerblue') #predicted_future_df['yhat']

            plt.axvline(x=max_date, color='gray', linestyle='--', label='Forecast split')
            plt.xlabel('Date')
            plt.ylabel('most_needs_idx')
            plt.title(f'Model Forecast for {country}')
            plt.legend()
            plt.tight_layout()
            plt.grid(True)
            #plt.show()
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join("exports/charts/", filename)
            plt.savefig(filepath)
            plt.close('all')
            plot_url = f"exports/charts/{filename}"
            result = jsonify({"type": "plot", "plot_url": plot_url})


        #print(result)
        return result
    
    except Exception as e:

        return jsonify({"error": str(e)}), 500
    

#@app.route('/map', methods=['POST'])
def map1():

    #data = request.get_json()
    #country = data.get("country", "")
    #print(country)
    try:

        # Load the CCAR historical and prediction datasets
        df_hist = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ccar_historical.csv")
        df_pred = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ccar_prediction.csv")
        # Load the country coordinates dataset
        coords = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/countries_codes_and_coordinates.csv")

        # Get the latest record per country from each dataset
        latest_hist = df_hist.sort_values("date").groupby("country").tail(1)
        latest_pred = df_pred.sort_values("date").groupby("country").tail(1)
                            
        # Union of the two datasets
        df_union = pd.concat([latest_hist, latest_pred], ignore_index=True)

        # Standardize column names for merging
        coords = coords.rename(columns={
            'Country': 'country',
            'Latitude (average)': 'latitude',
            'Longitude (average)': 'longitude'
        })

        # Optional: strip whitespace and normalize case
        coords['country'] = coords['country'].str.strip()
        df_union['country'] = df_union['country'].str.strip()

        # Merge on country name
        df_filtered = df_union.merge(coords[['country', 'latitude', 'longitude']], on='country', how='left')

        df_filtered['date'] = pd.to_datetime(df_filtered['date'], errors='coerce')

        #df_filtered = df_union[df_union['latitude'].notnull() & df_union['longitude'].notnull()]

        #df = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ACLED/cleaned_acled.csv")
        #df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        #df_filtered =  df.tail(5000)
        #df_filtered = df[df['event_date'] > pd.Timestamp('2025-04-30')]

        #<b>Fatalities:</b> {int(row.get('fatalities')) if pd.notna(row.get('fatalities')) else 'Unknown'}<br>

        if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
            # Remove rows with missing coordinates
            df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])
            df_filtered['latitude'] = pd.to_numeric(
                df_filtered['latitude'].astype(str).str.replace('"', '').str.strip(),
                errors='coerce'
            )
            df_filtered['longitude'] = pd.to_numeric(
                df_filtered['longitude'].astype(str).str.replace('"', '').str.strip(),
                errors='coerce'
            )

            #print(df_filtered.sort_values("country"))
            #print ("mean_lon: "+str(mean_lon))

            # Create a map centered on the mean coordinates
            mean_lat = df_filtered['latitude'].mean()
            mean_lon = df_filtered['longitude'].mean()

            conflict_map = folium.Map(location=[mean_lat, mean_lon], zoom_start=3, tiles='CartoDB positron')
            
            # Add a marker cluster
            ##marker_cluster = MarkerCluster().add_to(conflict_map)
            # Create MarkerCluster with custom cluster icon creation
            marker_cluster = MarkerCluster(
                name="Needs Index Cluster",
                control=False,
                overlay=True,
                icon_create_function=Template("""
                    function(cluster) {
                        var markers = cluster.getAllChildMarkers();
                        var maxIndex = 0;
                        for (var i = 0; i < markers.length; i++) {
                            console.log("Marker idx:", markers[i].most_needs_idx);  // Debug print
                            var idx = markers[i].most_needs_idx;
                            if (idx > maxIndex) {
                                maxIndex = idx;
                            }
                        }
                        var color;
                        if (maxIndex > 0.6) {
                            color = 'red';
                        } else if (maxIndex > 0.5) {
                            color = 'orange';
                        } else if (maxIndex > 0.4) {
                            color = 'beige';
                        } else if (maxIndex > 0.3) {
                            color = 'blue';
                        } else {
                            color = 'blue';
                        }
                        return new L.DivIcon({
                            html: '<div style="background-color:' + color + '; border-radius:50%; padding:6px 10px; color:white;"><b>' + cluster.getChildCount() + '</b></div>',
                            className: 'marker-cluster',
                            iconSize: new L.Point(40, 40)
                        })
                    }
                """).render()
            ).add_to(conflict_map)



            # Add markers for each event
            for idx, row in df_filtered.iterrows():
                popup_text = f"""
                <b>Location:</b>{row.get('country', 'Unknown')}<br>
                <b>Date:</b> {row.get('date').strftime('%Y-%m-%d') if pd.notna(row.get('date')) else 'Unknown'}<br>
                <b>CCAR most needs index:</b> {row.get('most_needs_idx', 'Unknown')}<br>
                """
                
                # Color based on event type
                if row.get('most_needs_idx') > 0.6:
                    icon_color = 'red'
                elif row.get('most_needs_idx') > 0.5:
                    icon_color = 'orange'
                elif row.get('most_needs_idx') > 0.4:
                    icon_color = 'beige'
                elif row.get('most_needs_idx') > 0.3:
                    icon_color = 'blue'
                else:
                    icon_color = 'green'
                
                marker = folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=icon_color)
                ) #.add_to(marker_cluster)
                #marker.options = {**marker.options, "most_needs_idx": row.get("most_needs_idx")}
                marker.add_to(marker_cluster)

                # Add custom JavaScript to attach most_needs_idx to marker
                js = Element(f"""
                    <script>
                        var lastMarker = marker_cluster.getLayers()[marker_cluster.getLayers().length - 1];
                        if (lastMarker) {{
                            lastMarker.most_needs_idx = {row.get("most_needs_idx")};
                        }}
                    </script>
                """)
                conflict_map.get_root().html.add_child(js)

            # Add a legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 180px; height: 180px; 
                    border:2px solid grey; z-index:9999; font-size:12px;
                    background-color:white; padding: 10px;
                    border-radius: 5px;">
            <p><b>Most Needs Categories:</b></p>
            <p><i class="fa fa-circle" style="color:red"></i> Critical Need</p>
            <p><i class="fa fa-circle" style="color:orange"></i> High Need</p>
            <p><i class="fa fa-circle" style="color:beige"></i> Medium Need</p>
            <p><i class="fa fa-circle" style="color:blue"></i> Low Need</p>
            <p><i class="fa fa-circle" style="color:green"></i> Very Low Need</p>
        </div>
        '''
        conflict_map.get_root().html.add_child(folium.Element(legend_html))

        # Add layer control
        folium.LayerControl().add_to(conflict_map)

        # Display map in notebook
        #conflict_map


            
        # Save the map to an HTML file
        map_url = "exports/maps/conflict_map.html"
        conflict_map.save(map_url)
        print("Interactive map saved as 'exports/maps/conflict_map.html'")

        result = jsonify({"type": "map", "plot_url": map_url})


        #print(result)
        return result
    
    except Exception as e:

        #return jsonify({"error": str(e)}), 500
        return str(e)
    

#@app.route('/map', methods=['POST'])
def map():

    #data = request.get_json()
    #country = data.get("country", "")
    #print(country)
    try:

        # Load the CCAR historical and prediction datasets
        #df_hist = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ccar_historical.csv")
        df_hist = pd.read_sql('SELECT * FROM historical', con=engine, parse_dates=['date'])
        #df_pred = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ccar_prediction.csv")
        df_pred = pd.read_sql('SELECT * FROM prediction_future', con=engine, parse_dates=['date'])
        # Load the country coordinates dataset
        #coords = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/countries_codes_and_coordinates.csv")
        coords = pd.read_sql('SELECT * FROM country', con=engine)

        # Get the latest record per country from each dataset
        latest_hist = df_hist.sort_values("date").groupby("country").tail(1)
        latest_pred = df_pred.sort_values("date").groupby("country").tail(1)
                            
        # Union of the two datasets
        df_union = pd.concat([latest_hist, latest_pred], ignore_index=True)

        # Standardize column names for merging
        #coords = coords.rename(columns={
        #    'Country': 'country',
        #    'Latitude (average)': 'latitude',
        #    'Longitude (average)': 'longitude'
        #})

        # Optional: strip whitespace and normalize case
        coords['country'] = coords['country'].str.strip()
        df_union['country'] = df_union['country'].str.strip()

        # Merge on country name
        df_filtered = df_union.merge(coords[['country', 'latitude', 'longitude']], on='country', how='left')

        df_filtered['date'] = pd.to_datetime(df_filtered['date'], errors='coerce')

        #df_filtered = df_union[df_union['latitude'].notnull() & df_union['longitude'].notnull()]

        #df = pd.read_csv("/home/user/BTS/finalProject/CCAR/data/ACLED/cleaned_acled.csv")
        #df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        #df_filtered =  df.tail(5000)
        #df_filtered = df[df['event_date'] > pd.Timestamp('2025-04-30')]

        #<b>Fatalities:</b> {int(row.get('fatalities')) if pd.notna(row.get('fatalities')) else 'Unknown'}<br>

        if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
            # Remove rows with missing coordinates
            df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])
            df_filtered['latitude'] = pd.to_numeric(
                df_filtered['latitude'].astype(str).str.replace('"', '').str.strip(),
                errors='coerce'
            )
            df_filtered['longitude'] = pd.to_numeric(
                df_filtered['longitude'].astype(str).str.replace('"', '').str.strip(),
                errors='coerce'
            )

            #print(df_filtered.sort_values("country"))
            #print ("mean_lon: "+str(mean_lon))

            # Create a map centered on the mean coordinates
            mean_lat = df_filtered['latitude'].mean()
            mean_lon = df_filtered['longitude'].mean()

            conflict_map = folium.Map(location=[mean_lat, mean_lon], zoom_start=3, tiles='CartoDB positron')

            icon_create_function = Template("""
                function(cluster) {
                    var markers = cluster.getAllChildMarkers();
                    var maxIndex = 0;
                    for (var i = 0; i < markers.length; i++) {
                        var idx = markers[i].options.most_needs_idx || 0;
                        if (idx > maxIndex) {
                            maxIndex = idx;
                        }
                    }
                    var color = maxIndex > 0.6 ? 'red' :
                                maxIndex > 0.5 ? 'orange' :
                                maxIndex > 0.4 ? 'purple' :
                                maxIndex > 0.3 ? 'blue' : 'green';

                    return new L.DivIcon({
                        html: '<div style="background-color:' + color + '; border-radius:50%; padding:6px 10px; color:white;"><b>' + cluster.getChildCount() + '</b></div>',
                        className: 'marker-cluster',
                        iconSize: new L.Point(40, 40)
                    });
                }
            """).render()

            # Create JS-based marker cluster (manually)
            cluster_js = """
            <script>
            var marker_cluster = L.markerClusterGroup({
                iconCreateFunction: %s
            });
            """ % icon_create_function


            # Add markers for each event
            for idx, row in df_filtered.iterrows():
                popup_text = f'''
                <b>Location:</b>{row.get('country', 'Unknown')}<br>
                <b>Date:</b> {row.get('date').strftime('%Y-%m-%d') if pd.notna(row.get('date')) else 'Unknown'}<br>
                <b>CCAR most needs index:</b> {row.get('most_needs_idx', 'Unknown')}<br>
                '''

                lat, lon = row["latitude"], row["longitude"]
                idx = row.get('most_needs_idx') 

                # Color based on event type
                if row.get('most_needs_idx') > 0.6:
                    icon_color = 'red'
                elif row.get('most_needs_idx') > 0.5:
                    icon_color = 'orange'
                elif row.get('most_needs_idx') > 0.4:
                    icon_color = 'purple'
                elif row.get('most_needs_idx') > 0.3:
                    icon_color = 'blue'
                else:
                    icon_color = 'green'
                
                # Add JS for each marker
                cluster_js += f"""
                var marker = L.marker([{lat}, {lon}], {{
                    icon: L.AwesomeMarkers.icon({{
                        icon: 'info-sign',
                        markerColor: '{icon_color}'
                    }}),
                    most_needs_idx: {idx}
                }}).bindPopup(`{popup_text}`);
                marker_cluster.addLayer(marker);
                """

        # Close script and add to map
        #cluster_js += "\nmap.addLayer(marker_cluster);\n</script>"
        cluster_js += "\n</script>"


        # Inject JS directly into HTML
        conflict_map.get_root().html.add_child(folium.Element(cluster_js))

        # Add a legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 180px; height: 180px; 
                    border:2px solid grey; z-index:9999; font-size:12px;
                    background-color:white; padding: 10px;
                    border-radius: 5px;">
            <p><b>Most Needs Categories:</b></p>
            <p><i class="fa fa-circle" style="color:red"></i> Critical Need</p>
            <p><i class="fa fa-circle" style="color:orange"></i> High Need</p>
            <p><i class="fa fa-circle" style="color:purple"></i> Medium Need</p>
            <p><i class="fa fa-circle" style="color:blue"></i> Low Need</p>
            <p><i class="fa fa-circle" style="color:green"></i> Very Low Need</p>
        </div>
        '''
        conflict_map.get_root().html.add_child(folium.Element(legend_html))


        # Add layer control
        folium.LayerControl().add_to(conflict_map)

        end_header = "</head>\n<body>"

        markercluster_libs = """
        <!-- Leaflet.markercluster JS and CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
        <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
        <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
        </head>\n<body>
        """
        #conflict_map.get_root().header.add_child(folium.Element(markercluster_libs))

        old_end_js = "</script>\n</html>"

        new_end_js = f"""
        map_{conflict_map._id}.addLayer(marker_cluster);
        map_{conflict_map._id}.fitBounds(marker_cluster.getBounds());
        </script>\n</html>
        """
        #conflict_map.get_root().html.add_child(folium.Element(end_js))


        # Render full HTML as a string
        html_str = conflict_map.get_root().render()

        # Replace a specific string
        html_str = html_str.replace(end_header, markercluster_libs)
        html_str = html_str.replace(old_end_js, new_end_js)

        # Save the map to an HTML file
        map_url = "exports/maps/conflict_map.html"
        #conflict_map.save(map_url)

        # Save the modified HTML
        with open(map_url, "w", encoding="utf-8") as f:
            f.write(html_str)
        print("Interactive map saved as 'exports/maps/conflict_map.html'")

        result = jsonify({"type": "map", "plot_url": map_url})


        #print(result)
        return result
    
    except Exception as e:

        #return jsonify({"error": str(e)}), 500
        return str(e)
    


def get_url(code):
  # Find the line that defines `result = { ... }`
  match = re.search(r'result\s*=\s*({.*})', code)

  if match:
      result_str = match.group(1)
      result_dict = ast.literal_eval(result_str)
      #print(result_dict)  # {'type': 'plot', 'value': 'exports/charts/....png'}
      result_json = json.dumps(result_dict)
      print(result_json)
  else:
      print("No result dictionary found.")
  
  return result_json



if __name__ == "__main__":
    print(map())
    app.run(port=5001)




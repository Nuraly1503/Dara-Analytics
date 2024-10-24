
import pandas as pd
from shiny import App, render, ui
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np


df = pd.read_csv('airlinedelaycauses_DelayedFlights.csv', 
                 na_values=['NA', 'null', '', 'NULL'])
df = df.dropna()

month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

unique_carriers = df['UniqueCarrier'].unique()

all_carriers_option = ["All Carriers"] + unique_carriers.tolist()

app_ui = ui.page_fluid(
    ui.input_select("month", "Select a month:", 
                    choices=list(month_mapping.keys()), 
                    selected="January"),
    ui.input_select("carrier", "Select a Carrier:", 
                    choices=all_carriers_option,
                    selected="All Carriers"),
    ui.input_select("day", "Select a day:", 
                    choices=list(range(1, 32)), 
                    selected=1),
    ui.navset_tab(
        ui.nav_panel("Delay Type Hours",
                     ui.output_plot("delay_type_plot")),
        ui.nav_panel("Carrier Delay Distribution",
                     ui.output_plot("carrier_delay_plot")),
        ui.nav_panel("Monthly Occurrences",
                     ui.output_plot("monthly_occurrences_plot")),
        ui.nav_panel("Carrier Destinations",
                        ui.output_plot("carrier_dest_plot"))
    )
)

def server(input, output, session):
    @output
    @render.plot
    def delay_type_plot():
        selected_month = month_mapping[input.month()]
        selected_carrier = input.carrier()
        selected_day = int(input.day())

        if selected_carrier == "All Carriers":
            filtered_df = df[(df['Month'] == selected_month) & (df['DayofMonth'] == selected_day)]
        else:
            filtered_df = df[(df['Month'] == selected_month) & (df['DayofMonth'] == selected_day) & (df['UniqueCarrier'] == selected_carrier)]

        total_delay_hours = {
            "CarrierDelay": filtered_df['CarrierDelay'].sum() / 60,
            "WeatherDelay": filtered_df['WeatherDelay'].sum() / 60,
            "NASDelay": filtered_df['NASDelay'].sum() / 60,
            "SecurityDelay": filtered_df['SecurityDelay'].sum() / 60,
            "LateAircraftDelay": filtered_df['LateAircraftDelay'].sum() / 60
        }
        
        plot_df = pd.DataFrame({
            "DelayType": total_delay_hours.keys(),
            "TotalHours": total_delay_hours.values()
        })

        plt.figure(figsize=(10, 6))
        sns.barplot(data=plot_df, x="DelayType", y="TotalHours", color="skyblue")
        plt.title(f"Total Hours of Delay Types for {selected_carrier} in {input.month()} on {selected_day}")
        plt.xlabel("Delay Type")
        plt.ylabel("Total Hours of Delay")
        plt.tight_layout()

    @output
    @render.plot
    def carrier_delay_plot():
        selected_month = month_mapping[input.month()]
        selected_carrier = input.carrier()
        selected_day = int(input.day())

        if selected_carrier == "All Carriers":
            filtered_df = df[(df['Month'] == selected_month) & (df['DayofMonth'] == selected_day)]
        else:
            filtered_df = df[(df['Month'] == selected_month) & (df['DayofMonth'] == selected_day) & (df['UniqueCarrier'] == selected_carrier)]
        
        total_delays = filtered_df[['CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay']].sum()
        
        labels = total_delays.index
        sizes = total_delays.values
        explode = (0.1, 0, 0, 0, 0)

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('Set2'))
        plt.title(f'Percentage of Delay Types for {selected_carrier} in {input.month()} on {selected_day}')
        plt.axis('equal')  
        plt.tight_layout()

    @output
    @render.plot
    def monthly_occurrences_plot():
        selected_carrier = input.carrier()

        if selected_carrier == "All Carriers":
            occurrences_by_month = df.groupby('Month').size().reset_index(name='Occurrences')
        else:
            occurrences_by_month = df[df['UniqueCarrier'] == selected_carrier].groupby('Month').size().reset_index(name='Occurrences')

        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        occurrences_by_month['MonthName'] = occurrences_by_month['Month'].map(lambda x: month_names[x - 1])

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=occurrences_by_month, x='MonthName', y='Occurrences', marker='o', color='blue')
        plt.title(f"Monthly Occurrences of Delayed Flights for {selected_carrier}")
        plt.xlabel("Month")
        plt.ylabel("Number of Occurrences")
        plt.xticks(rotation=45)  
        plt.tight_layout()

    @output
    @render.plot
    def carrier_dest_plot():
        selected_carrier = input.carrier()
        selected_month = month_mapping[input.month()]
        if selected_carrier == "All Carriers":
            filtered_df = df[(df['Month'] == selected_month)]
        else:
            filtered_df = df[(df['Month'] == selected_month) & (df['UniqueCarrier'] == selected_carrier)]

        carrier_dest = filtered_df.groupby('Dest').size().reset_index(name='Occurrences')
        carrier_dest = carrier_dest.sort_values(by='Occurrences', ascending=False).head(10)

        plt.figure(figsize=(10, 10))
        plt.pie(carrier_dest['Occurrences'], labels=carrier_dest['Dest'], autopct='%1.1f%%', 
                startangle=90, colors=plt.cm.tab20c(np.linspace(0.2, 0.7, len(carrier_dest))))
        plt.title(f"Top 10 Destinations for {selected_carrier} in {input.month()}", fontsize=16, pad=20)
        plt.legend(title="Destinations", loc="upper right", fontsize='small')
        plt.axis('equal')
        plt.tight_layout()


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

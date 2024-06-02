import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import requests

df = pd.read_csv('data/full_data.csv')

add_selectbox = st.sidebar.selectbox(
    "Navigate through the tabs",
    ("Leaderboard", "Total Amount", "Restaurant Recommendation")
)

if add_selectbox == 'Leaderboard':

    st.markdown("# Leaderboard")

    col1, col2 = st.columns(2)

    with col1:
        
        data = df.groupby('name')\
                .agg({'approx_cost(for two people)':'mean'})\
                .reset_index()\
                .rename(columns={'approx_cost(for two people)':'cost'})\
        
        data['rank'] = data['cost'].rank(method='dense',
                                        ascending=False)
        data = data.drop_duplicates(subset='rank')
        data = data.sort_values('cost',
                                ascending=False)
        data = data.head(10)
        
        with st.container():

            st.write('Top 10 Most Expensive Restaurant')
            st.bar_chart(data=data,
                        x='name',
                        y='cost',
                        use_container_width=True)
            
    with col2:

        data = df.groupby('rest_type')\
                .agg({'approx_cost(for two people)':'mean'})\
                .reset_index()\
                .rename(columns={'approx_cost(for two people)':'cost'})\
        
        data['rank'] = data['cost'].rank(method='dense',
                                        ascending=False)
        data = data.drop_duplicates(subset='rank')
        data = data.sort_values('cost',
                                ascending=False)
        data = data.head(10)
        
        with st.container():

            st.write('Top 10 Most Expensive Restaurant Type')
            st.bar_chart(data=data,
                        x='rest_type',
                        y='cost',
                        use_container_width=True)
            

    col1, col2 = st.columns(2)

    with col1:

        data = df[df['online_order'] == 'Yes']\
                .groupby('name')\
                .agg({'approx_cost(for two people)':'mean'})\
                .reset_index()\
                .rename(columns={'approx_cost(for two people)':'cost'})\
                .sort_values('cost',
                            ascending=False)\
                .head(1)\
                .to_numpy()
        
        with st.chat_message("assistant"):

            st.write('Most Expensive Restaurant With Online Order')
            st.markdown(f"### {data[0, 0]} \n # {data[0, 1]}")

    with col2:

        data = df[df['online_order'] == 'No']\
                .groupby('name')\
                .agg({'approx_cost(for two people)':'mean'})\
                .reset_index()\
                .rename(columns={'approx_cost(for two people)':'cost'})\
                .sort_values('cost',
                            ascending=False)\
                .head(1)\
                .to_numpy()
        with st.chat_message("assistant"):
            
            st.write('Most Expensive Restaurant Without Online Order  ')
            st.markdown(f"### {data[0, 0]} \n # {data[0, 1]}")
if add_selectbox == 'Total Amount':
    st.markdown("# Total Amount")

    st.write('Cities With Most Restaurant Map')
    data = df['listed_in(city)'].value_counts()\
                                    .reset_index()\
                                    .rename(columns={'listed_in(city)':'city',
                                                    'count':'total'})
    data['rank'] = data['total'].rank(method='dense',
                                        ascending=False)
    data['total'] *= 10e+2 * 1.5
    data = data.sort_values('total',
                            ascending=False)
    data = data.head(5)
    geoloc = [(12.924920, 77.555931), (29.837481, 77.928062), (12.807970, 77.562401), (12.926031, 77.676247), (54.875900, -6.258100)]
    data['lat'], data['long'] = np.array([i[0] for i in geoloc]), np.array([i[1] for i in geoloc])

    st.map(data,
            latitude='lat',
            longitude='long',
            size='total',
            color='#0000FF')

    col1, col2 = st.columns(2)

    with col1:

        data = df['listed_in(city)'].value_counts()\
                                    .reset_index()\
                                    .rename(columns={'listed_in(city)':'city',
                                                    'count':'total'})
            
        data['rank'] = data['total'].rank(method='dense',
                                            ascending=False)
        data = data.drop_duplicates(subset='rank')
        data = data.sort_values('total',
                                ascending=False)
        data = pd.concat([data.head(5),
                        pd.DataFrame({'city':['Other'],
                                        'total':[data.tail(data.shape[0]-5)['total'].sum()]})])
        
        with st.container():

            st.write('Cities With Most Restaurant')
            fig = alt.Chart(data).mark_arc()\
                                    .encode(theta='total',
                                            color='city',
                                            tooltip=['city', 'total'])\
                                    .properties(width=200,
                                                height=200)

            st.altair_chart(fig, use_container_width=True)
        
    with col2:

        data = df['online_order'].value_counts()\
                                .reset_index()
        
        with st.container():

            st.write('Online Order Distribution')
            fig = alt.Chart(data).mark_arc()\
                                    .encode(theta='count',
                                            color='online_order',
                                            tooltip=['online_order', 'count'])\
                                    .properties(width=200,
                                                height=200)

            st.altair_chart(fig, use_container_width=True)

if add_selectbox == 'Restaurant Recommendation':

    col1, col2 = st.columns(2)
    url1 = 'http://127.0.0.1:8000/recommendation1'
    url2 = 'http://127.0.0.1:8000/recommendation2'

    page = None
    restaurant = None
    result1 = None
    result2 = None

    with col1:

        city = st.selectbox('Select city : ',
                            (i for i in df['listed_in(city)'].unique()),
                            index=None,
                            placeholder="Select here")
        
        if city != None:

            data = df[df['listed_in(city)'] == city]['name'].unique()
            maxi = len(data) - (len(data) % 5)
            restaurants = [f"{i+1} - {i+5}" for i in range(0, (maxi + 1), 5)][:-1] + [f"{maxi} - {maxi + (len(data) % 5)}"]

            page = st.selectbox('Select page : ',
                                restaurants,
                                index=None,
                                placeholder="Select here")

    if page != None:

        with col2:

            mini, maxi = int(page.split(" - ")[0]), int(page.split(" - ")[1])
            restaurant = st.radio('Restaurants : ',
                                   data[mini-1:maxi])
            
    if restaurant != None:

        payload = {"name":restaurant,
                   "n_data":5}
        response1 = requests.get(url1, json=payload)

        if response1.status_code == 200:
            result1 = response1.json()
        
        if result1 != None:
            st.write("Recommendation based on restaurant type")
            st.table(pd.DataFrame(result1))

        response2 = requests.get(url2, json=payload)

        if response2.status_code == 200:
            result2 = response2.json()
        
        if result2 != None:
            st.write("Recommendation based on restaurant cuisines")
            st.table(pd.DataFrame(result2))
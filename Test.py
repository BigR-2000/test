import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import json

 #Haal de whitelist van e-mailadressen en wachtwoorden op uit de secret
whitelist_credentials = {
    'marco.verheuge@kaagent.be': 'KaaGent_9000',
    'frederic.dupre@kaagent.be': 'KaaGent_9000',
    'remi.demesel@ugent.be': 'KaaGent_9000',
    'thomasmatton12@hotmail.com': 'KaaGent_9000'
}

#secrets = st.secrets["whitelist_credentials"]

# Vraag de gebruiker om in te loggen
user_email = st.text_input("Email adress:")
user_password = st.text_input("Password:", type="password")

# Controleer of de verstrekte inloggegevens overeenkomen met de whitelist
if user_email in whitelist_credentials:
    if user_password == whitelist_credentials[user_email]:
        st.success('Welcome')
        user_email = ""
        user_password = ""
        # Afronding vd dataframes
        def afronding(Dataframe):
            Dataframe.iloc[:, 2:8] = Dataframe.iloc[:, 2:8].round(0)
            Dataframe.iloc[:, 9:16] = Dataframe.iloc[:, 9:16].round(1)
            return Dataframe

        # Functie voor alle grafieken in de applicatie
        def Barplot(dataframe):
            selected_column = st.selectbox('Choose metric', dataframe.columns[3:16])

            plt.figure(figsize=(10,6))
            bars = plt.bar(dataframe['Position'], dataframe[selected_column])
            for bar in bars:
                yval = bar.get_height()
                #plt.text(bar.get_x() + bar.get_width() / 2, yval, ha= 'center', va='bottom')
                plt.text(bar.get_x() + bar.get_width() / 2, yval, str(yval), ha='center', va='bottom')
            if selected_column == 'Distance P90':
                y_min = 7000
                y_max = 14000
                plt.ylim(y_min, y_max)
            if selected_column == 'PSV-99':
                y_min = 20
                y_max = 40
                plt.ylim(y_min, y_max)
            plt.xlabel('Positie')
            plt.ylabel(selected_column)
            plt.title(f'{selected_column} per positie')
            st.pyplot(plt)

        def laatste_deel_na_spatie(naam):
            delen = naam.split()  # splits de naam op spaties
            return delen[-1]  # retourneert het laatste deel van de naam

        #functie voor wanneer files worden geupload ter vergelijking
        def compare(files):
            compare_prospects = pd.DataFrame()
            for file in files:
                prospect = pd.read_csv(file, encoding='latin1', sep=';')
                prospect.loc[prospect['Position'].isin(['LWB', 'RWB']), 'Position Group'] = 'Full Back'
                prospect.loc[prospect['Position'].isin(['CB', 'LCB', 'RCB']), 'Position Group'] = 'Central Defender'
                prospect.loc[prospect['Position'].isin(['AM', 'RM', 'LM', 'DM', 'RW', 'LW']), 'Position Group'] = 'Midfielder'
                prospect.loc[prospect['Position'].isin(['RW', 'LW']), 'Position Group'] = 'Winger'
                prospect.loc[prospect['Position'].isin(['CA', 'CF', 'LF', 'RF']), 'Position Group'] = 'Forward'
                dummy = prospect['Position Group']
                prospect.drop(columns=prospect.columns[1], inplace = True)
                prospect.drop(columns=prospect.columns[1], inplace = True)
                prospect.drop(columns=prospect.columns[-1], inplace = True)
                prospect.rename(columns={prospect.columns[0]: "Position", prospect.columns[1]: "Total Minutes Played"}, inplace=True)
                Prospect = prospect.groupby('Position').mean().reset_index()
                Prospect_sum = prospect.groupby('Position').sum().reset_index()
                Prospect['Total Minutes Played'] = Prospect_sum['Total Minutes Played']
                Prospect['Position Group'] = dummy
                Prospect.reset_index(drop=True, inplace=True)
                cols = list(Prospect.columns)
                Prospect = Prospect[[cols[0]] + [cols[-1]] + cols[1:15]]
                Prospect.reset_index(drop=True, inplace=True)
                Prospect = afronding(Prospect)
                #Prospect['Position'] = Prospect['Position'].apply(laatste_deel_na_spatie)              
                compare_prospects = pd.concat([compare_prospects, Prospect], axis=0)
            return compare_prospects

        #functie voor wanneer een bepaalde opstelling wordt aangeklikt    
        def formatie(dataframe):

            if options == '3-5-2':
                st.markdown('In total, 27 games have been recorded in the 3-5-2 formation.')
            elif options == '3-4-3':
                st.markdown('In total, 10 games have been recorded in the 3-4-3 formation.')
            else:
                st.markdown('In total, 4 games have been recorded in the 4-3-3 formation.')

            dataframe.drop(columns= dataframe.columns[0:3], inplace=True)
            dataframe.drop(columns= dataframe.columns[2:4], inplace=True)

            Per_Position_90 = dataframe.groupby('Position').mean()
            Sum_Per_Position_90 = dataframe.groupby('Position').sum()
            Per_Position_90['Total Minutes Played'] = Sum_Per_Position_90['Minutes Played']

            Per_Position_90 = Per_Position_90.reset_index()
            Per_Position_90.loc[Per_Position_90['Position'] == 'LW', 'Position'] = 'LWB'
            Per_Position_90.loc[Per_Position_90['Position'] == 'RW', 'Position'] = 'RWB'
            Per_Position_90.loc[Per_Position_90['Position'] == 'RM', 'Position'] = 'RCM'
            Per_Position_90.loc[Per_Position_90['Position'] == 'LM', 'Position'] = 'LCM'
            if options == '4-3-3':
                Per_Position_90.loc[Per_Position_90['Position'] == 'LWB', 'Position'] = 'LB'
                Per_Position_90.loc[Per_Position_90['Position'] == 'RWB', 'Position'] = 'RB'
            Per_Position_90.loc[Per_Position_90['Position'].isin(['LWB', 'RWB', 'LB', 'RB']), 'Position Group'] = 'Full Back'
            Per_Position_90.loc[Per_Position_90['Position'].isin(['CB', 'LCB', 'RCB']), 'Position Group'] = 'Central Defender'
            Per_Position_90.loc[Per_Position_90['Position'].isin(['AM', 'RM', 'LM', 'DM', 'RW', 'LW', 'RCM', 'LCM']), 'Position Group'] = 'Midfielder'
            Per_Position_90.loc[Per_Position_90['Position'].isin(['RW', 'LW']), 'Position Group'] = 'Winger'
            Per_Position_90.loc[Per_Position_90['Position'].isin(['CA', 'CF', 'LF', 'RF']), 'Position Group'] = 'Forward'

            cols = list(Per_Position_90.columns)
            Per_Position_90 = Per_Position_90[[cols[0]] + [cols[-1]] + [cols[-2]] + cols[2:15]]

            position_ranking_map =  {
            'RWB': 1, 'RB': 2, 'RCB': 3, 'CB': 4, 'LCB': 5, 'LWB': 6, 'LB': 7,
            'RW': 8, 'RCM': 9, 'LCM': 10, 'LW': 11, 'AM': 12,
            'RF': 13, 'CF': 14, 'LF': 15
            }
            Per_Position_90['Ranking'] = Per_Position_90['Position'].map(position_ranking_map)
            Per_Position_90.sort_values(by='Ranking', inplace = True)
            Per_Position_90.drop(columns=['Ranking'], inplace = True)

            Per_Position_90 = afronding(Per_Position_90)

            selected_role = st.sidebar.multiselect('Position Group', ['Forward', 'Winger', 'Midfielder', 'Full Back', 'Central Defender'])
            df_selected_role = Per_Position_90[(Per_Position_90['Position Group'].isin(selected_role))]

            if not selected_role:
                st.dataframe(Per_Position_90, hide_index = True)
                st.markdown("<h4>Visualization</h4>", unsafe_allow_html=True)
                Barplot(Per_Position_90)

            else:
                selected_position = st.sidebar.multiselect('Position', df_selected_role['Position'].unique())
                df_selected_position = df_selected_role[(df_selected_role['Position'].isin(selected_position))]
                if not selected_position:
                    df_selected_role.reset_index(drop=True, inplace=True)
                    df_selected_role = df_selected_role.rename_axis('Rank', axis=0)
                    df_selected_role.index = df_selected_role.index + 1
                    st.dataframe(df_selected_role, hide_index= True)
                    st.markdown("<h4>Visualization</h4>", unsafe_allow_html=True)
                    Barplot(df_selected_role)

                else:
                    df_selected_position.reset_index(drop=True, inplace=True)
                    df_selected_position = df_selected_position.rename_axis('Rank', axis=0)
                    df_selected_position.index = df_selected_position.index + 1
                    st.dataframe(df_selected_position, hide_index= True)
                    st.markdown("<h4>Compare with prospect(s)</h4>", unsafe_allow_html=True)
                    st.markdown('In this section, you can compare the stats of different prospects with the benchmarks of KAA Gent. To do this, export the player data from SkillCorner and upload the file below.')
                    st.write("**Export player data from SkillCorner with the following settings:**")
                    st.write("       - Ensure that **'P90'** is selected.")
                    st.write("       - In **General** settings, only **'Player'**, **'Position'** and **'Date'** should be selected.")
                    st.write("       - In **Metrics**, everything should be selected except **'M/min'**.")
                    uploaded_files = st.file_uploader('upload player file(s) here', accept_multiple_files=True)

                    if uploaded_files:
                        compare_prospects = compare(uploaded_files)
                        df_compare = pd.concat([df_selected_position, compare_prospects])
                        st.dataframe(df_compare, hide_index=True)
                        df_compare['Position'] = df_compare['Position'].apply(laatste_deel_na_spatie) 
                        Barplot(df_compare)

        # Hoofdpagina met informatie/ en de navigatiebar
        st.subheader('KAA Gent Physical Performance Benchmarking Tool')
        st.markdown('Within this tool, a benchmark of the average physical data of KAA Gent can be found. The data spans across the 23/24 season, excluding the playoffs and friendly matches. Here\'s what you can do:')      
        st.markdown("- View the average physical output for KAA Gent players, categorized by formation.")
        st.markdown("- Further filter by position within each formation.")
        st.markdown("- Compare the physical output using visualizations.")
        st.markdown("- Compare the physical output of KAA Gent players with prospects from other teams.")
        st.divider()
        st.write("")
        st.write("")
        st.markdown("<h4>Physical statistics by position</h4>", unsafe_allow_html=True)
        options = st.sidebar.radio('Formations', options=['3-5-2', '3-4-3', '4-3-3'])

        if options == '4-3-3':
            df = pd.read_csv("433__P90.csv", encoding='latin1', sep=';')
            formatie(df)
        if options == '3-5-2':
            df = pd.read_csv("352___P90.csv", encoding='latin1', sep=';')
            formatie(df)
        if options == '3-4-3':
            df = pd.read_csv("343P90.csv", encoding='latin1', sep=';')
            formatie(df)
    #else:
        #st.error("Incorrect password or email. Try again.")





    
    
    
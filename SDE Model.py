
# coding: utf-8

# In[405]:


import numpy as np
import pandas as pd
import math
import civis
import json
import datetime

lee = [948327, 947318, 948329] 


# In[406]:


# Get login credentials from secrets file
secrets = json.load(open('secrets.json'))
CIVIS_API_KEY = secrets['civis']['api_key']

# Setup API client
client = civis.APIClient(api_key=CIVIS_API_KEY)

# Import precinct data
to_drop = ['clinton_16', 'hubbell_18', 'clinton_hubbell_sum', 'reporting_multiplier','percent_of_statewide_vote']
sql = "SELECT * FROM analytics_ia.precinct_data"
precinct_data = civis.io.read_civis_sql(sql, "Warren for MA", use_pandas=True, client=client)
precinct_data.drop(to_drop, inplace=True, axis=1)

# Import first choice ID data
sql = "select van_precinct_id, survey_response_name, count(*) from analytics_ia.vansync_responses where mrr_all = 1 and survey_question_name = '1st Choice Caucus' group by 1,2"    
fc = civis.io.read_civis_sql(sql, "Warren for MA", use_pandas=True, client=client)
# Set dtype for columns to float
cols = fc.columns.drop('survey_response_name')
fc[cols] = fc[cols].astype(np.float32)
# Pivot on van_precinct_id
fc = fc.pivot(index='van_precinct_id', columns='survey_response_name', values='count')
# Reset dtype for columns to float
cols = first_choice.columns
fc[cols] = fc[cols].astype(np.float32)


# In[407]:


# Rename columns
precinct_data.rename(index=str, columns={"congressional_district": "Congressional District", 
                                    "precinct_id": "Precinct ID", 
                                    "county": "County",
                                    "precinct_code": "Precinct Code",
                                    "sos_precinct_name": "Sec. State Precinct Name",
                                    "delegates_to_county_conv": "Delegates to County Conv",
                                    "state_delegate_equivalence_sde": "State Delegate Equivalence (SDE)"}, inplace=True)


# ## Expected Turnout
# 
# To predict turnout we have a number of different models that we can use. In the cells below you can select a turnout model and tune the parameter for statewide expected turnout. 
# 
# ---
# Our different models are as follows:
# 
# 1. `exp_16` - models precinct level turnout with the same turnout numbers as 2016
# 2. `exp_08` - models precinct level turnout with the same turnout numbers as 2008
# 3. `exp_avg` - models precinct level turnout with the average of the precinct level turnout numbers from 2016 and 2008
# 4. `exp_percent_16` - models precinct level turnout using the percent of statewide vote per precicnt in 2016 and a parameter for statewide turnout (`expected_statewide_turnout`) that can be adjusted.
# 5. `exp_percent_08` - models precinct level turnout using the percent of statewide vote per precicnt in 2008 and a parameter for statewide turnout (`expected_statewide_turnout`) that can be adjusted.
# 6. `exp_percent_avg` - models precinct level turnout using the average of the percents of statewide vote per precicnt in 2016 and 2008, and a parameter for statewide turnout (`expected_statewide_turnout`) that can be adjusted.7.
# 7. `overall_avg` - models precinct level turnout using the average of `exp_16`, `exp_08`, `exp_percent_16`, and `exp_percent_08`.
# 
# By default `expected_statewide_turnout` is set to 300,000.
# 
# 
# 

# In[408]:


def exp_16 (row):
    return row['count16']

def exp_08 (row):
    return row['count08']

def exp_avg (row):
    return (exp_16(row) + exp_08(row)) / 2

def exp_percent_16 (row):
    return (row['count16'] / statewide_turnout_16) * expected_statewide_turnout

def exp_percent_08 (row):
    return (row['count08'] / statewide_turnout_08) * expected_statewide_turnout

def exp_percent_avg (row):
    return (exp_percent_16(row) + exp_percent_08(row)) / 2

def overall_avg (row):
    return (exp_16(row) + exp_08(row) + exp_percent_16(row) + exp_percent_08(row)) / 4


# In[409]:


caucus_history = pd.read_csv('caucus_history.csv', header = 0, dtype=np.float32)
df = pd.merge(precinct_data, caucus_history, left_on='Precinct ID', right_on='van_precinct_id')
statewide_turnout_16 = caucus_history['count16'].sum()
statewide_turnout_08 = caucus_history['count08'].sum()
df.set_index('Precinct ID', inplace=True)


# In[410]:


# Set the Turnout Model you want to use
turnout_model = overall_avg
# Set the expected statewide turnout if your model depends on it
expected_statewide_turnout = 300000

df['Expected Turnout'] = df.apply(turnout_model, axis=1)
columns = ['van_precinct_id', 'count16', 'count08']
df.drop(columns, inplace=True, axis=1)


# In[411]:


def viability_threshold(num_del):
    if num_del == 0:
        return 0.0
    elif num_del == 1:
        return 0.0
    elif num_del == 2:
        return 0.25
    elif num_del == 3:
        return 1 / 6
    else:
        return 0.15


# In[413]:


# Calculate SDE per person based on turnout model
df['SDE per Person'] = df.apply(lambda row : row['State Delegate Equivalence (SDE)'] / row['Expected Turnout'], axis=1)
# Assign viablity thresholds based on the number of County Convention delegates and the turnout model
df['Viability Threshold'] = df.apply(lambda row : math.ceil(row['Expected Turnout'] * viability_threshold(row['Delegates to County Conv'])), axis=1).astype(np.float32)


# In[414]:


# Add Committed Warren and Lean Warren from fc to new merged df
df = pd.merge(df, fc[['Committed Warren']], how="left", left_index=True, right_index=True)
df = pd.merge(df, fc[['Lean Warren']], how="left", left_index=True, right_index=True)
# Add Viability Threshold to fc
fc = pd.merge(fc, df[['Viability Threshold']], how='left', left_index=True, right_index=True)
fc.fillna(0, inplace=True)


# ## Viability
# 
# To predict viablity for EW we first predict how many caucus goers we expect to turnout for EW and then compare this number against the viability threshold calculated from our expected turnout.
# 
# To predict viability for other candidtes we assume if they have at least 70% of the viability threshold in a given precinct then that candidate will be viable.
# 
# ---
# We predict the number of caucus goers for EW by weighting the number of 'Committed Warren' and 'Lean Warren' IDs we have. We than assume a flake rate for the weighted sum. The variables `committed_warren_weight` and `lean_warren_weight` can be set to adjust the weights of this prediction. The variable `flake_rate` can be set to adjust the flake rate (Note, the flake rate is set as the percent of people who do show up).
# 
# By default, `committed_warren_weight` is set to `0.9`, `lean_warren_weight` is set to `0.5`, and `flake_rate` is set to 0.85.
# 
# For other candidates, the 70% estimation can be changed by adjusting the `viability_percent` variable.

# In[415]:


# Set the desired weights here
committed_warren_weight = 0.9
lean_warren_weight = 0.6
flake_rate = 0.85
viability_percent = 0.7


# In[416]:


# Calculate whether or not EW is viable for each precinct
df['Expected Warren Turnout'] = df.apply(lambda row: flake_rate * (row['Committed Warren'] * committed_warren_weight) + (row['Lean Warren'] * lean_warren_weight), axis=1)
df['Warren Viable'] = df.apply(lambda row: row['Viability Threshold'] <= row['Expected Warren Turnout'] and row['Expected Warren Turnout'] != 0, axis=1)


# In[418]:


# Calculate the number of other viable candidates in each precinct
to_drop = ['Committed Warren', 'Lean Warren', 'GOP', 'Other Dem', 'Undecided', 'Refused to say', 'Viability Threshold']
candidates = fc.columns.drop(to_drop)

def get_other_viable (row):
    num_viable = 0
    for candidate in candidates:
        if (row[candidate] >= viability_percent * row['Viability Threshold']) and (row[candidate] != 0):
            num_viable += 1
    return num_viable

fc['Other Viable Candidates'] = fc.apply(get_other_viable, axis=1)

# Calculate the total turnout across other viable candidates
def get_turnout (row):
    ID_turnout = 0
    viable_turnout = 0
    for candidate in candidates:
        ID_turnout += row[candidate]
        # If the candidate has IDs above the viablity threshold
        if (row[candidate]) >= row['Viability Threshold'] and (row[candidate] != 0):
            # Add the number of IDs to the expected ID turnout
            viable_turnout += row[candidate]
        # If the candidate has IDs above the viability percent 
        if (row[candidate] >= viability_percent * row['Viability Threshold']) and (row[candidate] != 0):
            # Add the viability threhold to the expected turnout
            viable_turnout += row['Viability Threshold']
    return ID_turnout, viable_turnout

# This is the raw turnout based on IDs
def get_ID_turnout (row):
    x, y = get_turnout (row)
    return x

# This is the adjusted turnout rounding up if a candidate has more than the viablity percent
# This only includes candidates we think will be viable
def get_viable_turnout (row):
    x, y = get_turnout (row)
    return y

fc['Partial ID Turnout'] = fc.apply(get_ID_turnout, axis=1)
fc['Other Candidates Viable Turnout'] = fc.apply(get_viable_turnout, axis=1)

df = pd.merge(df, fc[['Other Viable Candidates']], how='left', left_index=True, right_index=True)
df = pd.merge(df, fc[['Other Candidates Viable Turnout']], how='left', left_index=True, right_index=True)

# Calculate total ID turnout by adding ID turnout for other candidates to expected warren turnout
df = pd.merge(df, fc[['Partial ID Turnout']], how='left', left_index=True, right_index=True)
df['Total ID Turnout'] = df.apply(lambda row: row['Partial ID Turnout'] + row['Expected Warren Turnout'], axis=1)
df.fillna(0, inplace=True)


# In[419]:


# Calculate expected number of warren delegates based on exprected warren turnout

def expected_dels (row):
    et = row['Expected Turnout']
    ew = row['Expected Warren Turnout']
    oc = row['Other Candidates Viable Turnout']
    id_turnout = ew + oc
    num_del = row['Delegates to County Conv']
    
    # Return 0 if not viable
    if (not row['Warren Viable']):
        return 0
    
    exp_del = num_del * (ew) / max(et, id_turnout)
    if (exp_del % 1) >= 0.5:
        return math.ceil(exp_del)
    else:
        return math.floor(exp_del)

df['Expected Warren Delegates'] = df.apply(expected_dels, axis=1)    


# In[421]:


def distance_to_next_delegate (row):
    et = row['Expected Turnout']
    ew = row['Expected Warren Turnout']
    oc = row['Other Candidates Viable Turnout']
    num_other = row['Other Viable Candidates']
    id_turnout = ew + oc
    num_del = row['Delegates to County Conv']
    
    n = row['Expected Warren Delegates'] + 0.5
    
    # Lee County
    if num_del == 0:
        return None
    
    # One delegate precinct
    elif num_del == 1:
        # Distance to 50% + 1 of expected turnout or id_turnout (whichever is higher)
        return math.ceil(max(et, id_turnout) * (0.5)) + 1 - ew
    
    # More than one delegate precicnt
    else:
        
        # If we are not yet viable return the distance to viability
        if (not row['Warren Viable']):
            return math.ceil(row['Viability Threshold'] - ew)
        
        else:
        
            # When there are more viable candidates than there are delegates
            if (num_other + 1 > num_del):
                return -1

            # Calculate distance to next assuming expected turnout
            dist_to_15 = math.ceil(((n * et) - (num_del * ew)) / num_del)

            # If the total is still less than or equal to expected turnout
            if (id_turnout + dist_to_15 <= et):
                return dist_to_15

            # Otherwise calculate distance to next with id_turnout
            else:
                return math.ceil(((n * (ew + oc)) - (num_del * ew)) / (num_del - n))
            
df['Distance to Next Delegate'] = df.apply(distance_to_next_delegate, axis=1)      


# In[422]:


# Drop columns only used for internal calculations
df.drop(['Other Candidates Viable Turnout', 'Partial ID Turnout'], inplace=True, axis=1)
# Sort columns
df.sort_values(['Distance to Next Delegate', 'State Delegate Equivalence (SDE)'], inplace=True)


# In[423]:


df


# In[253]:


df.to_csv('SDE_model_' + date + '.csv')


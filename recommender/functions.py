import os
# import psutil
import time 
import json

import subprocess
import fnmatch
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import *
from PIL import ImageFilter,Image
from tkinter import filedialog, messagebox
from sklearn.cluster import AgglomerativeClustering
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from foodrec.settings import BASE_DIR
import openai
import requests

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL   = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
GROQ_API_KEY   = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL     = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CSE_ID  = os.getenv('GOOGLE_CSE_ID', '')

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
groq_client   = (
    openai.OpenAI(
        base_url='https://api.groq.com/openai/v1',
        api_key=GROQ_API_KEY,
    ) if GROQ_API_KEY else None
)

# Load master dataset (use food_master.csv if available, fallback to food.csv)
FOOD_DATA_PATH = os.path.join(BASE_DIR, "static/data/food_master.csv")
if not os.path.exists(FOOD_DATA_PATH):
    FOOD_DATA_PATH = os.path.join(BASE_DIR, "static/data/food.csv")
    print(f"Warning: Using fallback dataset {FOOD_DATA_PATH}")

data = pd.read_csv(FOOD_DATA_PATH)
Breakfastdata = data['Breakfast']
BreakfastdataNumpy = Breakfastdata.to_numpy()
                                   
Lunchdata = data['Lunch']
LunchdataNumpy = Lunchdata.to_numpy()
                                            
Dinnerdata = data['Dinner']
DinnerdataNumpy = Dinnerdata.to_numpy()
Food_itemsdata = data['Food_items']

# Global variable to store trained model and feature importance
_trained_models = {}
_feature_importance = {}


# Global variable to store trained model and feature importance
_trained_models = {}
_feature_importance = {}


def apply_clustering(data_array, n_clusters=5):
    """
    Apply Agglomerative Clustering with Ward linkage
    Replaces K-Means clustering throughout the codebase
    """
    X = np.array(data_array)
    
    # Use AgglomerativeClustering instead of K-Means
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage='ward'
    )
    
    labels = clustering.fit_predict(X)
    return labels


def train_with_smote(X_train, y_train, model_name='default'):
    """
    Train Random Forest with SMOTE oversampling
    Stores feature importance for later analysis
    """
    # Check if we have enough samples and classes for SMOTE
    unique_classes, class_counts = np.unique(y_train, return_counts=True)
    min_samples = class_counts.min()
    
    # SMOTE requires at least 2 samples per class
    if min_samples >= 2 and len(unique_classes) > 1:
        try:
            # Apply SMOTE to balance classes
            smote = SMOTE(random_state=42, k_neighbors=min(5, min_samples - 1))
            X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
            print(f"SMOTE applied: {len(X_train)} → {len(X_train_resampled)} samples")
        except Exception as e:
            print(f"SMOTE failed: {e}. Using original data.")
            X_train_resampled, y_train_resampled = X_train, y_train
    else:
        print(f"Skipping SMOTE: insufficient samples (min={min_samples})")
        X_train_resampled, y_train_resampled = X_train, y_train
    
    # Train Random Forest
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train_resampled, y_train_resampled)
    
    # Store model and feature importance
    _trained_models[model_name] = clf
    _feature_importance[model_name] = clf.feature_importances_
    
    return clf


def save_feature_importance():
    """
    Save feature importance to JSON file for frontend dashboard
    """
    if not _feature_importance:
        return
    
    insights = {}
    
    for model_name, importances in _feature_importance.items():
        # Feature names (based on nutrition_distribution.csv structure)
        feature_names = [
            'Calories', 'Fats', 'Proteins', 'Carbohydrates', 
            'Fibre', 'Iron', 'Calcium', 'Sodium', 'Potassium', 
            'VitaminD', 'Sugars', 'BMI_Class', 'Age_Class'
        ]
        
        # Trim feature names to match actual number of features
        feature_names = feature_names[:len(importances)]
        
        # Get top 5 features
        indices = np.argsort(importances)[::-1][:5]
        top_features = [
            {
                'feature': feature_names[i] if i < len(feature_names) else f'Feature_{i}',
                'importance': float(importances[i])
            }
            for i in indices
        ]
        
        insights[model_name] = {
            'top_features': top_features,
            'total_features': len(importances)
        }
    
    # Save to JSON
    output_path = os.path.join(BASE_DIR, 'static/data/model_insights.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"Feature importance saved to: {output_path}")


def Weight_Loss(age,weight,height):
    breakfastfoodseparated=[]
    Lunchfoodseparated=[]
    Dinnerfoodseparated=[]
        
    breakfastfoodseparatedID=[]
    LunchfoodseparatedID=[]
    DinnerfoodseparatedID=[]
        
    for i in range(len(Breakfastdata)):
        if BreakfastdataNumpy[i]==1:
            breakfastfoodseparated.append( Food_itemsdata[i] )
            breakfastfoodseparatedID.append(i)
        if LunchdataNumpy[i]==1:
            Lunchfoodseparated.append(Food_itemsdata[i])
            LunchfoodseparatedID.append(i)
        if DinnerdataNumpy[i]==1:
            Dinnerfoodseparated.append(Food_itemsdata[i])
            DinnerfoodseparatedID.append(i)
        
    # retrieving Lunch data rows by loc method |
    LunchfoodseparatedIDdata = data.iloc[LunchfoodseparatedID]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
    #print(LunchfoodseparatedIDdata)
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.iloc[Valapnd]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
    #print(LunchfoodseparatedIDdata)

    # retrieving Breafast data rows by loc method 
    breakfastfoodseparatedIDdata = data.iloc[breakfastfoodseparatedID]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.iloc[Valapnd]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
        
        
    # retrieving Dinner Data rows by loc method 
    DinnerfoodseparatedIDdata = data.iloc[DinnerfoodseparatedID]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.iloc[Valapnd]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
        
    #calculating BMI
    bmi = weight/((height/100)**2) 
    agewiseinp=0
        
    for lp in range (0,80,20):
        test_list=np.arange(lp,lp+20)
        for i in test_list: 
            if(i == age):
                tr=round(lp/20)  
                agecl=round(lp/20)    

        
    #conditions
    bmiinfo=""    
    if ( bmi < 16):
        bmiinfo="According to your BMI, you are Severely Underweight"
        clbmi=4
    elif ( bmi >= 16 and bmi < 18.5):
        bmiinfo="According to your BMI, you are Underweight"
        clbmi=3
    elif ( bmi >= 18.5 and bmi < 25):
        bmiinfo="According to your BMI, you are Healthy"
        clbmi=2
    elif ( bmi >= 25 and bmi < 30):
        bmiinfo="According to your BMI, you are Overweight"
        clbmi=1
    elif ( bmi >=30):
        bmiinfo="According to your BMI, you are Severely Overweight"
        clbmi=0

    #converting into numpy array
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.to_numpy()
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.to_numpy()
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.to_numpy()
    ti=(clbmi+agecl)/2
    
    ## Agglomerative Clustering Based Dinner Food
    Datacalorie=DinnerfoodseparatedIDdata[1:,1:len(DinnerfoodseparatedIDdata)]
    dnrlbl = apply_clustering(Datacalorie, n_clusters=5)

    ## Agglomerative Clustering Based Lunch Food
    Datacalorie=LunchfoodseparatedIDdata[1:,1:len(LunchfoodseparatedIDdata)]
    lnchlbl = apply_clustering(Datacalorie, n_clusters=5)
    
    ## Agglomerative Clustering Based Breakfast Food
    Datacalorie=breakfastfoodseparatedIDdata[1:,1:len(breakfastfoodseparatedIDdata)]
    brklbl = apply_clustering(Datacalorie, n_clusters=5)
    
    inp=[]
    ## Reading of the Dataet
    datafin=pd.read_csv(os.path.join(BASE_DIR ,"static/data/nutrition_distriution.csv"))

    ## train set
    dataTog=datafin.T
    bmicls=[0,1,2,3,4]
    agecls=[0,1,2,3,4]
    weightlosscat = dataTog.iloc[[1,2,7,8]]
    weightlosscat=weightlosscat.T
    weightgaincat= dataTog.iloc[[0,1,2,3,4,7,9,10]]
    weightgaincat=weightgaincat.T
    healthycat = dataTog.iloc[[1,2,3,4,6,7,9]]
    healthycat=healthycat.T
    weightlosscatDdata=weightlosscat.to_numpy()
    weightgaincatDdata=weightgaincat.to_numpy()
    healthycatDdata=healthycat.to_numpy()
    weightlosscat=weightlosscatDdata[1:,0:len(weightlosscatDdata)]
    weightgaincat=weightgaincatDdata[1:,0:len(weightgaincatDdata)]
    healthycat=healthycatDdata[1:,0:len(healthycatDdata)]
    
    
    weightlossfin=np.zeros((len(weightlosscat)*5,6),dtype=np.float32)
    weightgainfin=np.zeros((len(weightgaincat)*5,10),dtype=np.float32)
    healthycatfin=np.zeros((len(healthycat)*5,9),dtype=np.float32)
    t=0
    r=0
    s=0
    yt=[]
    yr=[]
    ys=[]
    for zz in range(5):
        for jj in range(len(weightlosscat)):
            valloc=list(weightlosscat[jj])
            valloc.append(bmicls[zz])
            valloc.append(agecls[zz])
            weightlossfin[t]=np.array(valloc)
            yt.append(brklbl[jj])
            t+=1
        # for jj in range(len(weightgaincat)):
        #     valloc=list(weightgaincat[jj])
        #     valloc.append(bmicls[zz])
        #     valloc.append(agecls[zz])
        #     weightgainfin[r]=np.array(valloc)
        #     yr.append(lnchlbl[jj])
        #     r+=1
        # for jj in range(len(healthycat)):
        #     valloc=list(healthycat[jj])
        #     valloc.append(bmicls[zz])
        #     valloc.append(agecls[zz])
        #     healthycatfin[s]=np.array(valloc)
        #     ys.append(dnrlbl[jj])
        #     s+=1

    
    X_test=np.zeros((len(weightlosscat),6),dtype=np.float32)

    print('####################')
    
    #randomforest with SMOTE
    for jj in range(len(weightlosscat)):
        valloc=list(weightlosscat[jj])
        valloc.append(agecl)
        valloc.append(clbmi)
        X_test[jj]=np.array(valloc)*ti
    
    
    
    X_train=weightlossfin# Features
    y_train=yt # Labels

    #Train Random Forest with SMOTE
    clf = train_with_smote(X_train, y_train, model_name='weight_loss')
    
    #print (X_test[1])
    X_test2=X_test
    y_pred=clf.predict(X_test)
    
    # Save feature importance
    save_feature_importance()
    
    returndata=[]
    print ('SUGGESTED FOOD ITEMS ::')
    for ii in range(len(y_pred)):
        print(y_pred)
        if y_pred[ii]==2:     #weightloss
            findata=breakfastfoodseparated[ii]
            returndata.append(breakfastfoodseparated[ii])
            # if int(veg)==1:
            #     datanv=['Chicken Burger']
        # for it in range(len(datanv)):
        #     if findata==datanv[it]:
        #         pass

    returndata.append(bmi)
    returndata.append(bmiinfo)
    return returndata




def Weight_Gain(age,weight,height):
    breakfastfoodseparated=[]
    Lunchfoodseparated=[]
    Dinnerfoodseparated=[]
        
    breakfastfoodseparatedID=[]
    LunchfoodseparatedID=[]
    DinnerfoodseparatedID=[]
        
    for i in range(len(Breakfastdata)):
        if BreakfastdataNumpy[i]==1:
            breakfastfoodseparated.append( Food_itemsdata[i] )
            breakfastfoodseparatedID.append(i)
        if LunchdataNumpy[i]==1:
            Lunchfoodseparated.append(Food_itemsdata[i])
            LunchfoodseparatedID.append(i)
        if DinnerdataNumpy[i]==1:
            Dinnerfoodseparated.append(Food_itemsdata[i])
            DinnerfoodseparatedID.append(i)
        
    # retrieving rows by loc method |
    LunchfoodseparatedIDdata = data.iloc[LunchfoodseparatedID]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.iloc[Valapnd]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
    
        
    # retrieving rows by loc method 
    breakfastfoodseparatedIDdata = data.iloc[breakfastfoodseparatedID]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.iloc[Valapnd]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
        
        
    # retrieving rows by loc method 
    DinnerfoodseparatedIDdata = data.iloc[DinnerfoodseparatedID]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.iloc[Valapnd]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
        
    #claculating BMI
    bmi = weight/((height/100)**2)        

    for lp in range (0,80,20):
        test_list=np.arange(lp,lp+20)
        for i in test_list: 
            if(i == age):
                tr=round(lp/20)  
                agecl=round(lp/20)

    bmiinfo=""    
    #conditions

    if ( bmi < 16):
        bmiinfo="according to your BMI, you are Severely Underweight"
        clbmi=4
    elif ( bmi >= 16 and bmi < 18.5):
        bmiinfo="according to your BMI, you are Underweight"
        clbmi=3
    elif ( bmi >= 18.5 and bmi < 25):
        bmiinfo="according to your BMI, you are Healthy"
        clbmi=2
    elif ( bmi >= 25 and bmi < 30):
        bmiinfo="according to your BMI, you are Overweight"
        clbmi=1
    elif ( bmi >=30):
        bmiinfo="according to your BMI, you are Severely Overweight"
        clbmi=0


    
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.to_numpy()
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.to_numpy()
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.to_numpy()
    ti=(clbmi+agecl)/2 
    
    
    ## Agglomerative Clustering Based Dinner Food
    Datacalorie=DinnerfoodseparatedIDdata[1:,1:len(DinnerfoodseparatedIDdata)]
    dnrlbl = apply_clustering(Datacalorie, n_clusters=5)
    
    ## Agglomerative Clustering Based Lunch Food
    Datacalorie=LunchfoodseparatedIDdata[1:,1:len(LunchfoodseparatedIDdata)]
    lnchlbl = apply_clustering(Datacalorie, n_clusters=5)

    ## Agglomerative Clustering Based Breakfast Food
    Datacalorie=breakfastfoodseparatedIDdata[1:,1:len(breakfastfoodseparatedIDdata)]
    brklbl = apply_clustering(Datacalorie, n_clusters=5)
    
    # plt.title("Predicted Low-High Weigted Calorie Foods")
    inp=[]
    ## Reading of the Dataet
    datafin=pd.read_csv(os.path.join(BASE_DIR ,"static/data/nutrition_distriution.csv"))
    # datafin.head(5)
    
    dataTog=datafin.T
    bmicls=[0,1,2,3,4]
    agecls=[0,1,2,3,4]
    weightlosscat = dataTog.iloc[[1,2,7,8]]
    weightlosscat=weightlosscat.T
    weightgaincat= dataTog.iloc[[0,1,2,3,4,7,9,10]]
    weightgaincat=weightgaincat.T
    healthycat = dataTog.iloc[[1,2,3,4,6,7,9]]
    healthycat=healthycat.T
    weightlosscatDdata=weightlosscat.to_numpy()
    weightgaincatDdata=weightgaincat.to_numpy()
    healthycatDdata=healthycat.to_numpy()
    weightlosscat=weightlosscatDdata[1:,0:len(weightlosscatDdata)]
    weightgaincat=weightgaincatDdata[1:,0:len(weightgaincatDdata)]
    healthycat=healthycatDdata[1:,0:len(healthycatDdata)]
    
    # in wg
    weightlossfin=np.zeros((len(weightlosscat)*5,6),dtype=np.float32)
    weightgainfin=np.zeros((len(weightgaincat)*5,10),dtype=np.float32)
    healthycatfin=np.zeros((len(healthycat)*5,9),dtype=np.float32)
    t=0
    r=0
    s=0
    yt=[]
    yr=[]
    ys=[]
    for zz in range(5):
        # for jj in range(len(weightlosscat)):
        #     valloc=list(weightlosscat[jj])
        #     valloc.append(bmicls[zz])
        #     valloc.append(agecls[zz])
        #     weightlossfin[t]=np.array(valloc)
        #     yt.append(brklbl[jj])
        #     t+=1
        for jj in range(len(weightgaincat)):
            valloc=list(weightgaincat[jj])
            #print (valloc)
            valloc.append(bmicls[zz])
            valloc.append(agecls[zz])
            weightgainfin[r]=np.array(valloc)
            yr.append(lnchlbl[jj])
            r+=1
        # for jj in range(len(healthycat)):
        #     valloc=list(healthycat[jj])
        #     valloc.append(bmicls[zz])
        #     valloc.append(agecls[zz])
        #     healthycatfin[s]=np.array(valloc)
        #     ys.append(dnrlbl[jj])
        #     s+=1

    
    X_test=np.zeros((len(weightgaincat),10),dtype=np.float32)

  
    # In[287]:
    for jj in range(len(weightgaincat)):
        valloc=list(weightgaincat[jj])
        valloc.append(agecl)
        valloc.append(clbmi)
        X_test[jj]=np.array(valloc)*ti
    
    
    X_train=weightgainfin# Features
    y_train=yr # Labels
    
    #Train Random Forest with SMOTE
    clf = train_with_smote(X_train, y_train, model_name='weight_gain')
    
    #print (X_test[1])
    X_test2=X_test
    y_pred=clf.predict(X_test)
    
    # Save feature importance
    save_feature_importance()
    
    
    returndata=[]
    print("Suggested Food Item :: ")
    for ii in range(len(y_pred)):
        if y_pred[ii]==1: 
            print("now here")     #weightgain
            findata=Lunchfoodseparated[ii]
            print("i am hereeeeee")
            returndata.append(Lunchfoodseparated[ii])
            # if int(veg)==1:
            #     datanv=['Chicken Burger']
        # for it in range(len(datanv)):
        #     if findata==datanv[it]:
        #         pass

    returndata.append(bmi)
    returndata.append(bmiinfo)
    return returndata                    

   



def Healthy(age,weight,height):
    breakfastfoodseparated=[]
    Lunchfoodseparated=[]
    Dinnerfoodseparated=[]
        
    breakfastfoodseparatedID=[]
    LunchfoodseparatedID=[]
    DinnerfoodseparatedID=[]
        
    for i in range(len(Breakfastdata)):
        if BreakfastdataNumpy[i]==1:
            breakfastfoodseparated.append( Food_itemsdata[i] )
            breakfastfoodseparatedID.append(i)
        if LunchdataNumpy[i]==1:
            Lunchfoodseparated.append(Food_itemsdata[i])
            LunchfoodseparatedID.append(i)
        if DinnerdataNumpy[i]==1:
            Dinnerfoodseparated.append(Food_itemsdata[i])
            DinnerfoodseparatedID.append(i)
        
    # retrieving rows by loc method |
    LunchfoodseparatedIDdata = data.iloc[LunchfoodseparatedID]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.iloc[Valapnd]
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.T
        
    # retrieving rows by loc method 
    breakfastfoodseparatedIDdata = data.iloc[breakfastfoodseparatedID]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.iloc[Valapnd]
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.T
        
        
    # retrieving rows by loc method 
    DinnerfoodseparatedIDdata = data.iloc[DinnerfoodseparatedID]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
    val=list(np.arange(5,15))
    Valapnd=[0]+val
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.iloc[Valapnd]
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.T
        
    
    bmi = weight/((height/100)**2) 
    agewiseinp=0
        
    for lp in range (0,80,20):
        test_list=np.arange(lp,lp+20)
        for i in test_list: 
            if(i == age):
                tr=round(lp/20)  
                agecl=round(lp/20)    

    bmiinfo=""    
    #conditions
    print("Your body mass index is: ", bmi)
    if ( bmi < 16):
        bmiinfo="according to your BMI, you are Severely Underweight"
        clbmi=4
    elif ( bmi >= 16 and bmi < 18.5):
        bmiinfo="according to your BMI, you are Underweight"
        clbmi=3
    elif ( bmi >= 18.5 and bmi < 25):
        bmiinfo="according to your BMI, you are Healthy"
        clbmi=2
    elif ( bmi >= 25 and bmi < 30):
        bmiinfo="according to your BMI, you are Overweight"
        clbmi=1
    elif ( bmi >=30):
        bmiinfo="according to your BMI, you are Severely Overweight"
        clbmi=0

    
    DinnerfoodseparatedIDdata=DinnerfoodseparatedIDdata.to_numpy()
    LunchfoodseparatedIDdata=LunchfoodseparatedIDdata.to_numpy()
    breakfastfoodseparatedIDdata=breakfastfoodseparatedIDdata.to_numpy()
    ti=(clbmi+agecl)/2
    
    

    ## Agglomerative Clustering Based Dinner Food
    Datacalorie=DinnerfoodseparatedIDdata[1:,1:len(DinnerfoodseparatedIDdata)]
    dnrlbl = apply_clustering(Datacalorie, n_clusters=5)
    
    ## Agglomerative Clustering Based Lunch Food
    Datacalorie=LunchfoodseparatedIDdata[1:,1:len(LunchfoodseparatedIDdata)]
    lnchlbl = apply_clustering(Datacalorie, n_clusters=5)
   
    ## Agglomerative Clustering Based Breakfast Food
    Datacalorie=breakfastfoodseparatedIDdata[1:,1:len(breakfastfoodseparatedIDdata)]
    brklbl = apply_clustering(Datacalorie, n_clusters=5)
    inp=[]
    ## Reading of the Dataet
    datafin=pd.read_csv(os.path.join(BASE_DIR ,"static/data/nutrition_distriution.csv"))
    datafin.head(5)
   
    dataTog=datafin.T
    bmicls=[0,1,2,3,4]
    agecls=[0,1,2,3,4]
    weightlosscat = dataTog.iloc[[1,2,7,8]]
    weightlosscat=weightlosscat.T
    weightgaincat= dataTog.iloc[[0,1,2,3,4,7,9,10]]
    weightgaincat=weightgaincat.T
    healthycat = dataTog.iloc[[1,2,3,4,6,7,9]]
    healthycat=healthycat.T
    weightlosscatDdata=weightlosscat.to_numpy()
    weightgaincatDdata=weightgaincat.to_numpy()
    healthycatDdata=healthycat.to_numpy()
    weightlosscat=weightlosscatDdata[1:,0:len(weightlosscatDdata)]
    weightgaincat=weightgaincatDdata[1:,0:len(weightgaincatDdata)]
    healthycat=healthycatDdata[1:,0:len(healthycatDdata)]
    
    
    weightlossfin=np.zeros((len(weightlosscat)*5,6),dtype=np.float32)
    weightgainfin=np.zeros((len(weightgaincat)*5,10),dtype=np.float32)
    healthycatfin=np.zeros((len(healthycat)*5,9),dtype=np.float32)
    t=0
    r=0
    s=0
    yt=[]
    yr=[]
    ys=[]
    for zz in range(5):
        for jj in range(len(weightlosscat)):
            valloc=list(weightlosscat[jj])
            valloc.append(bmicls[zz])
            valloc.append(agecls[zz])
            weightlossfin[t]=np.array(valloc)
            yt.append(brklbl[jj])
            t+=1
        for jj in range(len(weightgaincat)):
            valloc=list(weightgaincat[jj])
            #print (valloc)
            valloc.append(bmicls[zz])
            valloc.append(agecls[zz])
            weightgainfin[r]=np.array(valloc)
            yr.append(lnchlbl[jj])
            r+=1
        for jj in range(len(healthycat)):
            valloc=list(healthycat[jj])
            valloc.append(bmicls[zz])
            valloc.append(agecls[zz])
            healthycatfin[s]=np.array(valloc)
            ys.append(dnrlbl[jj])
            s+=1

    X_test=np.zeros((len(healthycat),9),dtype=np.float32)
    
    for jj in range(len(healthycat)):
        valloc=list(healthycat[jj])
        valloc.append(agecl)
        valloc.append(clbmi)
        X_test[jj]=np.array(valloc)*ti
    
    
    X_train=healthycatfin# Features
    y_train=ys # Labels
    
    #Train Random Forest with SMOTE
    clf = train_with_smote(X_train, y_train, model_name='healthy')
    
    X_test2=X_test
    y_pred=clf.predict(X_test)
   
    # Save feature importance
    save_feature_importance()
    
    print(f"DEBUG Healthy: y_pred unique values and counts: {np.unique(y_pred, return_counts=True)}")
    print(f"DEBUG Healthy: Total predictions: {len(y_pred)}")
    
    returndata=[]
    for ii in range(len(y_pred)):
        # Check for cluster 2 instead of 1 (based on actual predictions)
        if y_pred[ii]==2:
            returndata.append(Dinnerfoodseparated[ii])
            findata=Dinnerfoodseparated[ii]
            print(f"DEBUG Healthy: Added food at index {ii}: {Dinnerfoodseparated[ii]}")
            # if int(veg)==1:
                # datanv=['Chicken Burger']

    returndata.append(bmi)
    returndata.append(bmiinfo)

    return returndata

def calculate_bmr(weight, height, age, gender, activity_level, category=None):
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        return "Invalid gender"

    activity_factor = 1.2  # default for Very Light activity level

    if activity_level == "Light":
        activity_factor = 1.375
    elif activity_level == "Moderate":
        activity_factor = 1.55
    elif activity_level == "Heavy":
        activity_factor = 1.725
    elif activity_level == "Very Heavy":
        activity_factor = 1.9

    # if category == "Athlete":
    #     activity_factor = 1.9
    # elif category == "Weight Lifter":
    #     activity_factor = 1.725
    # elif category == "Body Builder":
    #     activity_factor = 1.9
    # elif category == "Pregnant":
    #     activity_factor = 1.375

    bmr *= activity_factor

    return bmr

# ──────────────────────────────────────────────────────────────────
# Nutrition Knowledge Base  (rule-based fallback — no API key needed)
# ──────────────────────────────────────────────────────────────────
_KB = [
    {
        'keywords': ['bmi', 'body mass index'],
        'answer': (
            'BMI (Body Mass Index) is calculated as weight(kg) ÷ height(m)².\n\n'
            'Categories:\n'
            '• Below 18.5 → Underweight\n'
            '• 18.5 – 24.9 → Healthy weight\n'
            '• 25.0 – 29.9 → Overweight\n'
            '• 30.0 and above → Obese\n\n'
            'BMI is a screening tool, not a diagnosis. Muscle mass, age, and ethnicity can affect its accuracy.'
        ),
    },
    {
        'keywords': ['bmr', 'basal metabolic rate', 'metabolism at rest'],
        'answer': (
            'BMR (Basal Metabolic Rate) is the number of calories your body burns at complete rest to maintain '
            'basic functions like breathing, circulation, and cell production.\n\n'
            'Mifflin-St Jeor formula:\n'
            '• Men:   (10 × weight kg) + (6.25 × height cm) − (5 × age) + 5\n'
            '• Women: (10 × weight kg) + (6.25 × height cm) − (5 × age) − 161\n\n'
            'Multiply your BMR by an activity factor (1.2–1.9) to get Total Daily Energy Expenditure (TDEE).'
        ),
    },
    {
        'keywords': ['tdee', 'total daily energy', 'maintenance calories', 'how many calories do i need'],
        'answer': (
            'TDEE (Total Daily Energy Expenditure) is your BMR multiplied by an activity factor:\n\n'
            '• Sedentary (little/no exercise): BMR × 1.2\n'
            '• Lightly active (1–3 days/week): BMR × 1.375\n'
            '• Moderately active (3–5 days/week): BMR × 1.55\n'
            '• Very active (6–7 days/week): BMR × 1.725\n'
            '• Extra active (physical job + exercise): BMR × 1.9\n\n'
            'Eating at TDEE maintains your current weight.'
        ),
    },
    {
        'keywords': ['weight loss', 'lose weight', 'calorie deficit', 'fat loss', 'reduce weight'],
        'answer': (
            'For healthy weight loss, aim for a calorie deficit of 300–750 kcal/day below your TDEE.\n\n'
            'Key strategies:\n'
            '• Eat high-protein foods (eggs, chicken, lentils, paneer) to preserve muscle and stay full.\n'
            '• Include plenty of vegetables and fiber to manage hunger with fewer calories.\n'
            '• Reduce ultra-processed foods, sugary drinks, and refined carbs.\n'
            '• Stay hydrated — thirst is often mistaken for hunger.\n'
            '• Aim for 0.5–1 kg of fat loss per week; faster than this risks muscle loss.\n'
            '• Strength training preserves muscle mass during weight loss.'
        ),
    },
    {
        'keywords': ['weight gain', 'gain weight', 'calorie surplus', 'bulk', 'underweight'],
        'answer': (
            'For lean muscle gain, eat 300–500 kcal above your TDEE.\n\n'
            'Key tips:\n'
            '• Prioritise protein: 1.6–2.2 g per kg of body weight daily (chicken, eggs, dairy, legumes).\n'
            '• Eat calorie-dense whole foods: nuts, avocado, bananas, whole milk, oats, rice.\n'
            '• Resistance (weight) training 3–5 days/week stimulates muscle growth.\n'
            '• Get 7–9 hours of sleep — muscle is built during recovery.\n'
            '• Eat frequently (every 3–4 hours) if you struggle to hit calorie targets.'
        ),
    },
    {
        'keywords': ['protein', 'how much protein', 'protein intake', 'protein foods', 'high protein'],
        'answer': (
            'Protein is essential for muscle repair, immune function, and satiety.\n\n'
            'Recommended intake:\n'
            '• General health: 0.8 g per kg body weight\n'
            '• Active adults / muscle gain: 1.6–2.2 g per kg\n'
            '• Weight loss (preserve muscle): 1.2–1.6 g per kg\n\n'
            'Best protein sources:\n'
            '• Animal: eggs, chicken breast, fish, paneer, Greek yogurt, milk\n'
            '• Plant: lentils (dal), chickpeas, rajma, tofu, soy, quinoa, sprouts\n\n'
            '1 egg ≈ 6 g protein | 100 g chicken ≈ 31 g | 100 g lentils (cooked) ≈ 9 g'
        ),
    },
    {
        'keywords': ['carbohydrate', 'carbs', 'carb', 'complex carbs', 'simple carbs', 'sugar carb'],
        'answer': (
            'Carbohydrates are your body\'s primary energy source.\n\n'
            'Types:\n'
            '• Complex carbs (slow-digesting, healthy): oats, brown rice, whole wheat, sweet potato, legumes\n'
            '• Simple/refined carbs (fast-digesting, limit these): white bread, white rice, biscuits, sweets\n\n'
            'Aim for 45–65% of daily calories from carbs, focusing on complex sources rich in fiber.\n'
            'For weight loss, reducing refined carbs significantly helps manage blood sugar and hunger.'
        ),
    },
    {
        'keywords': ['fat', 'healthy fat', 'good fat', 'bad fat', 'saturated', 'unsaturated', 'omega'],
        'answer': (
            'Not all fats are equal.\n\n'
            'Healthy fats (eat these):\n'
            '• Monounsaturated: olive oil, avocado, peanuts, almonds\n'
            '• Polyunsaturated / Omega-3: salmon, walnuts, flaxseeds, chia seeds\n\n'
            'Limit these:\n'
            '• Saturated fats: ghee, butter, red meat (in moderation is fine)\n'
            '• Trans fats: margarine, fried fast food, packaged baked goods — avoid entirely\n\n'
            'Fat should make up 20–35% of daily calories. It supports hormone production and vitamin absorption.'
        ),
    },
    {
        'keywords': ['fiber', 'fibre', 'roughage', 'digestive', 'constipation'],
        'answer': (
            'Dietary fiber aids digestion, controls blood sugar, lowers cholesterol, and keeps you full.\n\n'
            'Daily target: 25 g (women) / 38 g (men)\n\n'
            'Great fiber sources:\n'
            '• Vegetables: broccoli, carrots, beans, peas, spinach\n'
            '• Fruits: apple, pear, guava, banana, berries\n'
            '• Grains: oats, whole wheat, brown rice, barley\n'
            '• Legumes: lentils, rajma, chana, moong dal\n\n'
            'Increase fiber intake gradually and drink plenty of water to avoid bloating.'
        ),
    },
    {
        'keywords': ['balanced diet', 'healthy diet', 'what should i eat', 'nutrition tips', 'healthy eating'],
        'answer': (
            'A balanced diet includes all macronutrients and micronutrients in the right proportions.\n\n'
            'The plate model:\n'
            '• ½ plate: non-starchy vegetables (leafy greens, salad, sabzi)\n'
            '• ¼ plate: lean protein (dal, paneer, chicken, eggs, fish)\n'
            '• ¼ plate: complex carbohydrates (rice, roti, oats)\n'
            '• A small amount of healthy fat (olive oil, nuts, seeds)\n\n'
            'Key habits:\n'
            '• Eat 3 main meals + 1–2 small snacks\n'
            '• Cook at home when possible\n'
            '• Minimise fried, processed, and packaged foods\n'
            '• Drink 8–10 glasses of water daily\n'
            '• Include seasonal fruits and vegetables'
        ),
    },
    {
        'keywords': ['intermittent fasting', 'if', '16:8', '16 8', 'fasting diet', 'time restricted eating'],
        'answer': (
            'Intermittent fasting (IF) cycles between eating and fasting periods.\n\n'
            'Popular methods:\n'
            '• 16:8 — Fast 16 hours, eat within an 8-hour window (e.g., 12 pm – 8 pm). Most common.\n'
            '• 5:2 — Eat normally 5 days; restrict to 500–600 kcal on 2 non-consecutive days.\n'
            '• Alternate Day Fasting — Alternate between normal eating and fasted/restricted days.\n\n'
            'Benefits: may aid weight loss, improve insulin sensitivity, and simplify meal planning.\n'
            'Caution: not suitable for pregnant women, people with diabetes (type 1), or a history of eating disorders. Consult a doctor first.'
        ),
    },
    {
        'keywords': ['keto', 'ketogenic', 'low carb', 'ketosis'],
        'answer': (
            'The ketogenic (keto) diet is a very-low-carb, high-fat diet that shifts your body into ketosis '
            '— burning fat for fuel instead of carbs.\n\n'
            'Typical macros: 70–75% fat | 20–25% protein | 5% carbs (<50 g/day)\n\n'
            'Allowed: meat, eggs, fish, cheese, paneer, nuts, avocado, non-starchy vegetables\n'
            'Avoided: bread, rice, roti, sugar, fruit, legumes\n\n'
            'Evidence shows keto can be effective short-term for weight loss and blood sugar control. '
            'Long-term effects and sustainability vary. It\'s restrictive and may not suit everyone.'
        ),
    },
    {
        'keywords': ['mediterranean', 'mediterranean diet'],
        'answer': (
            'The Mediterranean diet is consistently ranked one of the healthiest diets in the world.\n\n'
            'Core principles:\n'
            '• Abundant: vegetables, fruits, whole grains, legumes, nuts, olive oil\n'
            '• Moderate: fish (2+ times/week), poultry, dairy, eggs\n'
            '• Rare: red meat and sweets\n'
            '• Primary fat source: extra-virgin olive oil\n\n'
            'Benefits: reduced risk of heart disease, diabetes, cognitive decline, and obesity. '
            'It\'s an easy-to-follow, sustainable long-term eating pattern.'
        ),
    },
    {
        'keywords': ['vegetarian', 'vegan', 'plant based', 'plant-based', 'no meat'],
        'answer': (
            'Well-planned vegetarian and vegan diets can meet all nutritional needs.\n\n'
            'Key nutrients to watch:\n'
            '• Protein: dal, rajma, chana, soy, tofu, paneer (dairy for lacto-veg), seeds\n'
            '• Vitamin B12: deficient in plant foods — supplement or eat fortified foods\n'
            '• Iron: spinach, legumes, seeds (eat with vitamin C for better absorption)\n'
            '• Zinc: legumes, nuts, seeds, whole grains\n'
            '• Omega-3: flaxseeds, chia seeds, walnuts\n'
            '• Calcium: dairy (lacto-veg), fortified plant milk, sesame seeds, ragi\n'
            '• Vitamin D: sunlight + fortified foods or supplement'
        ),
    },
    {
        'keywords': ['breakfast', 'morning meal', 'skip breakfast', 'first meal'],
        'answer': (
            'Breakfast breaks the overnight fast and can kickstart your metabolism.\n\n'
            'Healthy options:\n'
            '• Eggs (boiled, scrambled, or omelette) — high protein\n'
            '• Poha, upma, or idli with sambar — balanced carbs + protein\n'
            '• Oats with fruit and nuts — fiber-rich\n'
            '• Greek yogurt with banana — protein + potassium\n'
            '• Whole wheat toast with peanut butter\n\n'
            'Skipping breakfast is not harmful for everyone — some people thrive with IF. '
            'The key is total daily nutrition, not meal timing alone.'
        ),
    },
    {
        'keywords': ['snack', 'snacks', 'healthy snack', 'between meals', 'hunger'],
        'answer': (
            'Healthy snack ideas (100–200 kcal):\n\n'
            '• A handful of mixed nuts (almonds, walnuts, cashews)\n'
            '• Apple or banana with a tablespoon of peanut butter\n'
            '• Roasted chana or makhana\n'
            '• Greek yogurt / dahi\n'
            '• Boiled egg\n'
            '• Hummus with cucumber or carrot sticks\n'
            '• A small bowl of fruit salad\n'
            '• Whole grain crackers with paneer\n\n'
            'Avoid: biscuits, chips, namkeen, biscuits, and sugary drinks between meals — they spike blood sugar and lead to energy crashes.'
        ),
    },
    {
        'keywords': ['water', 'hydration', 'how much water', 'drink water'],
        'answer': (
            'Staying hydrated is essential for every bodily function.\n\n'
            'General recommendation: 8–10 glasses (2–3 litres) of water per day.\n\n'
            'Increase intake if:\n'
            '• You exercise or sweat a lot\n'
            '• The weather is hot and humid\n'
            '• You eat a high-protein or high-fiber diet\n\n'
            'Hydration tips:\n'
            '• Start your day with a glass of water\n'
            '• Drink a glass before each meal\n'
            '• Carry a water bottle\n'
            '• Eat water-rich foods: cucumber, watermelon, oranges, tomatoes\n'
            '• Urine should be pale yellow — dark yellow = dehydrated'
        ),
    },
    {
        'keywords': ['sugar', 'added sugar', 'sweets', 'reduce sugar', 'sweet', 'candy'],
        'answer': (
            'Excess added sugar is linked to obesity, type 2 diabetes, heart disease, and dental decay.\n\n'
            'WHO recommends: less than 10% of daily calories from added sugars (about 50 g/day for a 2,000 kcal diet), ideally <5%.\n\n'
            'Common hidden sugar sources: soft drinks, packaged juices, flavoured yogurt, biscuits, ketchup, cereals.\n\n'
            'Tips to cut sugar:\n'
            '• Drink water, buttermilk, or plain chai instead of sugary drinks\n'
            '• Eat whole fruit instead of fruit juice\n'
            '• Read food labels — look for "sugar", "high-fructose corn syrup", "maltose", etc.\n'
            '• Replace dessert with naturally sweet foods: dates, figs, raisins (in moderation)'
        ),
    },
    {
        'keywords': ['sodium', 'salt', 'blood pressure', 'reduce salt'],
        'answer': (
            'High sodium intake raises blood pressure and increases risk of heart disease and stroke.\n\n'
            'WHO limit: less than 5 g of salt (2,000 mg sodium) per day.\n\n'
            'High-sodium foods to limit: pickles, papad, processed meats, instant noodles, namkeen, sauces.\n\n'
            'Reduce salt by:\n'
            '• Cooking with herbs, lemon, and spices instead of extra salt\n'
            '• Rinsing canned legumes before use\n'
            '• Choosing "low-sodium" versions of packaged foods\n'
            '• Eating more potassium-rich foods (banana, sweet potato, spinach) to counter sodium effects'
        ),
    },
    {
        'keywords': ['vitamin', 'mineral', 'micronutrient', 'supplement', 'deficiency'],
        'answer': (
            'Key vitamins and minerals and their food sources:\n\n'
            '• Vitamin A: carrots, sweet potato, mango, spinach — eye health\n'
            '• Vitamin C: amla, lemon, orange, guava — immunity, iron absorption\n'
            '• Vitamin D: sunlight, fortified milk, fatty fish — bone health, immunity\n'
            '• Vitamin B12: eggs, dairy, meat (vegans must supplement)\n'
            '• Iron: spinach, dal, rajma, jaggery — energy, blood health\n'
            '• Calcium: milk, paneer, ragi, sesame — bones and teeth\n'
            '• Zinc: nuts, seeds, legumes — immunity, wound healing\n'
            '• Magnesium: nuts, leafy greens, whole grains — muscle function, sleep\n\n'
            'A varied whole-food diet usually covers your needs. Supplements are helpful when dietary intake falls short.'
        ),
    },
    {
        'keywords': ['egg', 'eggs', 'are eggs healthy', 'egg nutrition'],
        'answer': (
            'Eggs are one of the most nutritious foods available.\n\n'
            '1 large egg contains:\n'
            '• ~75 kcal | 6 g protein | 5 g fat | 0 g carbs\n'
            '• Vitamin D, B12, choline, selenium, and lutein/zeaxanthin (eye health)\n\n'
            'The yolk contains most of the nutrients. Only people with a specific medical condition need to '
            'strictly limit dietary cholesterol. For healthy individuals, up to 2–3 whole eggs/day is safe.\n\n'
            'Egg whites alone are a low-fat, high-protein option (3 g protein per white, ~17 kcal).'
        ),
    },
    {
        'keywords': ['rice', 'brown rice', 'white rice', 'roti', 'chapati', 'wheat'],
        'answer': (
            'Rice vs Roti comparison:\n\n'
            'White rice (1 cup cooked ≈ 200 kcal):\n'
            '• Easy to digest, low in fiber, moderate GI\n'
            '• Good post-workout due to fast carb absorption\n\n'
            'Brown rice (1 cup cooked ≈ 215 kcal):\n'
            '• More fiber, vitamins, and minerals than white rice\n'
            '• Lower glycemic response — better blood sugar control\n\n'
            'Whole wheat roti (1 medium ≈ 80 kcal):\n'
            '• Good source of fiber and B-vitamins\n'
            '• Portion-controllable; can be made with added vegetables\n\n'
            'Both rice and roti are healthy in appropriate portions. The key is what you eat with them (dal, sabzi, protein).'
        ),
    },
    {
        'keywords': ['paneer', 'cottage cheese', 'dairy', 'milk protein'],
        'answer': (
            'Paneer (Indian cottage cheese) is an excellent protein source for vegetarians.\n\n'
            '100 g paneer contains:\n'
            '• ~265 kcal | 18 g protein | 20 g fat | 3 g carbs\n\n'
            'It is rich in calcium and casein protein (slow-digesting, great for satiety).\n'
            'For lower fat, choose low-fat paneer or tofu.\n\n'
            'Best consumed grilled, added to dal, or in sabzi — avoid deep-frying to keep it healthy.'
        ),
    },
    {
        'keywords': ['dal', 'lentil', 'legume', 'pulse', 'rajma', 'chana', 'chickpea', 'moong'],
        'answer': (
            'Dals and legumes are nutritional powerhouses — affordable, protein-rich, and fiber-dense.\n\n'
            'Per 100 g cooked dal (approx):\n'
            '• 110–130 kcal | 7–9 g protein | 20 g carbs | 6–8 g fiber\n\n'
            'Top options:\n'
            '• Moong dal: lighter, high protein, easy to digest — great for weight loss\n'
            '• Masoor dal: high iron and protein\n'
            '• Rajma / Chana: high fiber, complex carbs, sustained energy\n\n'
            'Eat dal daily if possible — pair with rice or roti and a vegetable for a complete meal.'
        ),
    },
    {
        'keywords': ['fruit', 'fruits', 'banana', 'apple', 'mango', 'which fruit'],
        'answer': (
            'Fruits provide vitamins, minerals, antioxidants, and fiber.\n\n'
            'High-nutrient choices:\n'
            '• Banana: energy, potassium, vitamin B6 — great pre-workout\n'
            '• Apple: fiber, vitamin C, antioxidants — good for digestion\n'
            '• Guava: very high vitamin C, fiber, low GI\n'
            '• Papaya: digestive enzymes, vitamin C, beta-carotene\n'
            '• Berries (strawberry, blueberry): low calorie, high antioxidants\n'
            '• Watermelon: hydrating, low calorie\n\n'
            'Eat 2–3 servings of fruit daily. Whole fruit is far superior to fruit juice — it retains fiber '
            'and doesn\'t spike blood sugar as sharply.'
        ),
    },
    {
        'keywords': ['vegetable', 'veggies', 'green vegetable', 'leafy', 'spinach', 'broccoli'],
        'answer': (
            'Vegetables are the foundation of any healthy diet — eat them generously.\n\n'
            'Top choices:\n'
            '• Spinach / Palak: iron, magnesium, vitamin K and A\n'
            '• Broccoli: vitamin C, fiber, cancer-protective compounds\n'
            '• Carrot: beta-carotene (vitamin A precursor), fiber\n'
            '• Sweet potato: complex carbs, vitamin A, potassium\n'
            '• Tomato: lycopene (antioxidant), vitamin C\n'
            '• Cucumber: very low calorie, hydrating\n'
            '• Methi (fenugreek): blood sugar regulation, iron\n\n'
            'Aim for half your plate at every meal to be non-starchy vegetables.'
        ),
    },
    {
        'keywords': ['calorie', 'calories', 'how many calories', 'daily calories', 'calories per day'],
        'answer': (
            'Calorie needs vary by age, gender, height, weight, and activity level.\n\n'
            'Rough general averages:\n'
            '• Sedentary adult women: 1,600–2,000 kcal/day\n'
            '• Sedentary adult men: 2,000–2,600 kcal/day\n'
            '• Active adults (exercising 4–5 days/week): add 300–500 kcal\n\n'
            'Use the EatRight diet planner to calculate YOUR personalised calorie target based on '
            'age, weight, height, gender, and activity level.\n\n'
            'Minimum safe intake: 1,200 kcal/day (women) and 1,500 kcal/day (men) — going below this '
            'slows metabolism and risks nutrient deficiency.'
        ),
    },
    {
        'keywords': ['diabetes', 'blood sugar', 'insulin', 'glycemic', 'diabetic diet'],
        'answer': (
            'For type 2 diabetes management through diet:\n\n'
            '• Choose low-GI foods: oats, lentils, most vegetables, whole grains\n'
            '• Avoid: white bread, white rice (in large portions), sugary drinks, sweets, refined flour\n'
            '• Eat regular small meals to stabilise blood sugar\n'
            '• Prioritise protein and fiber at every meal to slow glucose absorption\n'
            '• Limit fruit juice; eat whole fruit in moderation\n'
            '• Bitter gourd (karela), fenugreek seeds, and cinnamon have some evidence for modest blood sugar reduction\n\n'
            'Work with a registered dietitian for a personalised diabetes meal plan.'
        ),
    },
    {
        'keywords': ['cholesterol', 'ldl', 'hdl', 'heart health', 'cardiac', 'heart disease'],
        'answer': (
            'Diet plays a major role in managing cholesterol.\n\n'
            'To lower LDL ("bad") cholesterol:\n'
            '• Increase soluble fiber: oats, barley, apple, flaxseeds, legumes\n'
            '• Replace saturated fats (butter, ghee) with unsaturated (olive oil, mustard oil)\n'
            '• Eat fatty fish (salmon, mackerel) or walnuts for omega-3s\n'
            '• Avoid trans fats entirely: vanaspati, margarine, packaged snacks\n\n'
            'To raise HDL ("good") cholesterol:\n'
            '• Exercise regularly\n'
            '• Eat avocado, olive oil, nuts\n'
            '• Quit smoking\n\n'
            'The Mediterranean diet pattern has the strongest evidence for heart health.'
        ),
    },
    {
        'keywords': ['sleep', 'rest', 'insomnia', 'sleep and diet', 'sleep and weight'],
        'answer': (
            'Poor sleep significantly impacts diet and weight:\n\n'
            '• Sleep deprivation raises ghrelin (hunger hormone) and lowers leptin (fullness hormone) — '
            'increasing cravings for high-calorie foods by up to 45%.\n'
            '• Lack of sleep reduces insulin sensitivity, promoting fat storage.\n'
            '• Aim for 7–9 hours of quality sleep per night.\n\n'
            'Foods that support better sleep:\n'
            '• Milk (warm) — contains tryptophan\n'
            '• Banana — magnesium and tryptophan\n'
            '• Almonds — magnesium\n'
            '• Chamomile tea\n'
            '• Cherries — natural melatonin source\n\n'
            'Avoid caffeine after 2 pm and heavy meals within 2 hours of bedtime.'
        ),
    },
    {
        'keywords': ['workout', 'exercise diet', 'pre workout', 'post workout', 'gym food', 'before exercise', 'after exercise'],
        'answer': (
            'Fuelling exercise correctly improves performance and recovery.\n\n'
            'Pre-workout (1–2 hours before):\n'
            '• Carbs + moderate protein: banana with peanut butter, oats with milk, whole wheat toast with eggs\n'
            '• Stay hydrated\n\n'
            'Post-workout (within 30–60 minutes after):\n'
            '• Protein + carbs: chicken with rice, eggs with toast, protein shake with banana, paneer with roti, dal rice\n'
            '• Protein helps muscle repair; carbs replenish glycogen stores\n\n'
            'For weight loss during training:\n'
            '• Eat in a slight deficit but never skip protein\n'
            '• Protein target: 1.6–2.2 g per kg body weight'
        ),
    },
    {
        'keywords': ['gut', 'probiotics', 'prebiotics', 'microbiome', 'digestive health', 'bloating', 'stomach'],
        'answer': (
            'A healthy gut microbiome supports immunity, digestion, mood, and metabolism.\n\n'
            'Probiotic foods (introduce beneficial bacteria):\n'
            '• Dahi (yogurt), chaas (buttermilk), idli, dosa, kanji, kombucha, kimchi\n\n'
            'Prebiotic foods (feed good bacteria):\n'
            '• Garlic, onions, bananas, oats, flaxseeds, asparagus\n\n'
            'Habits for gut health:\n'
            '• Eat a diverse range of plant foods\n'
            '• Include fiber daily (25–38 g)\n'
            '• Limit antibiotics to when needed\n'
            '• Reduce processed food and alcohol\n'
            '• Manage stress — the gut-brain axis is bidirectional'
        ),
    },
    {
        'keywords': ['anti-inflammatory', 'inflammation', 'arthritis', 'joint pain'],
        'answer': (
            'Chronic inflammation is linked to heart disease, diabetes, arthritis, and cancer.\n\n'
            'Anti-inflammatory foods to eat more of:\n'
            '• Fatty fish (omega-3s): salmon, sardines, mackerel\n'
            '• Berries and dark fruits (polyphenols)\n'
            '• Olive oil (oleocanthal has anti-inflammatory properties)\n'
            '• Turmeric (curcumin) — add to milk, curries, soups\n'
            '• Ginger — tea, cooking\n'
            '• Leafy greens: spinach, kale, methi\n'
            '• Nuts: walnuts, almonds\n\n'
            'Pro-inflammatory foods to avoid:\n'
            '• Refined carbs, fried food, processed meat, margarine, excess alcohol, sugary drinks'
        ),
    },
    {
        'keywords': ['meal plan', 'meal planning', 'weekly plan', 'diet plan example', 'what to eat daily'],
        'answer': (
            'Sample balanced daily meal plan (approx 1,800–2,000 kcal):\n\n'
            'Breakfast (400 kcal): 3-egg omelette with vegetables + 2 slices whole wheat toast + 1 fruit\n\n'
            'Mid-morning snack (150 kcal): Handful of almonds + 1 banana\n\n'
            'Lunch (600 kcal): 1 cup dal + 2 rotis (or 1 cup rice) + 1 serving sabzi + raita\n\n'
            'Evening snack (150 kcal): Roasted chana or dahi\n\n'
            'Dinner (500 kcal): Grilled protein (chicken/paneer/fish) + 1 cup rice/roti + large vegetable salad\n\n'
            'Use the EatRight diet planner to get a personalised ML-powered plan based on your goals!'
        ),
    },
    {
        'keywords': ['obesity', 'overweight', 'fat', 'obese'],
        'answer': (
            'Obesity (BMI ≥ 30) increases risk of type 2 diabetes, hypertension, heart disease, sleep apnea, '
            'and certain cancers.\n\n'
            'Evidence-based approach:\n'
            '• Create a calorie deficit: 500–750 kcal/day below TDEE for 0.5–0.75 kg/week loss\n'
            '• High-protein diet: reduces hunger and preserves muscle\n'
            '• Reduce ultra-processed foods, liquid calories, and refined carbs\n'
            '• Move more: even walking 10,000 steps/day makes a significant difference\n'
            '• Sleep 7–9 hours — sleep deprivation promotes fat storage\n'
            '• Manage stress (elevated cortisol drives fat storage, especially around the abdomen)\n\n'
            'Avoid fad diets. Sustainable lifestyle changes matter more than rapid weight loss.'
        ),
    },
    {
        'keywords': ['portion', 'portion size', 'how much to eat', 'serving size', 'overeating'],
        'answer': (
            'Portion control is one of the most effective tools for weight management.\n\n'
            'Hand-size guide:\n'
            '• Protein (meat, paneer, fish) → palm of your hand (per serving)\n'
            '• Vegetables → cupped both hands\n'
            '• Carbs (rice, roti) → one cupped hand\n'
            '• Fats (oil, butter, ghee) → thumb tip\n\n'
            'Tips to avoid overeating:\n'
            '• Use smaller plates\n'
            '• Eat slowly — it takes 20 min for fullness signals to reach your brain\n'
            '• Don\'t eat in front of TV or phone\n'
            '• Drink water before meals\n'
            '• Never eat straight from a packet'
        ),
    },
    {
        'keywords': ['stress', 'cortisol', 'emotional eating', 'anxiety food', 'comfort food'],
        'answer': (
            'Stress triggers cortisol release, which raises appetite — especially for high-fat, high-sugar foods.\n\n'
            'Strategies to manage stress eating:\n'
            '• Identify emotional vs physical hunger — physical hunger builds gradually; emotional hunger is sudden\n'
            '• Replace stress eating with a short walk, deep breathing, or calling a friend\n'
            '• Keep healthy snacks accessible (fruit, nuts) and remove junk food from home\n'
            '• Eat regular meals — skipping meals worsens stress response\n'
            '• Magnesium-rich foods (dark chocolate in small amounts, nuts, seeds) may calm the nervous system\n'
            '• Practice 5 minutes of mindfulness or deep breathing before meals'
        ),
    },
    {
        'keywords': ['nuts', 'almond', 'walnut', 'cashew', 'peanut'],
        'answer': (
            'Nuts are calorie-dense but highly nutritious — a little goes a long way.\n\n'
            'Per 30 g (small handful) approx:\n'
            '• Almonds: 170 kcal | 6 g protein | 4 g fiber | rich in vitamin E and magnesium\n'
            '• Walnuts: 185 kcal | 4 g protein | 2.5 g omega-3 | brain-protective\n'
            '• Cashews: 160 kcal | 5 g protein | iron, zinc, magnesium\n'
            '• Peanuts: 170 kcal | 7 g protein — technically a legume, but great value\n\n'
            'Best eaten raw or dry-roasted — avoid salted, candied, or oil-roasted versions.\n'
            'Stick to one small handful per day if managing calorie intake.'
        ),
    },
    {
        'keywords': ['cooking methods', 'boiling', 'frying', 'grilling', 'steaming', 'baking', 'sauté'],
        'answer': (
            'Cooking methods significantly impact nutrient preservation and calorie content.\n\n'
            'Healthiest methods (preserve nutrients, low added fat):\n'
            '• Steaming: Vegetables retain vitamins; fish stays moist; no added oil needed\n'
            '• Grilling: Proteins develop flavor; minimal fat; creates beneficial compounds\n'
            '• Baking: Whole foods cook evenly; requires minimal oil\n'
            '• Boiling: Good for legumes, eggs; loses some water-soluble vitamins (but dal water is nutrient-dense)\n\n'
            'Methods to minimise (high fat/calories, nutrient loss):\n'
            '• Deep-frying: Adds 120–200 kcal per serving from oil absorption\n'
            '• Creamy curries: Adds saturated fat; portion control critical\n\n'
            'Tip: Stir-fry with minimal oil (1 tsp per person) and high heat to retain nutrients.'
        ),
    },
    {
        'keywords': ['spices', 'turmeric', 'cumin', 'chili', 'cinnamon', 'spice health benefits'],
        'answer': (
            'Indian spices are not just flavorful — many have powerful health benefits.\n\n'
            'Top spices and their benefits:\n'
            '• Turmeric (haldi): Curcumin is anti-inflammatory; enhances absorption with black pepper\n'
            '• Cumin (jeera): Aids digestion, improves iron absorption, stabilises blood sugar\n'
            '• Coriander (dhaniya): Diuretic; may help lower cholesterol\n'
            '• Ginger (adrak): Anti-nausea, anti-inflammatory; aids digestion\n'
            '• Red chili: Boosts metabolism by 3–5%; contains capsaicin\n'
            '• Cinnamon: Improves insulin sensitivity; lowers blood sugar spikes\n'
            '• Fenugreek (methi): Lowers blood sugar, aids lactation\n\n'
            'Use spices generously — they add flavor with zero calories while providing bioactive compounds!'
        ),
    },
    {
        'keywords': ['oil', 'olive oil', 'coconut oil', 'mustard oil', 'ghee', 'butter', 'which oil to use'],
        'answer': (
            'Oils and fats vary in fatty acid composition and smoke point.\n\n'
            'Best for cooking (high smoke point, healthy fats):\n'
            '• Mustard oil: High omega-3; strong taste; Indian staple\n'
            '• Coconut oil: Stable at high heat; mildly sweet flavor (use sparingly — high saturated fat)\n'
            '• Groundnut oil: Balanced profile; good for Indian cooking\n\n'
            'Best for drizzling/salads (low heat only):\n'
            '• Extra-virgin olive oil: Rich polyphenols; best unheated for Mediterranean recipes\n'
            '• Flaxseed oil: High omega-3; must be kept cold, never heated\n\n'
            'Limit for daily use:\n'
            '• Ghee: 15% more calories per serving than oil; use 1 teaspoon per person\n'
            '• Butter: Higher saturated fat — reserve for special occasions\n\n'
            'General guide: 1 teaspoon (5 ml) oil per person per meal ≈ 45 kcal, 5 g fat'
        ),
    },
    {
        'keywords': ['meal timing', 'eating time', 'when to eat', 'meal frequency', 'small meals'],
        'answer': (
            'While total daily calories matter most, meal timing affects hunger and energy.\n\n'
            'Optimal meal pattern (for most people):\n'
            '• 3 main meals (breakfast, lunch, dinner) spaced 4–5 hours apart\n'
            '• 1–2 small snacks between meals (especially if active)\n\n'
            'Why this matters:\n'
            '• Eating every 3–4 hours prevents extreme hunger (→ overeating)\n'
            '• Regular meals stabilise blood sugar and energy levels\n'
            '• Spreads protein intake throughout the day (better muscle synthesis)\n\n'
            'However: Intermittent fasting (16:8) works too if it helps you hit your calorie target.\n'
            'Some people thrive on 5–6 small meals; others on 2 large meals. Choose what you can sustain.\n\n'
            'The key: Eat in a way that prevents excessive hunger and supports adherence to your calorie goal.'
        ),
    },
    {
        'keywords': ['food substitution', 'swap', 'replace', 'healthier alternative', 'swap sugar'],
        'answer': (
            'Simple substitutions make healthy eating easier without sacrifice.\n\n'
            'Weight loss friendly swaps:\n'
            '• White rice → Brown rice or cauliflower rice (saves 30–40 kcal per cup)\n'
            '• White bread → Whole wheat or multigrain (more fiber, slower digestion)\n'
            '• Sugar drinks → Water, lemon water, black tea, black coffee\n'
            '• Fruit juice → Whole fruit (retains fiber; saves 50–80 kcal, cuts sugar spike)\n'
            '• Fried snacks → Baked chips, roasted chana, makhana\n'
            '• Cream/full-fat yogurt → Greek yogurt or low-fat dahi (same protein, fewer calories)\n'
            '• Cooking oil (3 tbsp) → Cooking spray + 1 tsp oil (saves 250 kcal)\n'
            '• Regular paneer → Low-fat paneer or tofu (saves 80 kcal per 100 g)\n'
            '• Desserts → Dark chocolate (70% cocoa), fruit, or dates\n\n'
            'Make one swap at a time to avoid overwhelm.'
        ),
    },
    {
        'keywords': ['digestion', 'bloating', 'gas', 'indigestion', 'acid reflux', 'heartburn'],
        'answer': (
            'Poor digestion impacts nutrient absorption and comfort.\n\n'
            'Common triggers:\n'
            '• High-fat meals: Take longer to digest (3–4 hours for fatty curry vs 2 hours for dal)\n'
            '• Legumes (dal, rajma, chana): High fiber; can cause bloating if eaten infrequently\n'
            '• Cruciferous veggies (cabbage, broccoli): Sauté with ginger and cumin to reduce gas\n'
            '• Eating too fast: Swallow air; eat too much too quickly\n'
            '• Spicy food: Can trigger reflux in sensitive people\n\n'
            'Solutions:\n'
            '• Ginger tea 20 min before meals improves digestion\n'
            '• Add dal gradually to your diet if new to it; your gut adapts in 2–3 weeks\n'
            '• Chew slowly: At least 20–30 chews per mouthful\n'
            '• Cumin-coriander-fennel tea post-meal aids digestion\n'
            '• Avoid lying down immediately after eating\n\n'
            'Consistent bloating after meals? Consult a doctor — may indicate food intolerance or IBS.'
        ),
    },
    {
        'keywords': ['hunger cues', 'true hunger', 'thirst', 'appetite', 'fullness signals'],
        'answer': (
            'Learning to distinguish true hunger from thirst or emotional hunger is key to sustainable eating.\n\n'
            'True physical hunger:\n'
            '• Develops gradually over 2–3 hours\n'
            '• Stomach growls or feels empty\n'
            '• Willing to eat any healthy food\n'
            '• Satisfied by any nourishing meal\n\n'
            'False hunger (thirst, boredom, stress):\n'
            '• Comes suddenly and intensely\n'
            '• Cravings for specific foods (usually high-sugar/high-fat)\n'
            '• Stops after drinking water or distraction\n'
            '• Eating doesn\'t feel truly satisfying\n\n'
            'Quick test: Drink a glass of water and wait 10 min. If hunger goes away, you were thirsty.\n'
            'Fullness takes 20 min to register in your brain — eat slowly and stop when 80% full.'
        ),
    },
    {
        'keywords': ['calorie burn', 'exercise', 'steps', 'walking', 'calories burned', 'activity'],
        'answer': (
            'Exercise burns calories and builds muscle, but diet is 70–80% of weight loss.\n\n'
            'Typical calorie burns (varies by weight and intensity):\n'
            '• Walking: 200–300 kcal per 30 min (depends on speed and incline)\n'
            '• Running: 400–600 kcal per 30 min\n'
            '• Cycling: 300–500 kcal per 30 min\n'
            '• Weight training: 200–300 kcal per 30 min + increased resting metabolism\n'
            '• Yoga: 120–180 kcal per 30 min\n\n'
            'Bottom line: 10,000 steps ≈ 300–400 kcal burned; this equals a single meal.\n'
            '→ Exercise alone cannot overcome a poor diet; pair with calorie awareness.\n'
            '→ Strength training builds muscle, which increases resting metabolism (long-term benefit).\n'
            '→ Aim for 150 min moderate + 2 days strength training per week.'
        ),
    },
    {
        'keywords': ['food label', 'nutrition facts', 'read label', 'ingredients list', 'expiry date'],
        'answer': (
            'Reading food labels helps you make informed choices.\n\n'
            'What to check:\n'
            '1. Serving size: The entire nutrition table is per this serving (often smaller than you eat!)\n'
            '2. Calories: Total energy in one serving\n'
            '3. Macros: Protein (builds muscle), fat (avoid trans fats), carbs (choose complex)\n'
            '4. Ingredients list: Listed by weight. If sugar/salt in top 3, it\'s a high-sugar/salt product.\n'
            '5. Look for claims: "No added sugar" ≠ naturally sugar-free. Check ingredients.\n\n'
            'Red flags:\n'
            '• Trans fat (avoid entirely; check ingredients for "hydrogenated oil")\n'
            '• Added sugar >5g per serving for savory foods, >15g for sweets\n'
            '• Sodium >300 mg per serving for snacks\n\n'
            'Pro tip: Apps like MyFitnessPal scan barcodes to log nutrition easily.'
        ),
    },
    {
        'keywords': ['myths', 'myth', 'misconception', 'nutrition myth', 'false belief'],
        'answer': (
            'Common nutrition myths debunked:\n\n'
            '❌ Myth: "Eating fat makes you fat"\n'
            '✓ Truth: Excess calories make you fat. Healthy fats are essential.\n\n'
            '❌ Myth: "Eggs raise cholesterol; avoid them"\n'
            '✓ Truth: Eggs are nutritious; dietary cholesterol ≠ blood cholesterol. Eat up to 3/day.\n\n'
            '❌ Myth: "Carbs are bad; go low-carb"\n'
            '✓ Truth: Complex carbs (oats, dal, brown rice) are fuel; refined carbs are the issue.\n\n'
            '❌ Myth: "Skip breakfast for weight loss"\n'
            '✓ Truth: Breakfast doesn\'t affect weight loss; total daily calories do. Eat if hungry.\n\n'
            '❌ Myth: "Detox diets cleanse your body"\n'
            '✓ Truth: Your liver and kidneys detox automatically. No product needed.\n\n'
            '❌ Myth: "Avoid salt entirely"\n'
            '✓ Truth: Sodium is essential; just avoid excess. Limit to 2,000 mg/day.\n\n'
            'Trust evidence, not hype!'
        ),
    },
    {
        'keywords': ['body composition', 'muscle', 'fat loss', 'lean', 'body recomposition', 'muscle gain fat loss'],
        'answer': (
            'Body recomposition (losing fat while gaining muscle) is possible and highly desirable.\n\n'
            'Key principle: Weight alone is misleading (muscle weighs more than fat).\n'
            '→ A person may lose 2 kg fat but gain 1 kg muscle (net -1 kg, but body looks better).\n\n'
            'To achieve recomposition:\n'
            '• Eat protein: 1.6–2.2 g per kg body weight (preserves + builds muscle)\n'
            '• Eat in slight deficit: 200–300 kcal below TDEE (slow fat loss, preserves muscle)\n'
            '• Lift weights 3–5 days/week (stimulates muscle protein synthesis)\n'
            '• Get 7–9 hours sleep (muscle grows during rest)\n'
            '• Don\'t rush: Body recomposition takes 8–12 weeks to show visibly\n\n'
            'Better metric than scale: Photos, measurements, how clothes fit, or DEXA scan.'
        ),
    },
    {
        'keywords': ['cooking tips', 'batch cooking', 'meal prep', 'food storage', 'how to store food'],
        'answer': (
            'Meal prep saves time and keeps you on track.\n\n'
            'Batch cooking strategy:\n'
            '• Cook dal/rice in bulk on Sunday for 3–4 days\n'
            '• Grill chicken/paneer in batches; refrigerate up to 4 days\n'
            '• Chop vegetables and store in airtight containers (lasts 3–4 days)\n'
            '• Portion snacks (nuts, fruit) in containers for grab-and-go\n\n'
            'Storage guidelines:\n'
            '• Cooked dal/rice: 4 days in fridge\n'
            '• Cooked meat/paneer: 3–4 days\n'
            '• Raw vegetables: 5–7 days in airtight container\n'
            '• Cut fruit: 2–3 days (keeps longer if acidic: citrus, berries)\n'
            '• Nuts/seeds: 2 weeks (room temp); 3 months (freezer)\n\n'
            'Freeze-friendly: Dal, cooked rice, cooked meat, soups, curries (up to 3 months).\n'
            'Planning 1 hour/week saves 5+ hours of daily meal decisions!'
        ),
    },
    {
        'keywords': ['motivation', 'motivation to diet', 'stay on track', 'consistency', 'losing motivation'],
        'answer': (
            'Nutrition success requires consistency, not perfection. Even 80% adherence wins over time.\n\n'
            'Strategies to stay motivated:\n'
            '• Set specific, measurable goals: "Lose 5 kg in 3 months" vs "Get fit"\n'
            '• Track progress beyond scale: Energy, strength gains, clothes fit, skin clarity\n'
            '• Join a community: Friends, online groups, or a registered dietitian for accountability\n'
            '• Plan 1 cheat meal/week: Knowing you can enjoy your favorite food prevents deprivation\n'
            '• Celebrate small wins: Stuck to protein target for a week? That\'s a win!\n'
            '• Change your environment: Bring snacks to office; meal prep at home; avoid triggers\n'
            '• Remind yourself why: Write your goal and reasons on a sticky note; read weekly\n\n'
            'Remember: The best diet is one you can follow consistently. Choose realistic, sustainable changes.'
        ),
    },
    {
        'keywords': ['indian food', 'desi', 'traditional indian', 'indian cuisine', 'south indian'],
        'answer': (
            'Traditional Indian cuisine is naturally nutritious when cooked mindfully.\n\n'
            'Nutrition highlights:\n'
            '• Dal (lentils): High protein and fiber; affordable, sustains energy\n'
            '• Roti (whole wheat): Complex carbs, easy portion control, satiating\n'
            '• Sambar/rasam: Spice blends aid digestion; can make at home to control oil\n'
            '• Dosa/idli: Fermented, easier to digest; use minimal coconut oil\n'
            '• Sabzi: Nutrient-dense vegetables; cook with minimal oil for best results\n\n'
            'Modifications for weight loss:\n'
            '• Use 1 tsp oil per person, not a glob\n'
            '• Grill or steam instead of frying (saves 100+ kcal per dish)\n'
            '• Include vegetables in every meal; aim for 50% of the plate\n'
            '• Whole wheat roti > refined maida roti (saves 20 kcal, gains 2 g fiber)\n\n'
            'You don\'t need to eat foreign foods to be healthy — master your traditional diet first!'
        ),
    },
]

_FALLBACK_ANSWER = (
    'That\'s a great question about nutrition! While I\'m a rule-based assistant with a built-in knowledge base, '
    'I may not have a specific answer for that.\n\n'
    'Try asking about:\n'
    '• BMI, BMR, or calorie calculations\n'
    '• Weight loss or weight gain strategies\n'
    '• Protein, carbs, fat, or fiber intake\n'
    '• Specific foods (eggs, dal, paneer, rice, fruits, vegetables)\n'
    '• Diet types (keto, Mediterranean, vegetarian)\n'
    '• Meal planning or portion control\n'
    '• Health topics (diabetes, cholesterol, gut health, sleep)\n\n'
    'For a fully personalised AI response, add a free Groq API key (see .env.example).'
)


def _rule_based_chat(question):
    """Keyword-score the knowledge base and return the best matching answer."""
    q = question.lower()
    best_score = 0
    best_answer = None
    for entry in _KB:
        score = sum(1 for kw in entry['keywords'] if kw in q)
        if score > best_score:
            best_score = score
            best_answer = entry['answer']
    return best_answer if best_score > 0 else _FALLBACK_ANSWER


def _call_llm(client, model, question, history):
    """Shared call for OpenAI or Groq (same interface)."""
    system_prompt = (
        'You are EatRight AI, a knowledgeable, friendly, and personalized nutrition and diet assistant. '
        'You are part of the EatRight app that helps users with personalized diet recommendations, calorie tracking, and health goals.\n\n'
        'Your expertise:\n'
        '• Personalized diet planning based on user metrics (BMI, body fat, age, gender, goals)\n'
        '• Macronutrient guidance (protein, carbs, fats) tailored to individual targets\n'
        '• Indian cuisine nutrition (dal, paneer, roti, traditional dishes, spices)\n'
        '• Practical strategies: meal prep, cooking methods, label reading, portion control\n'
        '• Evidence-based answers on weight loss, muscle gain, and body recomposition\n'
        '• Debunking myths and providing scientifically-backed nutrition facts\n\n'
        'Tone & approach:\n'
        '• Always be encouraging and non-judgmental\n'
        '• Provide specific, actionable advice with quantities and examples\n'
        '• Include Indian food context when relevant — many users follow traditional diets\n'
        '• Format multi-step answers with numbered lists or bullet points\n'
        '• When a user mentions body metrics or goals, relate advice to their specific situation\n'
        '• Distinguish between personalized guidance (use app features) vs general advice (provide here)\n\n'
        'Examples of personalization:\n'
        '• "Based on your BMI of 28, a calorie deficit of 300-500 kcal/day through diet + exercise is ideal for you."\n'
        '• "For your goal of 1,800 kcal/day, I\'d suggest: 150g protein (20%), 180g carbs (40%), 60g fat (30%)."\n'
        '• "Since you prefer vegetarian foods, let\'s build your protein from dal, paneer, eggs, and Greek yogurt."\n\n'
        'Scope reminders:\n'
        '• Do NOT diagnose medical conditions or replace a doctor\'s advice\n'
        '• When discussing health concerns (diabetes, heart disease), emphasize consulting a healthcare provider\n'
        '• Recommend a registered dietitian for athletes, pregnant women, or complex conditions'
    )
    messages = [{'role': 'system', 'content': system_prompt}]
    if history:
        for msg in history[-10:]:
            role = msg.get('role', 'user')
            if role in ('user', 'assistant'):
                messages.append({'role': role, 'content': str(msg.get('content', ''))})
    messages.append({'role': 'user', 'content': question})
    try:
        completion = client.chat.completions.create(model=model, messages=messages)
        return completion.choices[0].message.content or 'No response generated. Please try again.'
    except Exception as exc:
        return f'AI service error: {exc}. Falling back to knowledge base.\n\n{_rule_based_chat(question)}'


def chatfunction(question, history=None):
    content = (question or '').strip()
    if not content:
        return 'Please enter a question.'

    # Priority 1: OpenAI
    if openai_client:
        return _call_llm(openai_client, OPENAI_MODEL, content, history)

    # Priority 2: Groq (free tier — add GROQ_API_KEY to .env)
    if groq_client:
        return _call_llm(groq_client, GROQ_MODEL, content, history)

    # Priority 3: Offline rule-based knowledge base
    return _rule_based_chat(content)


def get_image(question):
    cont = (question or '').strip()
    if not cont or not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return None

    url = f'https://www.googleapis.com/customsearch/v1?q={cont}&cx={GOOGLE_CSE_ID}&searchType=image&key={GOOGLE_API_KEY}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    items = data.get('items', [])
    for item in items:
        link = item.get('link')
        if not link:
            continue
        try:
            res = requests.get(link, timeout=10)
            if res.ok and res.content:
                return res.content
        except requests.RequestException:
            continue
    return None
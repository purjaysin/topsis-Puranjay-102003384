import streamlit as st
import smtplib
st.set_page_config(page_title="Puranjay's Topsis", layout="wide", initial_sidebar_state="expanded")  
st.title("TOPSIS for MCDM")

Inpcsv = st.file_uploader("Upload the input .csv file", type="csv")
Weights = st.text_input("Weights")
Impacts = st.text_input("Impacts", value="")
Email_id = st.text_input("Enter email ID", value="", type="default")
submit = st.button("Submit")

if submit:
    if Inpcsv is None:
        st.error("Please upload the input .csv file")
    else:
        # st.success("Input file uploaded successfully")
        if Weights is "":
            st.error("Please enter the weights")
        else:
            # st.success("Weights entered successfully")
            if Impacts is "":
                st.error("Please enter the impacts")
            else:
                # st.success("Impacts entered successfully")
                new_weights = Weights.split(",")
                new_impacts = Impacts.split(",")
                if len(new_weights) != len(new_impacts):
                    st.error("No. of weights and impacts should be equal")
                if Email_id is "":
                    st.error("Please enter the email ID")
                else:
                    if "@" not in Email_id:
                        st.error("Please enter a valid email ID")
                    else:
                        # st.success("Email ID entered successfully")
                        st.balloons()
                        st.success("Result has been mailed to your email ID.")

if submit:
    import pandas as pd
    import numpy as np
    import sys
    import email, smtplib, ssl
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import os

    def checkfornumerical(_df):
        if _df.shape[1] == _df.select_dtypes(include=np.number).shape[1]:
            return True
        else:
            return False
    def normalize(result_df):
        for i in range(result_df.shape[1]):
            rootofsums = 0
            for j in range(result_df.shape[0]):
                rootofsums = rootofsums + result_df.iloc[j, i] ** 2
            rootofsums = rootofsums ** 0.5
            for j in range(result_df.shape[0]):
                result_df.iloc[j, i] = (result_df.iloc[j, i] / rootofsums)
        return result_df
    
    def addingweights(result_df, _weights):
        weights = _weights.split(",")
        if len(weights) != result_df.shape[1]:
            print("Size of weights is not equal to number of columns")
            sys.exit()
        for i in range(len(weights)):
            try:
                weights[i] = float(weights[i])
            except:
                print("Value of weight is not in float. Please enter only float value.")
                sys.exit()
        for i in range(result_df.shape[1]):
            for j in range(result_df.shape[0]):
                result_df.iloc[j, i] = (result_df.iloc[j, i]) * (weights[i])
        return result_df

    def idealbestworst(result_df, _impacts):
        impacts = _impacts.split(",")
        if len(impacts) != result_df.shape[1]:
            print("Size of Impacts is not equal to number of columns")
            sys.exit()
        for i in range(len(impacts)):
            if impacts[i] == '+' or impacts[i] == '-':
                continue
            else:
                print("Impacts are not '+' or '-'")
                sys.exit()
        idealbest = []
        idealworst = []
        for i in range(result_df.shape[1]):
            if impacts[i] == "+":
                idealbest.append(max(result_df.iloc[:, i]))
                idealworst.append(min(result_df.iloc[:, i]))
            if impacts[i] == "-":
                idealbest.append(min(result_df.iloc[:, i]))
                idealworst.append(max(result_df.iloc[:, i]))

        result_df.loc[len(result_df.index)] = idealbest
        result_df.loc[len(result_df.index)] = idealworst
        return result_df

    def euclideandistance(result_df):
        idealbest = list(result_df.iloc[-2, :])
        idealworst = list(result_df.iloc[-1, :])
        result_df = result_df.iloc[:-2, :].copy()
        edp = []
        edn = []
        for i in range(result_df.shape[0]):
            tempedp = 0
            tempedn = 0
            for j in range(result_df.shape[1]):
                tempedp = tempedp + (result_df.iloc[i, j] - idealbest[j]) ** 2
                tempedn = tempedn + (result_df.iloc[i, j] - idealworst[j]) ** 2
            edp.append(tempedp ** 0.5)
            edn.append(tempedn ** 0.5)
        result_df["edp"] = edp
        result_df["edn"] = edn
        result_df["edp+edn"] = result_df["edp"] + result_df["edn"]
        pscore = []
        for i in range(result_df.shape[0]):
            pscore.append(((result_df["edn"][i]) / (result_df["edp+edn"][i])) * 100)
        result_df["Topsis Score"] = pscore
        return result_df
    
    def givingranks(result_df):
        mapping = {}
        temp_psscore = list(result_df.iloc[:, -1])
        temp_psscore.sort(reverse=True)
        for i in range(len(temp_psscore)):
            mapping[temp_psscore[i]] = i + 1
        ranks = []
        for i in range(result_df.shape[0]):
            ranks.append(mapping[result_df.iloc[i, -1]])
        result_df = result_df.copy()
        result_df["Rank"] = ranks
        return result_df

    def topsis(_inputcsv, _weights, _impacts, _resultfilename):
        try:
            df = pd.read_csv(_inputcsv)
        except:
            print("Input file could not be found")
            sys.exit()

        if len(df.columns) < 3:
            print("There needs to be atleast 3 columns")
            sys.exit()
        if checkfornumerical(df.iloc[:, 1:]) == False:
            print("Need only numerical values")
            sys.exit()
        evaldf = df.iloc[:, 1:]
        weights = _weights
        impacts = _impacts
        evaldf1 = normalize(evaldf)
        evaldf2 = addingweights(evaldf1, weights)
        evaldf3 = idealbestworst(evaldf2, impacts)
        evaldf4 = euclideandistance(evaldf3)
        evaldf5 = givingranks(evaldf4)
        df["Topsis Score"] = evaldf5["Topsis Score"]
        df["Rank"] = evaldf5["Rank"]
        df.to_csv(_resultfilename, index=False)
    filenameout = "result-topsis.csv"
    topsis(Inpcsv, Weights, Impacts, filenameout)
    st.write("Result File is generated with name: ", filenameout)

    def sendEmail(email, result_file) : 
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "psingh12_be20@thapar.edu"  # Enter your address
        PASSWORD = "lxreijnqjiaghtti"
        receiver_email = Email_id  # Enter receiver address

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Topsis result from Puranjay Singh"

        # Add body to email
        message.attach(MIMEText("You used the app for TOPSIS calculation. Please find the result in the attached CSV file.", "plain"))

        # Open PDF file in bynary
        with open(filenameout, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload((attachment).read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header with pdf name
        part.add_header(
        "Content-Disposition",
        f"attachment; filename={result_file}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, PASSWORD)
            server.sendmail(sender_email, receiver_email, text)
    sendEmail(Email_id, filenameout)

    os.remove(filenameout)





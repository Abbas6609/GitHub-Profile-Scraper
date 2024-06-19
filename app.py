# Importing Necessary Libraries
import streamlit as st
from scrape import getData
import plotly.express as px
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import traceback

# Initialize session state for username, display_data, and input_key
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'display_data' not in st.session_state:
    st.session_state.display_data = False
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0  # Initialize a key for the input widget

# Streamlit page configuration
st.set_page_config(page_title="✨Tosief's:  GitScrapper!✨", layout='centered')
st.title("🌟✨ Tosief's GitScrapper! 🎉🚀")
st.title("Navigating GitHub Universe🌌🔭")

# Use the session state for the username input with a dynamic key
userName = st.text_input('Enter Github Username', value=st.session_state.username, key=st.session_state.input_key)

# Adding a process button
process_button = st.button('Process')

if process_button:
    st.session_state.username = userName  # Store the username in session state
    st.session_state.display_data = True

# Clear button to reset the display and username
clear_button = st.button('Clear')

if clear_button:
    st.session_state.username = ''
    st.session_state.display_data = False
    st.session_state.input_key += 1  # Increment the key to reset the input widget
    st.experimental_rerun()  # Rerun the app to clear the interface


def generate_pdf(df):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))  # Use landscape orientation
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(name='Custom', parent=styles['Normal'], wordWrap='LTR', fontSize=8)
    column_widths = [100, 150, 80, 80, 200, 40, 40, 60]  # Adjust the widths as needed

    # Prepare data for Table
    data = [['Repository Name', 'URL', 'Updated', 'Language', 'Description', 'Stars', 'Forks', 'Open Issues']]
    for _, row in df.iterrows():
        row_data = [Paragraph(str(row[col]), custom_style) for col in df.columns]
        data.append(row_data)

    table = Table(data, colWidths=column_widths, repeatRows=1)

    # Style the Table
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    # Build the PDF
    elems = [table]
    pdf.build(elems)

    buffer.seek(0)
    return buffer

# Main logic inside a conditional block based on session state
if st.session_state.display_data and userName:
    with st.spinner('Fetching data... Please wait.'):
        try:
            result = getData(userName)

            if result is not None:
                info, repo_info = result
                df = pd.DataFrame(repo_info)

                for key, value in info.items():
                    if key != 'image_url':
                        st.subheader(f'{key} : {value}')
                    else:
                        st.image(value)

                # Initialize language filter with no selection
                language_filter = st.sidebar.multiselect('Filter by Language', ['All'] + list(df['language'].unique()), default=['All'])

                # Filtering logic
                if 'All' in language_filter or not language_filter:
                    filtered_repos = df
                else:
                    filtered_repos = df[df['language'].isin(language_filter)]

                st.subheader("Repositories")
                st.table(filtered_repos)

                # Plotting code
                st.subheader("Repository Stars and Forks")
                fig = px.scatter(df, x='forks', y='stars', color='language', hover_data=['name'])
                st.plotly_chart(fig)

                # CSV Download
                csv = df.to_csv().encode('utf-8')
                st.download_button(label="Download profile data as CSV", data=csv, file_name='Gh_profile_df.csv', mime='text/csv')
                
                # PDF Download
                pdf = generate_pdf(df)
                st.download_button(label="Download profile data as PDF", data=pdf, file_name="Gh_profile_df.pdf", mime="application/pdf")

            else:
                st.error("Failed to fetch data. Please check the username and try again.")

        except requests.exceptions.RequestException as e:
            st.error("Error in fetching data: " + str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            traceback.print_exc()
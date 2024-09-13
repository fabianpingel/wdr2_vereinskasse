import sqlite3
import streamlit as st
import pandas as pd
from io import BytesIO  # Für den In-Memory-Download

def main():

    # SQLite Datenbankverbindung
    db_path = 'codewords.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabelle erstellen (falls noch nicht vorhanden)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS codewords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vereinsname TEXT UNIQUE,
        codewort TEXT
    )
    ''')

    # Funktion zum Hinzufügen eines Codeworts
    def add_codeword(vereinsname, codewort):
        cursor.execute('INSERT OR REPLACE INTO codewords (vereinsname, codewort) VALUES (?, ?)', (vereinsname, codewort))
        conn.commit()

    # Funktion zum Abrufen aller Codewörter
    def get_codewords():
        cursor.execute('SELECT * FROM codewords')
        return cursor.fetchall()
   
    # Funktion zum Löschen eines Eintrags
    def delete_codeword(vereinsname):
        cursor.execute('DELETE FROM codewords WHERE vereinsname = ?', (vereinsname,))
        conn.commit()
    
    # Funktion zum Exportieren der Datenbank als Excel
    def export_to_excel():
        data = get_codewords()
        df = pd.DataFrame(data, columns=['ID', 'Vereinsname', 'Codewort'])
        
        # Excel-Datei in einem BytesIO-Puffer speichern
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        buffer.seek(0)  # Setze den Cursor auf den Anfang des Puffers
        return buffer
    
    # Funktion zum Exportieren der Datenbankdatei
    def export_db():
        with open(db_path, 'rb') as f:
            db_data = f.read()
        return db_data
        
    # Passwortschutz für Admin-Funktionen (Laden aus secrets)
    def check_password():
        # Admin-Passwort aus Streamlit-Secrets laden
        admin_password = st.secrets["admin"]["password"]
        return st.sidebar.text_input("Admin Passwort", type="password") == admin_password


    # Seitenlayout
    st.title('📻 WDR2 Gewinnspiel')
    st.header('💰 1.000€ für die Vereinskasse 💰')

    # Seitenleiste für das Hinzufügen neuer Codewörter
    with st.sidebar:

        # Logo
        st.image('Logo_Dorfverein.jpeg', use_column_width=True)

        st.header('Neues Codewort hinzufügen', divider="gray")
        vereinsname = st.text_input('Vereinsname', help='Hier den Vereinsnamen eintragen.')
        codewort = st.text_input('Codewort', help='Hier das Codewort eintragen.')
        if st.button('Codewort hinzufügen'):
            if vereinsname.strip() != '' and codewort.strip() != '':
                add_codeword(vereinsname, codewort)
                st.success(f'Codewort für {vereinsname} hinzugefügt!')


        # Passwort für Admin-Funktionen 
        st.sidebar.markdown("---")
        if check_password():
            with st.expander("Admin-Optionen", expanded=False):
                st.header('Admin-Optionen', divider="gray")
                
                #st.header('Datenbank exportieren')
                # Button zum Herunterladen der Datenbank
                if st.button('Datenbank exportieren'):
                    # Download als Excel
                    excel_data = export_to_excel()
                    st.download_button(
                        label="Excel-Datei herunterladen",
                        data=excel_data,
                        file_name='codewords_export.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    
                    # Download der Datenbank
                    db_file = export_db()
                    st.download_button(
                        label="Datenbank herunterladen",
                        data=db_file,
                        file_name='codewords.db',
                        mime='application/octet-stream'
                    )

                st.header('Einträge löschen', divider="gray")
                selected_verein = st.selectbox('Wähle einen Verein zum Löschen aus', [x[1] for x in get_codewords()])
                if st.button('Eintrag löschen'):
                    delete_codeword(selected_verein)
                    st.success(f'Eintrag für {selected_verein} gelöscht!')

                st.header('Codewort bearbeiten', divider="gray")
                edit_verein = st.selectbox('Wähle einen Verein zum Bearbeiten aus', [x[1] for x in get_codewords()])
                new_codewort = st.text_input('Neues Codewort für den Verein eingeben', value='')

                if st.button('Änderungen speichern'):
                    if new_codewort.strip() != '':
                        add_codeword(edit_verein, new_codewort)  # `INSERT OR REPLACE` wird verwendet, um das Codewort zu aktualisieren
                        st.success(f'Codewort für {edit_verein} wurde aktualisiert!')
        else:
            st.error("Zugriff auf Admin-Funktionen verweigert! Falsches Passwort.")

    # Hauptbereich zur Anzeige der Codewörter
    st.subheader('Codewörter anzeigen')

    codewords_list = get_codewords()
    if len(codewords_list) == 0:
        st.error('Keine Codewörter hinzugefügt.')

    vereinsnamen = [item[1] for item in codewords_list]
    selected_verein = st.selectbox('Wähle einen Verein aus', sorted(vereinsnamen), help='Hier einen Verein auswählen, um dessen Codewort anzuzeigen.')

    if st.button('Zeige Codewort'):
        for id, verein, codewort in codewords_list:
            if verein == selected_verein:
                st.success(f'Das Codewort für {selected_verein} ist: **{codewort}**')
                st.info('WDR 2 Hotline **0800 5678 222**')


    # Copyright- und Versionsinformation hinzufügen
    st.sidebar.markdown("---")
    st.sidebar.text("© 2024 - Fabian Pingel")
    st.sidebar.text("Version: 1.1")

if __name__ == "__main__":
    main()
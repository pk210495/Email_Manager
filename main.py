import streamlit as st
import imaplib
import email
import csv
import io

def connect_to_email(email_address, password):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, password)
        return mail
    except imaplib.IMAP4.error as e:
        st.error(f"IMAP error: {str(e)}")
        if "AUTHENTICATIONFAILED" in str(e):
            st.error("Authentication failed. Please check your email and password.")
            st.info("If you're using Gmail, make sure to:")
            st.info("1. Enable 'Less secure app access' in your Google Account settings, or")
            st.info("2. Use an 'App Password' if you have 2-factor authentication enabled.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def filter_emails(mail, keywords):
    mail.select('inbox')
    deleted_emails = []

    for keyword in keywords:
        _, message_numbers = mail.search(None, f'SUBJECT "{keyword}"')
        for num in message_numbers[0].split():
            _, msg = mail.fetch(num, '(RFC822)')
            email_body = msg[0][1]
            message = email.message_from_bytes(email_body)
            
            subject = message['subject']
            sender = message['from']
            date = message['date']
            
            deleted_emails.append({
                'Subject': subject,
                'From': sender,
                'Date': date,
                'Keyword': keyword
            })
            
            mail.store(num, '+FLAGS', '\\Deleted')
    
    mail.expunge()
    return deleted_emails

def main():
    st.title("Email Keyword Filter App")

    email_address = st.text_input("Email Address:")
    password = st.text_input("Email Password:", type="password")
    keywords = st.text_input("Keywords (comma-separated):")

    if st.button("Filter Emails"):
        if email_address and password and keywords:
            st.info(f"Attempting to connect to email: {email_address}")
            mail = connect_to_email(email_address, password)
            if mail:
                st.success("Successfully connected to email.")
                keywords_list = [k.strip() for k in keywords.split(',')]
                deleted_emails = filter_emails(mail, keywords_list)
                st.success(f"Filtered and deleted {len(deleted_emails)} emails.")

                if deleted_emails:
                    csv_buffer = io.StringIO()
                    writer = csv.DictWriter(csv_buffer, fieldnames=['Subject', 'From', 'Date', 'Keyword'])
                    writer.writeheader()
                    writer.writerows(deleted_emails)

                    st.download_button(
                        label="Download Deleted Emails CSV",
                        data=csv_buffer.getvalue(),
                        file_name="deleted_emails.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No emails were deleted based on the provided keywords.")
        else:
            st.warning("Please fill in all fields.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Send follow-up email to Dr. Sabin Paudel after fixing his profile issues
"""

from app import app
import os
import resend
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email_to_sabin():
    with app.app_context():
        # Dr. Sabin Paudel's email
        doctor_email = "dr.sabin@mandaladental.com"

        print(f"📧 Sending email to: {doctor_email}")
        print()

        # Get Resend API key
        resend.api_key = os.getenv('RESEND_API_KEY')

        if not resend.api_key:
            print("❌ RESEND_API_KEY not found in environment!")
            return

        subject = "Your RankSewa Profile Has Been Updated"

        html_body = """
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #111;">
            <p><strong>Namaste Dr. Sabin Paudel,</strong></p>

            <p>
                Thank you for reaching out and for bringing those details to our attention.
            </p>

            <p>
                We're happy to let you know that both issues have been resolved:
            </p>

            <ul style="margin: 20px 0;">
                <li>The duplicate "Dr. Dr." prefix has been corrected.</li>
                <li>Your specialty has been updated to <strong>Dentist</strong></li>
            </ul>

            <p>
                Your profile is now accurate and live on RankSewa ✅
            </p>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

            <h3 style="color: #2563eb;">Enhance Your Profile (Optional)</h3>

            <p>
                If you'd like, you can further enhance your profile by adding a short professional
                description (about your experience, services, or areas of interest).
            </p>

            <p>You may either:</p>
            <ul>
                <li>Update it directly from your <a href="https://ranksewa.com/doctor/dashboard" style="color: #2563eb;">dashboard</a>, or</li>
                <li>Email us the description details, and we'll gladly update it for you</li>
            </ul>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

            <h3 style="color: #2563eb;">Help Patients Find You</h3>

            <p>To help patients discover your profile, we also encourage you to:</p>
            <ul>
                <li>Share your RankSewa profile on Facebook</li>
                <li>Follow and subscribe to the <a href="https://www.facebook.com/ranksewa" style="color: #2563eb;">RankSewa Facebook page</a> for updates and visibility</li>
            </ul>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

            <p>
                If you need any further assistance, feel free to reply to this email—we're always happy to help.
            </p>

            <p style="margin-top: 32px;">
                <strong>Warm regards,</strong><br>
                RankSewa Support Team<br>
                <a href="mailto:support@ranksewa.com" style="color: #2563eb;">support@ranksewa.com</a><br>
                <a href="https://ranksewa.com" style="color: #2563eb;">https://ranksewa.com</a>
            </p>

            <div style="margin-top: 40px; padding: 20px; background-color: #f3f4f6; border-radius: 8px;">
                <p style="margin: 0; font-size: 14px; color: #6b7280;">
                    <strong>Note:</strong> We've also improved our registration form based on your feedback
                    to prevent these issues for future doctors. Your input was invaluable in making RankSewa better!
                </p>
            </div>
        </div>
        """

        try:
            params = {
                "from": "RankSewa Support <support@ranksewa.com>",
                "to": [doctor_email],
                "subject": subject,
                "html": html_body,
                "reply_to": "support@ranksewa.com"
            }

            response = resend.Emails.send(params)
            print(f"✅ Email sent successfully to {doctor_email}!")
            print(f"   Message ID: {response.get('id', 'N/A')}")
            print(f"\n📧 Dr. Sabin should receive the email shortly.")

        except Exception as e:
            print(f"❌ Failed to send email: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Send Follow-Up Email to Dr. Sabin Paudel")
    print("=" * 60)
    print()
    send_email_to_sabin()

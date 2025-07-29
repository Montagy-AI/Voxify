"""
Email Service
SMTP email sending functionality for Voxify platform
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending SMTP emails"""

    def __init__(self, smtp_config: Optional[dict] = None):
        """
        Initialize email service with SMTP configuration

        Parameters
        ----------
        smtp_config : dict, optional
            SMTP configuration dictionary. If None, uses environment variables.
        """
        if smtp_config:
            self.smtp_host = smtp_config.get("host")
            self.smtp_port = smtp_config.get("port", 587)
            self.smtp_username = smtp_config.get("username")
            self.smtp_password = smtp_config.get("password")
            self.smtp_use_tls = smtp_config.get("use_tls", True)
            self.from_email = smtp_config.get("from_email", self.smtp_username)
            self.from_name = smtp_config.get("from_name", "Voxify")
        else:
            # Load from environment variables
            self.smtp_host = os.getenv("SMTP_HOST")
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
            self.smtp_username = os.getenv("SMTP_USERNAME")
            self.smtp_password = os.getenv("SMTP_PASSWORD")
            self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            self.from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_username)
            self.from_name = os.getenv("SMTP_FROM_NAME", "Voxify")

    def send_password_reset_email(
        self, to_email: str, reset_token: str, user_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send password reset email to user

        Parameters
        ----------
        to_email : str
            Recipient email address
        reset_token : str
            Password reset token
        user_name : str, optional
            User's name for personalization

        Returns
        -------
        tuple
            (success, error_message)
        """
        try:
            # Generate email content
            subject, html_content, text_content = self._get_reset_email_template(
                reset_token, user_name
            )

            # Send email
            return self._send_email(to_email, subject, html_content, text_content)

        except Exception as e:
            error_msg = f"Failed to send password reset email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Send email via SMTP

        Parameters
        ----------
        to_email : str
            Recipient email address
        subject : str
            Email subject
        html_content : str
            HTML email content
        text_content : str, optional
            Plain text email content

        Returns
        -------
        tuple
            (success, error_message)
        """
        try:
            # Validate SMTP configuration
            if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
                return False, "SMTP configuration is incomplete"

            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()

                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Password reset email sent successfully to {to_email}")
            return True, ""

        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP authentication failed. Please check email credentials."
            logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPRecipientsRefused:
            error_msg = (
                f"Recipient email address '{to_email}' was refused by the server."
            )
            logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _get_reset_email_template(
        self, reset_token: str, user_name: Optional[str] = None
    ) -> Tuple[str, str, str]:
        """
        Generate password reset email template

        Parameters
        ----------
        reset_token : str
            Password reset token
        user_name : str, optional
            User's name for personalization

        Returns
        -------
        tuple
            (subject, html_content, text_content)
        """
        # Determine greeting
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        # Generate reset URL (this should be configurable)
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{base_url}/reset-password?token={reset_token}"

        # Email subject
        subject = "Reset Your Voxify Password"

        # HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #ffffff;
            background-color: #000000;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background-color: #000000;
            border: 1px solid #333333;
            border-radius: 12px;
            overflow: hidden;
        }}
        .header {{
            background-color: #000000;
            color: #ffffff;
            padding: 30px 20px;
            text-align: center;
            border-bottom: 1px solid #333333;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header h2 {{
            margin: 0;
            font-size: 18px;
            font-weight: 400;
            color: #cccccc;
        }}
        .content {{
            background-color: #111111;
            padding: 40px 30px;
            color: #ffffff;
        }}
        .content p {{
            margin: 0 0 16px 0;
            color: #e5e5e5;
        }}
        .button {{
            display: inline-block;
            background-color: #ffffff;
            color: #000000;
            padding: 14px 28px;
            text-decoration: none;
            border-radius: 8px;
            margin: 24px 0;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .button:hover {{
            background-color: #f0f0f0;
        }}
        .url-box {{
            word-break: break-all;
            background-color: #1a1a1a;
            border: 1px solid #333333;
            padding: 16px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #cccccc;
        }}
        .warning {{
            background-color: #1a1a1a;
            border: 1px solid #444444;
            border-left: 4px solid #ffffff;
            border-radius: 8px;
            padding: 20px;
            margin: 24px 0;
        }}
        .warning strong {{
            color: #ffffff;
        }}
        .warning ul {{
            margin: 12px 0 0 0;
            padding-left: 20px;
        }}
        .warning li {{
            margin: 8px 0;
            color: #cccccc;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333333;
            font-size: 14px;
            color: #888888;
        }}
        .footer p {{
            margin: 8px 0;
            color: #888888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ Voxify</h1>
            <h2>Password Reset Request</h2>
        </div>
        
        <div class="content">
            <p>{greeting}</p>
            
            <p>We received a request to reset your password for your Voxify account. If you made this request, click the button below to reset your password:</p>
            
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset My Password</a>
            </p>
            
            <p><strong>⚠️ If the button doesn't work properly:</strong></p>
            <p>Some email clients may redirect links through security services. If you're redirected to an unexpected page, please copy and paste this link directly into your browser address bar:</p>
            <div class="url-box">
                {reset_url}
            </div>
            
            <div class="warning">
                <strong>⚠️ Important:</strong>
                <ul>
                    <li>This link will expire in <strong>15 minutes</strong></li>
                    <li>If the button redirects to an unexpected page, <strong>copy the link above and paste it directly into your browser</strong></li>
                    <li>If you didn't request this password reset, please ignore this email</li>
                    <li>Your password will remain unchanged until you create a new one</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>If you're having trouble clicking the button, copy and paste the URL above into your web browser.</p>
                <p>This is an automated message from Voxify. Please do not reply to this email.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Plain text content
        text_content = f"""
{greeting}

We received a request to reset your password for your Voxify account.

If you made this request, copy and paste the link below directly into your browser address bar:
{reset_url}

IMPORTANT:
- This link will expire in 15 minutes
- If you're redirected to an unexpected page, make sure to copy and paste the link directly into your browser
- If you didn't request this password reset, please ignore this email
- Your password will remain unchanged until you create a new one

For best results, copy the entire link and paste it directly into your browser address bar.

This is an automated message from Voxify. Please do not reply to this email.
"""

        return subject, html_content, text_content

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test SMTP connection

        Returns
        -------
        tuple
            (success, message)
        """
        try:
            if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
                return False, "SMTP configuration is incomplete"

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)

            return True, "SMTP connection successful"

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed"
        except Exception as e:
            return False, f"SMTP connection failed: {str(e)}"


# Utility function to get default email service instance
def get_email_service() -> EmailService:
    """
    Get default email service instance using environment variables

    Returns
    -------
    EmailService
        Configured email service instance
    """
    return EmailService()

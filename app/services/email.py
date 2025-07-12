# app/services/email.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)

class EmailService:
    """Email notification service for ReWear"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.email_username = getattr(settings, 'EMAIL_USERNAME', '')
        self.email_password = getattr(settings, 'EMAIL_PASSWORD', '')
        self.email_from = getattr(settings, 'EMAIL_FROM', 'noreply@rewear.com')
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _send_email_sync(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email synchronously"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                if self.email_username and self.email_password:
                    server.login(self.email_username, self.email_password)
                server.sendmail(self.email_from, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_email_async(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._send_email_sync, 
            to_email, 
            subject, 
            html_content, 
            text_content
        )
    
    def _render_template(self, template_str: str, **kwargs) -> str:
        """Render email template"""
        template = Template(template_str)
        return template.render(**kwargs)
    
    # Email Templates
    SWAP_REQUEST_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #2ecc71; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .button { display: inline-block; background: #2ecc71; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            .item-card { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2ecc71; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 New Swap Request - ReWear</h1>
            </div>
            <div class="content">
                <h2>Hi {{ owner_name }}!</h2>
                
                <p><strong>{{ requester_name }}</strong> wants to swap for your item:</p>
                
                <div class="item-card">
                    <h3>{{ item_title }}</h3>
                    <p><strong>Points Value:</strong> {{ item_points }} points</p>
                    <p><strong>Condition:</strong> {{ item_condition }}</p>
                </div>
                
                {% if swap_type == 'direct_swap' %}
                <p><strong>They're offering:</strong></p>
                <div class="item-card">
                    <h3>{{ offered_item_title }}</h3>
                    <p><strong>Points Value:</strong> {{ offered_item_points }} points</p>
                </div>
                {% else %}
                <p><strong>Points Offered:</strong> {{ points_offered }} points</p>
                {% endif %}
                
                {% if requester_message %}
                <p><strong>Message from {{ requester_name }}:</strong></p>
                <blockquote style="background: white; padding: 10px; border-left: 3px solid #2ecc71;">
                    "{{ requester_message }}"
                </blockquote>
                {% endif %}
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{{ accept_url }}" class="button">✅ Accept Swap</a>
                    <a href="{{ reject_url }}" class="button" style="background: #e74c3c;">❌ Decline</a>
                </div>
                
                <p style="text-align: center;">
                    <a href="{{ view_url }}">View on ReWear</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    SWAP_ACCEPTED_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #27ae60; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Swap Accepted - ReWear</h1>
            </div>
            <div class="content">
                <div class="success">
                    <h2>Great news, {{ requester_name }}!</h2>
                    <p><strong>{{ owner_name }}</strong> accepted your swap request for <strong>{{ item_title }}</strong>!</p>
                </div>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Contact {{ owner_name }} to arrange pickup/shipping</li>
                    <li>Complete the exchange</li>
                    <li>Mark the swap as completed on ReWear</li>
                </ol>
                
                {% if owner_response %}
                <p><strong>Message from {{ owner_name }}:</strong></p>
                <blockquote style="background: white; padding: 10px; border-left: 3px solid #27ae60;">
                    "{{ owner_response }}"
                </blockquote>
                {% endif %}
                
                <p style="text-align: center;">
                    <a href="{{ view_url }}" style="display: inline-block; background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">View Swap Details</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    SWAP_COMPLETED_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #f39c12; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .celebration { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌱 Swap Completed - ReWear</h1>
            </div>
            <div class="content">
                <div class="celebration">
                    <h2>🎊 Congratulations, {{ user_name }}!</h2>
                    <p>You've successfully completed a swap for <strong>{{ item_title }}</strong></p>
                    <p style="font-size: 18px;"><strong>+{{ points_earned }} points earned!</strong></p>
                </div>
                
                <h3>🌍 Your Sustainability Impact:</h3>
                <ul>
                    <li>✅ Prevented 1 clothing item from going to waste</li>
                    <li>🔄 Extended the lifecycle of pre-loved fashion</li>
                    <li>🌱 Contributed to the circular economy</li>
                    <li>💚 Reduced environmental footprint</li>
                </ul>
                
                <p>Keep up the great work! Every swap makes a difference. 🌟</p>
                
                <p style="text-align: center;">
                    <a href="{{ dashboard_url }}" style="display: inline-block; background: #f39c12; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">View Your Dashboard</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Email sending methods
    async def send_swap_request_email(
        self,
        owner: User,
        requester: User,
        swap_data: dict
    ) -> bool:
        """Send email notification for new swap request"""
        
        if not owner.email:
            return False
        
        # Build URLs (you'd use your actual frontend URLs)
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        accept_url = f"{base_url}/swaps/{swap_data['swap_id']}/accept"
        reject_url = f"{base_url}/swaps/{swap_data['swap_id']}/reject" 
        view_url = f"{base_url}/swaps/{swap_data['swap_id']}"
        
        html_content = self._render_template(
            self.SWAP_REQUEST_TEMPLATE,
            owner_name=owner.first_name or owner.username,
            requester_name=requester.first_name or requester.username,
            item_title=swap_data.get('item_title', 'Unknown Item'),
            item_points=swap_data.get('item_points', 0),
            item_condition=swap_data.get('item_condition', 'Good'),
            swap_type=swap_data.get('swap_type', 'points_redemption'),
            offered_item_title=swap_data.get('offered_item_title', ''),
            offered_item_points=swap_data.get('offered_item_points', 0),
            points_offered=swap_data.get('points_offered', 0),
            requester_message=swap_data.get('requester_message', ''),
            accept_url=accept_url,
            reject_url=reject_url,
            view_url=view_url
        )
        
        subject = f"🔄 New swap request for your {swap_data.get('item_title', 'item')} - ReWear"
        
        return await self.send_email_async(
            to_email=owner.email,
            subject=subject,
            html_content=html_content
        )
    
    async def send_swap_accepted_email(
        self,
        requester: User,
        owner: User,
        swap_data: dict
    ) -> bool:
        """Send email notification when swap is accepted"""
        
        if not requester.email:
            return False
        
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        view_url = f"{base_url}/swaps/{swap_data['swap_id']}"
        
        html_content = self._render_template(
            self.SWAP_ACCEPTED_TEMPLATE,
            requester_name=requester.first_name or requester.username,
            owner_name=owner.first_name or owner.username,
            item_title=swap_data.get('item_title', 'Unknown Item'),
            owner_response=swap_data.get('owner_response', ''),
            view_url=view_url
        )
        
        subject = f"🎉 Your swap request was accepted! - ReWear"
        
        return await self.send_email_async(
            to_email=requester.email,
            subject=subject,
            html_content=html_content
        )
    
    async def send_swap_completed_email(
        self,
        user: User,
        swap_data: dict
    ) -> bool:
        """Send email notification when swap is completed"""
        
        if not user.email:
            return False
        
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{base_url}/dashboard"
        
        html_content = self._render_template(
            self.SWAP_COMPLETED_TEMPLATE,
            user_name=user.first_name or user.username,
            item_title=swap_data.get('item_title', 'Unknown Item'),
            points_earned=swap_data.get('points_earned', 0),
            dashboard_url=dashboard_url
        )
        
        subject = f"🌱 Swap completed! You earned {swap_data.get('points_earned', 0)} points - ReWear"
        
        return await self.send_email_async(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new users"""
        
        if not user.email:
            return False
        
        welcome_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2ecc71; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌱 Welcome to ReWear!</h1>
                </div>
                <div class="content">
                    <h2>Hi {{ user_name }}!</h2>
                    
                    <p>Welcome to ReWear - the sustainable fashion community! 🎉</p>
                    
                    <p>You've earned <strong>{{ signup_points }} welcome points</strong> to get you started!</p>
                    
                    <h3>Get Started:</h3>
                    <ul>
                        <li>📷 Upload photos of clothing items you want to swap</li>
                        <li>🔍 Browse items from other community members</li>
                        <li>🔄 Create swap requests using points or direct exchanges</li>
                        <li>🌍 Join the sustainable fashion movement!</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="{{ dashboard_url }}" style="display: inline-block; background: #2ecc71; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Start Swapping</a>
                    </p>
                    
                    <p>Happy swapping! 🌟</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{base_url}/dashboard"
        
        html_content = self._render_template(
            welcome_template,
            user_name=user.first_name or user.username,
            signup_points=getattr(settings, 'SIGNUP_BONUS_POINTS', 100),
            dashboard_url=dashboard_url
        )
        
        subject = "🌱 Welcome to ReWear - Start your sustainable fashion journey!"
        
        return await self.send_email_async(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )


# Global email service instance
email_service = EmailService()
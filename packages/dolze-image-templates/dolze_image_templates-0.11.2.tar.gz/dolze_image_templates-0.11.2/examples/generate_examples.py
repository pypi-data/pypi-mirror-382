"""
Example script demonstrating how to use the Dolze Templates library.

This script shows how to:
1. Load templates from JSON files
2. Render templates with different data
3. Save the generated images
"""

from cgitb import text
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import the package
import sys

sys.path.append(str(Path(__file__).parent.parent))

from dolze_image_templates import (
    get_template_registry,
    configure,
    get_font_manager,
)

# Initialize font manager to scan for fonts
font_manager = get_font_manager()
print("Font manager initialized. Available fonts:", font_manager.list_fonts())

# Configure the library
configure(
    templates_dir=os.path.join(
        os.path.dirname(__file__), "..", "dolze_image_templates", "templates"
    ),
    output_dir=os.path.join(os.path.dirname(__file__), "output"),
)


async def generate_business_template(templateName: str):
    """Generate a business template post."""
    # Get the template registry
    registry = get_template_registry()
    template_data = {
        "cta_text": "LEARN MORE",
        "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
        "image_url": "https://images.pexels.com/photos/235986/pexels-photo-235986.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "cta_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
        "heading": "plan your day in a snap",
        "subheading": "Driving success",
        "contact_email": "contact@business.com",
        "contact_phone": "+1-800-555-1234",
        "website_url": "dolze.ai /download",
        "quote": "The only way to do great work is to love what you do.",
        "theme_color": "#44EC9D",
        "user_avatar": "https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
        "user_name": "Alex Johnson",
        "user_title": "Marketing Director, TechCorp",
        "testimonial_text": "This product has completely transformed how we works. The intuitive interface and powerful features have saved us countless hours.",
    }
    # Template data mapping
    if templateName == "calendar_app_promo":
        template_data = {
            "cta_text": "LEARN MORE",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "image_url": "https://www.calendar.com/wp-content/uploads/2019/09/CalendarAndroidApp.png.webp",
            "cta_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
            "heading": "streamline your business with Dolze",
            "subheading": "Your AI-powered business assistant",
            "contact_email": "contact@dolze.ai",
            "contact_phone": "+1-800-555-1234",
            "website_url": "dolze.ai/download",
            "quote": "Simplify your business, amplify your success.",
            "theme_color": "#ffc524",
            "user_avatar": "https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "user_name": "Maya Patel",
            "user_title": "Founder, Artisan Gems",
            "testimonial_text": "Dolze transformed how I manage my jewelry store. The AI team handles marketing and customer care seamlessly.",
        }
  
  
  
    elif templateName == "education_info" or templateName == "education_info_2":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "product_name": "Dolze AI Managers",
            "product_info": "AI-powered assistants that automate marketing, customer care, and operations for small businesses.",
            "author": "@dolze_ai",
            "read_time": "4",
            "image_url": "https://img.freepik.com/free-photo/portrait-young-businesswoman-holding-eyeglasses-hand-against-gray-backdrop_23-2148029483.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "logo_url": "https://img.freepik.com/free-vector/gradient-s-letter-logo_343694-1365.jpg",
        }
    
    elif templateName == "product_promotion":
        template_data = {
            "image_url": "https://media.licdn.com/dms/image/v2/D4D12AQGnbgq78a4LMg/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1677634984855?e=1755734400&v=beta&t=PS0JBTOx91C-z1Tb4Ky4NOnQeRosuW-7i1GIDUj088o",
            "heading": "Dolze AI Managers",
            "subheading": "Your digital business team made simple witn Dolze ai. Your digital business team made simple witn Dolze ai.Your digital business team made simple witn Dolze ai.",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg?w=200&h=200&white=true",
            "cta_text": "LEARN MORE",
            "website_url": "dolze.ai/download",
            "theme_color": "#ffc524",
        }
   
    elif templateName == "coming_soon_page":
        template_data = {
            "header_text": "Dolze is Coming",
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/download",
            "contact_email": "contact@dolze.ai",
        }
    elif templateName == "coming_soon_post_2":
        template_data = {
            "text": "3 days left until Dolze launches to simplify your business!",
            "cta_text": "STAY TUNEDSTAY TUNEDSTAY TUNEDSTAY TUNED",
            "website_url": "dolze.ai/download",
        }
    elif templateName == "hiring_post":
        template_data = {
            "theme_color": "#ffc524",
            "heading": "Join Our Team",
            "subheading": "Passionate about AI and business? We want you!",
            "job_title": "Social Media Lead",
            "website_url": "dolze.ai/careers",
            "company_name": "Dolze",
            "cta_text": "Apply Now!",
        }
  
    elif templateName == "product_marketing":
        template_data = {
            "social_handle": "@dolze.ai",
            "heading": "Unlock AI-Driven Growth",
            "description": "Transform your marketing with Dolze.ai—an AI-powered SaaS that analyzes data, crafts high-performing campaigns, and scales your reach effortlessly.",
            "background_image_url": "https://img.freepik.com/free-photo/open-laptop-with-glowing-screen-notepad-table-night_169016-53665.jpg?t=st=1752265269~exp=1752268869~hmac=ffb2b5be8ce1b9130640bfeb4d11ec00d46974ad6c576e0857b3b6bbdffb7e65&w=2000",
        }

        # https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/mbcEtwwJKCf7jn4GnfzFm1thlhC3/6829afe6925fb5ef8c087942/business_assets/BlackRedGeometricBusinessMarketingInstagramPost.png

        # {
        #     "product_name": "Dolze AI Subscription",
        #     "sale_text": "Flat 15% OFF",
        #     "product_description": "Automate your business with Dolze’s AI managers.",
        #     "cta_text": "BUY NOW",
        #     "sale_end_text": "Ends 10th July at midnight",
        #     "sale_heading": "Flash Sale!"
        # }
  
        
    
    elif templateName == "product_showcase_3":
        template_data = {
            "product_name": "Dolze AI Assistant",
            "product_description": "Start automating your business today for just $15.99/month.",
            "cta_text": "Get Started",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
            "website_url": "dolze.ai/shop",
        }
    elif templateName == "quote_template":
        template_data = {
            "quote": "The only way to do your best work is to love what you do and let Dolze handle the rest.",
            "social_handle": "@dolze_ai",
        }
    elif templateName == "product_service_minimal":
        template_data = {
            "text": "Simplify your business with Dolze’s AI-powered services.",
            "website_url": "dolze.ai/shop",
            "product_image": "https://img.freepik.com/free-photo/furniture-background-clean-wall-wood_1253-666.jpg?t=st=1751691647~exp=1751695247~hmac=d5a191ec06d19843dcb271039a8e46a0374789e5a09714f0335e34139da25e43&w=1380",
        }
    elif templateName == "product_showcase_4":
        template_data = {
            "offer_text": "Only with Dolze",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
            "website_url": "dolze.ai/shop",
            "theme_color": "#ffc524",
        }
    elif templateName == "coming_soon":
        template_data = {
            "background_image_url": "https://img.freepik.com/free-photo/close-up-meat-with-baked-potatoes-eggplant-tomato-pepper-decorated-with-pomegranate-wooden-bark_176474-2443.jpg?t=st=1751704275~exp=1751707875~hmac=1bb3b262f6a44e5898fcf5f70fb1be071981253d1b1db308ac972cf7f0e9e0ab&w=1380",
            "text": "COMING SOON",
            "website_url": "dolze.ai",
            "business_name": "Dolze AI",
            "logo_url": "https://img.freepik.com/free-vector/detailed-chef-logo-template_23-2148987940.jpg?t=st=1751704940~exp=1751708540~hmac=d327a7d9b9b689564d411580764d3308e521d60ea9b470ce9ed0c75b978d29d7&w=1380",
        }
    
    elif templateName == "product_showcase_5":
        template_data = {
            "heading": "Healthy living happy living",
            "subheading": "Healthy eating is about choosing fresh, balanced meals to nourish your body and mind. Start small, and enjoy the benefits every day!",
            "cta_text": "Book Now",
            "contact_number": "+09876543211",
            "website_url": "dolze.ai",
            "product_image": "https://rukminim2.flixcart.com/image/100/100/xif0q/mobile/k/l/l/-original-imagtc5fz9spysyk.jpeg?q=90",
        }
    elif templateName == "brand_info":
        template_data = {
            "product_image": "https://plus.unsplash.com/premium_photo-1677087121676-2acaaae5b3c8?w=1200&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8b2ZmaWNlfGVufDB8MnwwfHx8MA%3D%3D",
            "heading": "build a brand in 10 days",
            "subheading": "build a brand in under 10 days if not return the money to usif not return the money to usif not return the money to us",
            "cta_text": "Book Now Today",
            "website_url": "dolze.ai",
            "theme_color": "#214aff",
        }
    elif templateName == "brand_info_2":
        template_data = {
            "service_hook": "Require a brand new",
            "service_name": "Website ?",
            "content": "our team of expert devlopers will make sure you will get the best website available in the market",
            "contact_number": "+123-456-7890",
            "website_url": "www.dolze.ai/careers",
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "contact_email": "contact@dolze.ai",
        }
    elif templateName == "product_sale_2":
        template_data = {
            "theme_color": "#fffdf7",
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "heading": "Digital planner",
            "usp1": "Undated Planner",
            "usp2": "Hyperlinked Pages",
            "cta_text": "Book Now",
            "product_highlights": "300+ pages",
            "social_handle": "@dolze_ai",
            "business_name": "Dolze AI",
        }
   
    elif templateName == "event_alert":
        template_data = {
            "company_name": "Dolze AI",
            "event_type": "FREE WEBINAR",
            "event_date": "July 16",
            "event_time": "10:00 AM - 12:00 PM",
            "event_venue": "Online",
            "event_highlight": "How Dolze saves time for you to make your business successful",
            "register_details": "Registration Link in bio",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
        }
    elif templateName == "sale_alert":
        template_data = {
            "sale_heading": "Technology Sale",
            "sale_description": "Special Sale Only in August",
            "cta_text": "Shop Now!",
            "website_url": "www.dolze.ai",
            "sale_text": "30% off",
            "product_image": "https://static.vecteezy.com/system/resources/previews/055/473/101/large_2x/cute-cartoon-teddy-bear-sitting-perfect-for-children-s-products-free-png.png",
        }
    elif templateName == "testimonials":
        template_data = {
            "product_image": "https://img.freepik.com/free-photo/portrait-white-man-isolated_53876-40306.jpg?t=st=1752413811~exp=1752417411~hmac=afeea5e512a3cef81bfab9b893856637b99d6b4a617883396766b8ced0981805&w=2000",
            "name": "Sagar Giri",
            "greeting": "Meet our developers",
            "designation": '" I have had a passion for coding since I was a kid. I have developed in the field of software and now with Rimberio I help our customers solve their digital product problems. "',
            "social_handle": "@dolze_ai",
        }
    elif templateName == "event_announcement":
        template_data = {
            "event_image": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/mbcEtwwJKCf7jn4GnfzFm1thlhC3/68a0f60bd5f7b8aa0112a695/image/3e46700f-b5bd-4b0d-bb17-e3821ee99d87.png",
            "event_name": "Sale Alert",
            "company_name": "Dolze AI",
            "event_description": "Sale starting on our grocery store for all users on all platforms",
        }

   
    elif templateName == "product_promotion_6":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "button_text": "Learn more today",
            "excerpt": "Average baby\nor super baby?",
            "text_subtext": "The choice is yours",
            "logo_url": "https://i.postimg.cc/d3qQry0D/Frame-1244832596.png",
            "background_image_url": "https://i.postimg.cc/wvmG6fcd/image-10.png",
            "baby_image": "https://i.postimg.cc/vZ78mhhf/image-11.png",
            "gradient_bg": "https://i.postimg.cc/cJgPk4zh/Frame-1244832597.png",
        }

    elif templateName == "super_king_burgers_template":
        template_data = {
            "background_image_url": "https://i.postimg.cc/bJzN2BL1/jhunelle-francis-sardido-PPtcyr-AB5-UQ-unsplash.jpg",
            "badge_number": "Super Burgers",
            "subtitle": "CULINARY EXPLORATIONS",
            "main_title": "Super King Burgers",
            "description": "Discover the most unique flavors and try new food experiences. Limited spots available!",
            "button_text": "ORDER NOW",
            "theme_color": "#FFD700",
            "gradient_bg": "https://i.postimg.cc/WbfFcT8C/Frame-1244832597.png",
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
        }

    elif templateName == "product_poster":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "headline": "GET 25% OFF",
            "subtitle": "Healthy Snacking Made Easy!",
            "cta_text": "Book now",
            "product_image": "https://elements-resized.envatousercontent.com/elements-cover-images/8462fe84-c870-4d77-8399-7d3bc3151987?w=710&cf_fit=scale-down&q=85&format=auto&s=8272500a78acfd2fa2a5f04dc0a85005133db0d24f4ee4a51fe22bc752180eaf",
            "theme_color": "#F7A824",
        }

    elif templateName == "sales_offer_poster":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "headline": "GET 25% OFF!",
            "subtitle": "Healthy Snacking Made Easy!",
            "cta_text": "BESTEL NU",
            "background_image_url": "https://i.postimg.cc/cCN5RtSB/image-24.png",
            "juice_image_url": "https://i.postimg.cc/9MPBjx6y/Frame-1244832601.png",
            "theme_color": "#383838",
        }

 
    elif templateName == "food_offer_promo":
        template_data = {
            "background_image": "https://i.postimg.cc/ydBhzwjk/image-29.png",
            "logo_url": "https://cdn.prod.website-files.com/65d0a7f29d4c760c3869e2a2/65ec89c76f839f619b94dc55_refyne-dark-logo.svg",
            "product_image": "https://i.postimg.cc/PfZqsPcV/image-31.png",
            "product_name": "GRILLED CHICKEN",
            "product_description": "Description of the chicken dish and its ingredients",
            "price": "$14",
            "contact_text": "Contact us on ",
            "price_note": "ONLY",
            "contact_number": "987 6543 3210",
            "address_line1": "123 STREET, AREA NAME",
            "address_line2": "YOUR CITY, STATE",
            "username": "@username",
            "theme_color": "#F4A300",
        }

  

    elif templateName == "food_menu_promo":
        template_data = {
            "product_image": "https://i.postimg.cc/PfZqsPcV/image-31.png",
            "product_name": "UltraBoost Running Shoes",
            "product_description": "Lightweight and responsive running shoes with superior cushioning for maximum comfort",
            "price": "$129.99",
            "cta_text": "Shop Now",
            "theme_color": "#00BCD4",
            "shoe_image_url": "https://i.postimg.cc/PfZqsPcV/image-31.png",
        }

    elif templateName == "reward_program_template":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "heading": "Loyalty Rewards",
            "subheading": "Earn points with every purchase",
            "points": "250",
            "theme_color": "#795548",
            "cta_text": "Redeem Now",
        }
    elif templateName == "neon_creative_agency":
        template_data = {
            "website_url": "www.reallygreatsite.com",
            "social_handle": "@reallygreatsite",
            "description": "We are a modern creative agency that pushes the boundaries of traditional marketing. Our edgy approach to branding sets us apart, and our team of talented creatives is dedicated to bringing your vision to life. From strategy and identity to motion design and content, we craft bold work that wins attention and drives growth.",
            "studio_name": "Studio Shodwe",
            "address": "123 Anywhere St., Any City, ST 12345",
        }
    
    elif templateName == "faq_template":
        template_data = {
            "question1": "How do I start a return or exchange?",
            "answer1": "Email us your order number to initiate the return or exchange process.",
            "question2": "What if I received a damaged item?",
            "answer2": "Send us photos right away. We'll arrange a replacement or full refund.",
            "company_name": "Dolze AI",
            "website_url": "www.dolze.ai",  
            "background_image_url": "https://i.ibb.co/201rrb9P/Green-Geometric-Returns-Exchange-FAQs-Instagram-Post-1.png",
        }

    elif templateName == "customer_retention_strategies":
        template_data = {
            "heading": "6 Strategies for",
            "title": "Customer Retention",
"card1": "Make it simple and quick for people to buy.",
"card2": "Give good and useful products with help.",
"card3": "Be kind, patient and helpful to people.",
"card4": "Make fun reward plans for happy buyers.",
"card5": "Always do what you say you will do about it.",
"card6": "Ask happy people to tell more friends.",
            "website_url": "www.reallygreatsite.com",

        }
    elif templateName == "faq_white_post":
        template_data = {
            "q1": "Are sale items eligible for return?",
            "a1": "Sale items are final and cannot be returned or exchanged.",
            "q2": "What is your return and refund policy?",
            "a2": "We accept returns within 14 days of delivery with original condition.",
            "brand_name": "Aldenaire & Partners",
        }

    elif templateName == "search_services_listing":
        template_data = {
            "item1": "Online Payment Tracking",
            "item2": "Automatic Bank Feeds",
            "item3": "Collect Digital Payments",
            "item4": "Online Invoices & Quotes",
            "cta_text": "reallygreatsite.com",
        }


    elif templateName == "why_us_reasons":
        template_data = {
            "website_left": "REALLYGREATSITE.COM",
            "social_right": "@REALLYGREATSITE",
            "reason1_title": "Expertise and Experience",
            "reason1_desc": "Our team consists of seasoned professionals with specialized expertise to produce top-quality results.",
            "reason2_title": "Innovative Solutions",
            "reason2_desc": "We utilize the latest technologies and creative strategies to deliver innovative and effective outcomes for your projects.",
            "reason3_title": "Customer-Centric Approach",
            "reason3_desc": "We prioritize your needs and preferences, providing personalized solutions and exceptional customer service.",
            "reason4_title": "Reliability and Trust",
            "reason4_desc": "We are dedicated to transparency, meeting deadlines, and fostering open communication to build a reliable partnership.",
            "reason5_title": "Competitive Pricing",
            "reason5_desc": "We offer high-quality services at a competitive price, ensuring you get the best value for your investment.",
        }

    elif templateName == "hiring_minimal_red":
        template_data = {
            "hiring_title": "We're Hiring",
            "role_title": "Marketers",
            "bullet1": "Do you have a passion for marketing?",
            "bullet2": "Do you have experience in marketing campaigns?",
            "bullet3": "Do you want to join a dynamic and innovative team?",
            "cta_text": "If yes, then apply now!",
            "apply_instruction": "Send your CV at email us:",
            "apply_email": "hello@reallygreatsite.com",
        }

    elif templateName == "testimonial_card":
        template_data = {
            "author_name": "Olivia Wilson",
            "quote": "Social media can also be used to share interesting facts, inspiring true stories, helpful tips, useful knowledge, and other important information.",
            "author_role": "CEO of Ginyard International Co.",
            "company_name":"ReallyGreatCompany"
        }

    elif templateName == "myth_or_fact":
        template_data = {
            "main_title_line1": "Myth or Fact",
            "main_title_line2": "Social Media",
            "subtitle": "LET’S CLEAR UP COMMON SOCIAL MEDIA ASSUMPTIONS",
            "myth": "Myth",
            "fact": "Fact",
            "myth1": "You must post daily",
            "fact1": "You must post daily",
            "myth2": "More hashtags = more views",
            "fact2": "More hashtags = more views",
            "myth3": "You need to go viral",
            "fact3": "You need to go viral",
            "myth4": "Strategy = trend following",
            "fact4": "Strategy = trend following",
            "footer_handle": "@reallygreatsite",
        }

    elif templateName == "process_steps":
        template_data = {
            "main_title": "Our Process",
            "step1_text": "Develop a marketing plan that's in line with the company's goal.",
            "step2_text": "Identify your target audience & where they like to hang out.",
            "step3_text": "Research & analyze your social media competitors",
            "step4_text": "Make a hyper targeted campaign to boost your account's growth.",
            "website_url": "www.reallygreatsite.com",


        }

    elif templateName == "spotlight_launching":
        template_data = {
            "main_title": "Launching Soon",
            "subheading": "Countdown",
            "days": "10",
            "hours": "09", 
            "minutes": "25",
            "cta_text": "Stay Tuned!"
        }

    elif templateName == "spotlight_launching_text":
        template_data = {
            "company_name": "Larana, Inc.",
            "headline": "LAUNCHING\nSOON",
            "description": "Get ready, because something amazing is coming your way! Our launch is just around the corner",
            "website_url": "www.reallygreatsite.com",
        }


    elif templateName == "marketing_trends_list":
        template_data = {
            "heading_word1": "MARKETING",
            "heading_word2": "TRENDS",
            "trend1": "User-generated content marketing is only going up.",
            "trend2": "Hyper-personalization — get creative with your personalization.",
            "trend3": "Human content and storytelling. We love the real stories.",
            "handle": "@ReallyGreatSite",
        }

    elif templateName == "contact_us_overlay":
        template_data = {
            "phone": "123-456-7890",
            "email": "hello@reallygreatsite.com",
            "website": "www.reallygreatsite.com",
            "address": "123 Anywhere St., Any City",
            "company_name": "Dolze AI"

        }


    elif templateName == "social_media":
        template_data = {
            "headline_primary": "Social Media",
            "headline_accent": "Marketing",
            "subheading": "Transform your online presence with expert strategies",
            "bullet1": "Increased Visibility",
            "bullet2": " Better Engagement",
            "bullet3": " Higher Conversion Rates",
            "cta_text": "Visit Us For More",
            "website_url": "reallygreatsite.com",
            "studio_name": "Studio Shodwe",
        }


    elif templateName == "social_media_2":
        template_data = {
            "title": "What Exactly Is Marketing?",
            "item1": "Research",
            "item2": "Distribution",
            "item3": "Product & Services",
            "item4": "Pricing",
            
            "item5": "Promotion",
            "cta_text": "Visit Us For More",
            "website_url": "reallygreatsite.com",
        }
    elif templateName == "stocks_dividend_post":
        template_data = {
            "brand_name": "Stock.Academy",
            "title_line1": "What is a",
            "title_line2_accent": "Dividend Stock?",
            "body_text": "A dividend stock gives you regular income from company profits—paid out to shareholders. Think of it as your investment earning you 'rent' every quarter.",
            "footer_question": "Want to learn passive income strategies?",
            "website_url": "stockacademy.com"
        }
    
    elif templateName == "announcement_template":
        template_data = {
            "announcement_header": "OFFICIAL ANNOUNCEMENT",
            "main_announcement_text": "We are partnering with",
            "partner_company": "Rolk Inc.",
            "details_text": "More details on",
            "website_url": "www.reallygreatsite.com",
            "company_name": "WeisenhamTech"
        }

    elif templateName == "add_branding":
        template_data = {
            "background_image_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1080&h=1080&fit=crop",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "company_name": "GDX PRIVATE SECURITY LIMITED",
        }

    # Render the template with the data
    output_path = os.path.join("output", f"{templateName}.png")
    rendered_image = await registry.render_template(
        templateName,
        template_data,
        output_path=output_path,
    )

    print(f"Template saved to {os.path.abspath(output_path)}")
    return rendered_image


async def main():
    """Generate all example templates."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Generate all templates
        templates = [
            #"event_alert",
            # "calendar_app_promo",
            # "education_info",
            #  "education_info_2",
            #  "product_promotion",
       
            # "quote_template",
            # "product_showcase_3",
           
            # "coming_soon_page",
            #  "coming_soon_post_2",
            #"coming_soon",
            #  "product_marketing",
            # "brand_info_2",
            # "brand_info",
            # "product_sale_2",
            #     "product_service_minimal",
            # "spotlight_launching",
            # "testimonials",
            # "hiring_post",
            #  "product_showcase_5",
            #  "product_showcase_4",
            #  "event_announcement",
            #  "product_poster",
            # "sales_offer_poster",
            # "food_offer_promo",
            #  "product_promotion_6",
            #  "food_menu_promo",
            # "reward_program_template",
            # "sale_alert",

            # "search_services_listing",


            # "search_services_listing",
            # "neon_creative_agency"
            # "faq_template",
            # "spotlight_launching_text",
            # "social_media",
            # "neon_creative_agency",
            # "contact_us_overlay",


            # "search_services_listing",
            # "why_us_reasons"
            # "neon_creative_agency"
            # "faq_template",
            # "spotlight_launching_text"
            # "social_media"
            # "neon_creative_agency"

            # "search_services_listing"
            # "neon_creative_agency"
            # "faq_template",
            # "spotlight_launching_text"
            # "social_media"
            # "neon_creative_agency"

            # "faq_template",
            # "social_media_2",

            # "hiring_minimal_red",

            # "testimonial_card",


            # "social_media_2",
            # "myth_or_fact"


            # "social_media_2",
            # "process_steps"

            # "social_media_2"



            # "search_services_listing",
            # "customer_retention_strategies",

            # "neon_creative_agency"
            # "faq_template",
            # "spotlight_launching_text",
            # "social_media",
            # "neon_creative_agency",

            # "marketing_trends_list",

            # "faq_template",
            # "spotlight_launching_text",
            # "social_media",
            # "faq_white_post",
            # "spotlight_launching_text",
            # "social_media",
            # "neon_creative_agency",

            # "faq_template",
            # "stocks_dividend_post",





            # "announcement_template",

            "add_branding",





        ]

        for template in templates:
            await generate_business_template(template)

        print("\nAll examples generated successfully!")
    except Exception as e:
        print(f"\nError generating examples: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

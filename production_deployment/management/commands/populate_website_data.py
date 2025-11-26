from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, datetime
from accounts.models import (
    Footer, AboutUs, PageContent, Feature, SiteConfiguration, 
    TermsOfService, PrivacyPolicy
)
from tenants.models import SubscriptionPlan
import json
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate comprehensive website data for production deployment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting comprehensive website data population...'))

        # Create superuser if not exists
        self.create_superuser()
        
        # Load and create all website content
        self.load_exported_data()

        self.stdout.write(self.style.SUCCESS('Website data population completed successfully!'))

    def load_exported_data(self):
        """Load data from exported JSON file or use defaults"""
        data_file = 'website_data_export.json'
        
        if os.path.exists(data_file):
            self.stdout.write(self.style.SUCCESS('Loading data from export file...'))
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.create_from_export(data)
        else:
            self.stdout.write(self.style.WARNING('Export file not found, using default data...'))
            self.create_default_data()

    def create_from_export(self, data):
        """Create all data from exported JSON"""
        # Create Footer
        if 'footer' in data:
            footer_data = data['footer']
            footer, created = Footer.objects.get_or_create(
                pk=1,
                defaults=footer_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Footer created from export'))
            else:
                # Update existing footer
                for key, value in footer_data.items():
                    setattr(footer, key, value)
                footer.save()
                self.stdout.write(self.style.SUCCESS('✓ Footer updated from export'))

        # Create About Us
        if 'about_us' in data:
            about_data = data['about_us']
            about, created = AboutUs.objects.get_or_create(
                pk=1,
                defaults=about_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ About Us created from export'))
            else:
                for key, value in about_data.items():
                    setattr(about, key, value)
                about.save()
                self.stdout.write(self.style.SUCCESS('✓ About Us updated from export'))

        # Create Features
        if 'features' in data:
            Feature.objects.all().delete()  # Clear existing
            for feature_data in data['features']:
                Feature.objects.create(**feature_data)
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(data["features"])} features from export'))

        # Create Page Contents
        if 'page_contents' in data:
            for page_data in data['page_contents']:
                page, created = PageContent.objects.get_or_create(
                    page_name=page_data['page_name'],
                    defaults={
                        'page_title': page_data['page_title'],
                        'page_subtitle': page_data['page_subtitle']
                    }
                )
                if not created:
                    page.page_title = page_data['page_title']
                    page.page_subtitle = page_data['page_subtitle']
                    page.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created/Updated {len(data["page_contents"])} page contents from export'))

        # Create Site Configuration
        if 'site_config' in data:
            config_data = data['site_config']
            config, created = SiteConfiguration.objects.get_or_create(
                pk=1,
                defaults=config_data
            )
            if not created:
                for key, value in config_data.items():
                    setattr(config, key, value)
                config.save()
            self.stdout.write(self.style.SUCCESS('✓ Site configuration created/updated from export'))

        # Create Subscription Plans
        if 'subscription_plans' in data:
            for plan_data in data['subscription_plans']:
                plan, created = SubscriptionPlan.objects.get_or_create(
                    name=plan_data['name'],
                    defaults=plan_data
                )
                if not created:
                    for key, value in plan_data.items():
                        if key != 'name':  # Don't update name as it's the lookup key
                            setattr(plan, key, value)
                    plan.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created/Updated {len(data["subscription_plans"])} subscription plans from export'))

        # Create Terms of Service
        if 'terms_of_service' in data:
            terms_data = data['terms_of_service']
            terms_data['effective_date'] = datetime.fromisoformat(terms_data['effective_date']).date()
            
            # Deactivate existing terms
            TermsOfService.objects.filter(is_active=True).update(is_active=False)
            
            terms = TermsOfService.objects.create(**terms_data)
            self.stdout.write(self.style.SUCCESS('✓ Terms of Service created from export'))

        # Create Privacy Policy
        if 'privacy_policy' in data:
            privacy_data = data['privacy_policy']
            privacy_data['effective_date'] = datetime.fromisoformat(privacy_data['effective_date']).date()
            
            # Deactivate existing policies
            PrivacyPolicy.objects.filter(is_active=True).update(is_active=False)
            
            privacy = PrivacyPolicy.objects.create(**privacy_data)
            self.stdout.write(self.style.SUCCESS('✓ Privacy Policy created from export'))

    def create_superuser(self):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@aurastay.com',
                password='admin123',
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser created'))
        else:
            self.stdout.write(self.style.WARNING('✓ Superuser already exists'))

    def create_default_data(self):
        """Create default data if export file not available"""
        self.create_footer()
        self.create_about_us()
        self.create_page_contents()
        self.create_features()
        self.create_site_configuration()
        self.create_subscription_plans()
        self.create_terms_and_privacy()

    def create_footer(self):
        footer, created = Footer.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'AuraStay',
                'company_description': 'The world\'s most advanced hotel management platform, designed for luxury hospitality.',
                'email': 'info@aurastay.com',
                'phone': '+1 (555) 123-4567',
                'address_line1': '123 Business Ave',
                'address_line2': 'New York, NY 10001',
                'copyright_line1': '© 2025 AuraStay. All rights reserved.',
                'copyright_line2': 'Design: MA Qureshi | Development: Momin Ali'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Footer content created'))
        else:
            self.stdout.write(self.style.WARNING('✓ Footer content already exists'))

    def create_about_us(self):
        about, created = AboutUs.objects.get_or_create(
            pk=1,
            defaults={
                'purpose_title': 'Our Purpose: Why AuraStay Exists',
                'mission_statement': 'To revolutionize hotel management through innovative technology that empowers hospitality professionals to deliver exceptional guest experiences.',
                'mission_description': 'We believe that great hospitality starts with great tools. Our mission is to provide hotel owners and staff with the most intuitive, powerful, and reliable management platform available.',
                'problem_description': 'Traditional hotel management systems are outdated, complex, and expensive. They often require extensive training, lack modern features, and fail to integrate with today\'s digital ecosystem.',
                'solution_description': 'AuraStay provides a comprehensive, cloud-based hotel management solution that\'s easy to use, feature-rich, and affordable. Our platform integrates all aspects of hotel operations into one seamless experience.',
                'global_architecture_text': 'Built on enterprise-grade cloud infrastructure with global redundancy and 99.9% uptime guarantee.',
                'data_security_text': 'Bank-level encryption, GDPR compliance, and ISO 27001 certified security protocols protect your data.',
                'modern_tech_text': 'Cutting-edge technology stack with real-time updates, mobile optimization, and AI-powered insights.',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ About Us content created'))
        else:
            self.stdout.write(self.style.WARNING('✓ About Us content already exists'))

    def create_page_contents(self):
        pages = [
            ('super_admin_dashboard', 'Super Admin Dashboard', 'Comprehensive system overview and management controls'),
            ('owner_dashboard', 'Hotel Owner Dashboard', 'Manage your hotel operations and monitor performance'),
            ('employee_dashboard', 'Employee Dashboard', 'Access your daily tasks and hotel information'),
            ('profile', 'User Profile', 'Manage your account settings and personal information'),
            ('about', 'About AuraStay', 'Learn more about our mission and technology'),
            ('landing', 'Welcome to AuraStay', 'The future of hotel management is here'),
            ('login', 'Login to AuraStay', 'Access your hotel management dashboard'),
        ]

        for page_name, title, subtitle in pages:
            page, created = PageContent.objects.get_or_create(
                page_name=page_name,
                defaults={
                    'page_title': title,
                    'page_subtitle': subtitle
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Page content created: {page_name}'))

    def create_features(self):
        features_data = [
            ('Smart Reservations', 'Advanced booking system with real-time availability, automated confirmations, and guest communication tools.', 'fas fa-calendar-check', 'blue', 1),
            ('Guest Management', 'Comprehensive CRM system to track guest preferences, history, and personalized service delivery.', 'fas fa-users', 'green', 2),
            ('Analytics & Reports', 'Powerful business intelligence with revenue tracking, occupancy analytics, and performance insights.', 'fas fa-chart-line', 'purple', 3),
            ('Housekeeping Management', 'Streamlined room status tracking, cleaning schedules, and maintenance coordination.', 'fas fa-broom', 'yellow', 4),
            ('Billing & Payments', 'Integrated payment processing, invoicing, and financial reporting with multiple payment methods.', 'fas fa-credit-card', 'indigo', 5),
            ('Mobile Optimization', 'Full mobile responsiveness allowing staff to manage operations from any device, anywhere.', 'fas fa-mobile-alt', 'pink', 6),
            ('Security & Compliance', 'Enterprise-grade security with data encryption, backup systems, and compliance management.', 'fas fa-shield-alt', 'red', 7),
            ('Customization', 'Flexible system configuration to match your hotel\'s unique workflows and branding requirements.', 'fas fa-cog', 'gray', 8),
        ]

        for title, description, icon, color, order in features_data:
            feature, created = Feature.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'icon': icon,
                    'color': color,
                    'order': order,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Feature created: {title}'))

    def create_site_configuration(self):
        config, created = SiteConfiguration.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'AuraStay',
                'site_title': 'AuraStay - Hotel Management System',
                'site_description': 'The world\'s most advanced hotel management platform'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Site configuration created'))
        else:
            self.stdout.write(self.style.WARNING('✓ Site configuration already exists'))

    def create_subscription_plans(self):
        plans_data = [
            ('Starter', 'Perfect for small hotels and B&Bs', 29, 290, True, 25, 2, 5, False, False),
            ('Professional', 'Ideal for mid-size hotels', 79, 790, False, 100, 5, 20, True, True),
            ('Enterprise', 'Complete solution for large hotels', 199, 1990, False, 500, 20, 100, True, True),
            ('Premium', 'Ultimate package with all features', 399, 3990, False, 1000, 50, 500, True, True),
        ]

        for name, desc, monthly, yearly, trial, rooms, managers, reports, analytics, support in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'price_monthly': monthly,
                    'price_yearly': yearly,
                    'is_free_trial': trial,
                    'max_rooms': rooms,
                    'max_managers': managers,
                    'max_reports': reports,
                    'has_advanced_analytics': analytics,
                    'has_priority_support': support,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Subscription plan created: {name}'))

    def create_terms_and_privacy(self):
        # Terms of Service
        terms_content = """
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using AuraStay's hotel management platform, you accept and agree to be bound by the terms and provision of this agreement.</p>

        <h2>2. Service Description</h2>
        <p>AuraStay provides a comprehensive hotel management software solution including but not limited to:</p>
        <ul>
            <li>Reservation management system</li>
            <li>Guest relationship management</li>
            <li>Billing and payment processing</li>
            <li>Housekeeping and maintenance tracking</li>
            <li>Analytics and reporting tools</li>
        </ul>

        <h2>3. User Responsibilities</h2>
        <p>Users are responsible for:</p>
        <ul>
            <li>Maintaining the confidentiality of account credentials</li>
            <li>Ensuring accurate data entry and management</li>
            <li>Complying with applicable laws and regulations</li>
            <li>Proper use of the platform in accordance with these terms</li>
        </ul>

        <h2>4. Payment Terms</h2>
        <p>Subscription fees are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law.</p>

        <h2>5. Data Security</h2>
        <p>We implement industry-standard security measures to protect your data. However, no system is 100% secure, and users acknowledge this inherent risk.</p>

        <h2>6. Limitation of Liability</h2>
        <p>AuraStay's liability is limited to the amount paid for the service in the preceding 12 months.</p>

        <h2>7. Termination</h2>
        <p>Either party may terminate this agreement with 30 days written notice. Upon termination, access to the platform will be revoked.</p>

        <h2>8. Contact Information</h2>
        <p>For questions about these terms, contact us at legal@aurastay.com</p>
        """

        terms, created = TermsOfService.objects.get_or_create(
            is_active=True,
            defaults={
                'title': 'Terms of Service',
                'content': terms_content,
                'effective_date': date.today(),
                'version': '1.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Terms of Service created'))

        # Privacy Policy
        privacy_content = """
        <h2>1. Information We Collect</h2>
        <p>We collect information you provide directly to us, such as:</p>
        <ul>
            <li>Account registration information</li>
            <li>Hotel and guest data you input into our system</li>
            <li>Communication preferences and support requests</li>
            <li>Payment and billing information</li>
        </ul>

        <h2>2. How We Use Your Information</h2>
        <p>We use the information we collect to:</p>
        <ul>
            <li>Provide, maintain, and improve our services</li>
            <li>Process transactions and send related information</li>
            <li>Send technical notices and support messages</li>
            <li>Respond to your comments and questions</li>
        </ul>

        <h2>3. Information Sharing</h2>
        <p>We do not sell, trade, or otherwise transfer your personal information to third parties except:</p>
        <ul>
            <li>With your explicit consent</li>
            <li>To comply with legal obligations</li>
            <li>To protect our rights and safety</li>
            <li>With trusted service providers under strict confidentiality agreements</li>
        </ul>

        <h2>4. Data Security</h2>
        <p>We implement appropriate security measures including:</p>
        <ul>
            <li>Encryption of data in transit and at rest</li>
            <li>Regular security audits and updates</li>
            <li>Access controls and authentication systems</li>
            <li>Employee training on data protection</li>
        </ul>

        <h2>5. Data Retention</h2>
        <p>We retain your information for as long as your account is active or as needed to provide services, comply with legal obligations, and resolve disputes.</p>

        <h2>6. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
            <li>Access and update your personal information</li>
            <li>Request deletion of your data</li>
            <li>Object to processing of your information</li>
            <li>Data portability where applicable</li>
        </ul>

        <h2>7. Cookies and Tracking</h2>
        <p>We use cookies and similar technologies to enhance user experience, analyze usage patterns, and improve our services.</p>

        <h2>8. Contact Us</h2>
        <p>For privacy-related questions, contact us at privacy@aurastay.com</p>
        """

        privacy, created = PrivacyPolicy.objects.get_or_create(
            is_active=True,
            defaults={
                'title': 'Privacy Policy',
                'content': privacy_content,
                'effective_date': date.today(),
                'version': '1.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Privacy Policy created'))
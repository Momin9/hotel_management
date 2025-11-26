from django.core.management.base import BaseCommand
from django.core import serializers
from accounts.models import *
from tenants.models import SubscriptionPlan
import json

class Command(BaseCommand):
    help = 'Export all website data from local database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Exporting website data from local database...'))

        data = {}

        # Export Footer
        footer = Footer.objects.first()
        if footer:
            data['footer'] = {
                'company_name': footer.company_name,
                'company_description': footer.company_description,
                'email': footer.email,
                'phone': footer.phone,
                'address_line1': footer.address_line1,
                'address_line2': footer.address_line2,
                'twitter_url': footer.twitter_url,
                'linkedin_url': footer.linkedin_url,
                'instagram_url': footer.instagram_url,
                'facebook_url': footer.facebook_url,
                'copyright_line1': footer.copyright_line1,
                'copyright_line2': footer.copyright_line2,
            }

        # Export About Us
        about = AboutUs.objects.first()
        if about:
            data['about_us'] = {
                'purpose_title': about.purpose_title,
                'purpose_icon': about.purpose_icon,
                'trust_title': about.trust_title,
                'trust_subtitle': about.trust_subtitle,
                'trust_icon': about.trust_icon,
                'mission_statement': about.mission_statement,
                'mission_description': about.mission_description,
                'problem_description': about.problem_description,
                'solution_description': about.solution_description,
                'problem_icon': about.problem_icon,
                'solution_icon': about.solution_icon,
                'mission_icon': about.mission_icon,
                'global_architecture_text': about.global_architecture_text,
                'data_security_text': about.data_security_text,
                'modern_tech_text': about.modern_tech_text,
                'uptime_percentage': about.uptime_percentage,
                'security_monitoring': about.security_monitoring,
                'security_certification': about.security_certification,
                'compliance_standard': about.compliance_standard,
                'support_email': about.support_email,
                'support_phone': about.support_phone,
                'support_hours': about.support_hours,
                'is_active': about.is_active,
            }

        # Export Features
        features = []
        for feature in Feature.objects.filter(is_active=True).order_by('order'):
            features.append({
                'title': feature.title,
                'description': feature.description,
                'icon': feature.icon,
                'color': feature.color,
                'order': feature.order,
                'is_active': feature.is_active,
            })
        data['features'] = features

        # Export Page Contents
        page_contents = []
        for page in PageContent.objects.all():
            page_contents.append({
                'page_name': page.page_name,
                'page_title': page.page_title,
                'page_subtitle': page.page_subtitle,
            })
        data['page_contents'] = page_contents

        # Export Site Configuration
        config = SiteConfiguration.objects.first()
        if config:
            data['site_config'] = {
                'company_name': config.company_name,
                'site_title': config.site_title,
                'site_description': config.site_description,
            }

        # Export Subscription Plans
        plans = []
        for plan in SubscriptionPlan.objects.filter(is_active=True):
            plans.append({
                'name': plan.name,
                'description': plan.description,
                'price_monthly': float(plan.price_monthly),
                'price_yearly': float(plan.price_yearly) if plan.price_yearly else None,
                'is_free_trial': plan.is_free_trial,
                'max_rooms': plan.max_rooms,
                'max_managers': plan.max_managers,
                'max_reports': plan.max_reports,
                'has_advanced_analytics': plan.has_advanced_analytics,
                'has_priority_support': plan.has_priority_support,
                'is_active': plan.is_active,
            })
        data['subscription_plans'] = plans

        # Export Terms and Privacy
        terms = TermsOfService.objects.filter(is_active=True).first()
        if terms:
            data['terms_of_service'] = {
                'title': terms.title,
                'content': terms.content,
                'effective_date': terms.effective_date.isoformat(),
                'version': terms.version,
                'is_active': terms.is_active,
            }

        privacy = PrivacyPolicy.objects.filter(is_active=True).first()
        if privacy:
            data['privacy_policy'] = {
                'title': privacy.title,
                'content': privacy.content,
                'effective_date': privacy.effective_date.isoformat(),
                'version': privacy.version,
                'is_active': privacy.is_active,
            }

        # Save to file
        with open('website_data_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS('✓ Data exported to website_data_export.json'))
        self.stdout.write(self.style.SUCCESS(f'✓ Exported {len(features)} features'))
        self.stdout.write(self.style.SUCCESS(f'✓ Exported {len(page_contents)} page contents'))
        self.stdout.write(self.style.SUCCESS(f'✓ Exported {len(plans)} subscription plans'))